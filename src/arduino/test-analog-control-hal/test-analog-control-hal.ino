/* -------------------------------------------------------------------------- */
/* FILE NAME:   test-analog-control-hal.ino
   DESCRIPTION: TRUE hardware-timed control loop using STM32 HAL
                This version uses:
                - Timer-triggered ADC with DMA (single channel A0)
                - Timer-triggered DAC output
                - All synchronized to TIM6 for precise timing
                - CIRCULAR DMA mode with proper stop mechanism
                
   HARDWARE:    Arduino Giga R1 WiFi (STM32H747)
                - ADC channel: A0 (PA0) → ADC1 Channel 0
                - DAC output: A12 (PA4) → DAC1 Channel 1
                
   SAMPLE_RATE: Adjustable, true hardware timing with zero jitter
   
   NOTE:        Simplified to single channel for initial testing.
                CIRCULAR DMA mode allows future expansion to continuous
                control loop operation.
/* -------------------------------------------------------------------------- */

// Note: mbed.h removed to avoid conflicts with direct HAL usage
#include "stm32h7xx_hal.h"

// ============================================================================
// Configuration
// ============================================================================

#define SERIAL_BAUD 115200
#define SAMPLE_RATE 2000        // Hz - true hardware rate, no jitter
#define DURATION_SEC 0.1
#define TOTAL_SAMPLES ((uint32_t)(SAMPLE_RATE * DURATION_SEC))
#define NUM_ADC_CHANNELS 1      // Single channel (A0) for now

// ============================================================================
// Global Variables
// ============================================================================

// HAL handles
TIM_HandleTypeDef htim6;        // Timer for ADC/DAC triggering
ADC_HandleTypeDef hadc1;        // ADC1 for single-channel acquisition (A0)
DAC_HandleTypeDef hdac1;        // DAC1 for output
DMA_HandleTypeDef hdma_adc1;    // DMA for ADC data transfer

// ADC buffer - DMA writes here automatically
// Note: Using 16-bit values (0-65535 for 16-bit ADC resolution)
uint16_t adc_buffer[NUM_ADC_CHANNELS];

// Data storage
float output_voltage_buffer[TOTAL_SAMPLES];
float input_voltage_buffer[TOTAL_SAMPLES];  // Single channel

// State
volatile uint32_t sample_index = 0;
volatile bool acquisition_complete = false;
volatile bool control_loop_active = false;

// ============================================================================
// HAL MSP Callbacks - Required for proper HAL initialization
// ============================================================================

/**
 * ADC MSP Initialization callback
 * Called by HAL_ADC_Init() to perform low-level peripheral initialization
 */
void HAL_ADC_MspInit(ADC_HandleTypeDef* hadc) {
  if(hadc->Instance == ADC1) {
    // Enable ADC1 clock (if not already enabled)
    __HAL_RCC_ADC12_CLK_ENABLE();
    
    // GPIO clock should already be enabled, but ensure it's on
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    Serial.println("HAL_ADC_MspInit called for ADC1");
  }
}

/**
 * ADC MSP De-Initialization callback
 */
void HAL_ADC_MspDeInit(ADC_HandleTypeDef* hadc) {
  if(hadc->Instance == ADC1) {
    // Disable ADC1 clock
    __HAL_RCC_ADC12_CLK_DISABLE();
  }
}

// ============================================================================
// Hardware Configuration Functions
// ============================================================================

/**
 * Initialize TIM6 as trigger source for ADC and DAC
 * TIM6 generates TRGO events at SAMPLE_RATE Hz
 */
void HAL_TIM6_Init(uint32_t sample_rate) {
  // Enable TIM6 clock
  __HAL_RCC_TIM6_CLK_ENABLE();
  
  // TIM6 configuration
  // Timer clock = 240 MHz (typical for STM32H7)
  // We want to generate update events at sample_rate Hz
  // Timer frequency = Timer_clock / (Prescaler * Period)
  
  uint32_t timer_clock = 240000000;  // 240 MHz
  uint32_t prescaler = 240 - 1;       // Divide by 240 -> 1 MHz
  uint32_t period = (1000000 / sample_rate) - 1;  // Period for desired rate
  
  htim6.Instance = TIM6;
  htim6.Init.Prescaler = prescaler;
  htim6.Init.Period = period;
  htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim6.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim6.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  
  if (HAL_TIM_Base_Init(&htim6) != HAL_OK) {
    Serial.println("ERROR: TIM6 init failed!");
    return;
  }
  
  // Configure TIM6 to generate TRGO on update event
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  
  if (HAL_TIMEx_MasterConfigSynchronization(&htim6, &sMasterConfig) != HAL_OK) {
    Serial.println("ERROR: TIM6 master config failed!");
    return;
  }
  
  Serial.println("TIM6 initialized successfully");
}

/**
 * Initialize DMA for ADC1
 * DMA automatically transfers ADC results to memory
 */
void HAL_DMA_ADC1_Init() {
  // Enable DMA1 clock
  __HAL_RCC_DMA1_CLK_ENABLE();
  
  // DMA configuration for ADC1
  // ADC1 uses DMA1 Stream 0 or DMA1 Stream 1
  hdma_adc1.Instance = DMA1_Stream0;
  hdma_adc1.Init.Request = DMA_REQUEST_ADC1;
  hdma_adc1.Init.Direction = DMA_PERIPH_TO_MEMORY;
  hdma_adc1.Init.PeriphInc = DMA_PINC_DISABLE;
  hdma_adc1.Init.MemInc = DMA_MINC_ENABLE;
  hdma_adc1.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;  // 16-bit
  hdma_adc1.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;     // 16-bit
  hdma_adc1.Init.Mode = DMA_CIRCULAR;
  hdma_adc1.Init.Priority = DMA_PRIORITY_HIGH;
  hdma_adc1.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
  
  if (HAL_DMA_Init(&hdma_adc1) != HAL_OK) {
    Serial.println("ERROR: DMA init failed!");
    return;
  }
  
  // Link DMA to ADC
  __HAL_LINKDMA(&hadc1, DMA_Handle, hdma_adc1);
  
  // Enable DMA interrupt
  HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Stream0_IRQn);
  
  Serial.println("DMA initialized successfully");
}

/**
 * Configure GPIO pin for ADC (A0 = PA0)
 */
void HAL_GPIO_ADC_Init() {
  // Enable GPIOA clock
  __HAL_RCC_GPIOA_CLK_ENABLE();
  
  // Configure PA0 (A0) as analog input
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_PIN_0;
  GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  
  Serial.println("GPIO configured for A0 (PA0)");
}

/**
 * Initialize ADC1 with single channel (A0) and timer trigger
 */
void HAL_ADC1_Init() {
  // Configure GPIO first
  HAL_GPIO_ADC_Init();
  
  // Enable ADC1 clock
  __HAL_RCC_ADC12_CLK_ENABLE();
  
  // =========================================================================
  // IMPORTANT: On STM32H7, must exit deep power down and enable voltage
  // regulator BEFORE HAL_ADC_Init
  // =========================================================================
  
  // Debug: Print initial ADC CR register state
  Serial.print("ADC CR before config: 0x");
  Serial.println(ADC1->CR, HEX);
  
  // Exit deep power down mode (clear DEEPPWD bit)
  ADC1->CR &= ~ADC_CR_DEEPPWD;
  Serial.println("Exited ADC deep power down mode");
  
  // Enable ADC voltage regulator (set ADVREGEN bit)
  ADC1->CR |= ADC_CR_ADVREGEN;
  Serial.println("ADC voltage regulator enabled");
  
  // Wait for voltage regulator to stabilize (at least 10µs, use 20ms to be safe)
  delay(20);
  
  // Debug: Print ADC CR register after voltage regulator enable
  Serial.print("ADC CR after ADVREGEN: 0x");
  Serial.println(ADC1->CR, HEX);
  
  // Set ADC instance BEFORE DMA init (needed for __HAL_LINKDMA)
  hadc1.Instance = ADC1;
  
  // =========================================================================
  // IMPORTANT: Initialize DMA BEFORE HAL_ADC_Init
  // This ensures proper DMA linkage when ADC is initialized
  // =========================================================================
  HAL_DMA_ADC1_Init();
  
  // ADC1 configuration
  hadc1.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV4;
  hadc1.Init.Resolution = ADC_RESOLUTION_16B;  // 16-bit resolution
  hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;  // Single channel, no scan
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc1.Init.LowPowerAutoWait = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;     // Triggered by timer
  hadc1.Init.NbrOfConversion = 1;              // Single conversion
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_EXTERNALTRIG_T6_TRGO;  // TIM6 trigger
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
  hadc1.Init.ConversionDataManagement = ADC_CONVERSIONDATA_DMA_CIRCULAR;
  hadc1.Init.Overrun = ADC_OVR_DATA_OVERWRITTEN;
  hadc1.Init.LeftBitShift = ADC_LEFTBITSHIFT_NONE;
  hadc1.Init.OversamplingMode = DISABLE;
  
  // NOW initialize ADC (after DMA is already linked)
  if (HAL_ADC_Init(&hadc1) != HAL_OK) {
    Serial.println("ERROR: ADC1 init failed!");
    return;
  }
  Serial.println("ADC1 HAL_ADC_Init successful");
  
  // Check if ADC is ready (ADRDY flag) after HAL_ADC_Init
  // This is the correct time to check - after initialization
  uint32_t timeout = 1000; // 1 second timeout
  uint32_t start_time = millis();
  bool adrdy_set = false;
  
  while ((millis() - start_time < timeout)) {
    if (ADC1->ISR & ADC_ISR_ADRDY) {
      Serial.println("ADC ready (ADRDY flag set after HAL_ADC_Init)");
      // Clear ADRDY flag by writing 1 to it
      ADC1->ISR |= ADC_ISR_ADRDY;
      adrdy_set = true;
      break;
    }
    delay(1);
  }
  
  if (!adrdy_set) {
    Serial.println("WARNING: ADRDY flag not set after HAL_ADC_Init!");
    Serial.println("Attempting manual ADC enable sequence...");
    
    // Manual enable sequence: Set ADEN bit and wait for ADRDY
    // First, ensure ADC is disabled
    if (ADC1->CR & ADC_CR_ADEN) {
      ADC1->CR |= ADC_CR_ADDIS;  // Request ADC disable
      delay(10);
      while (ADC1->CR & ADC_CR_ADEN) {
        delay(1);
      }
    }
    
    // Clear ADRDY flag if it was set
    ADC1->ISR |= ADC_ISR_ADRDY;
    
    // Now enable ADC
    ADC1->CR |= ADC_CR_ADEN;
    Serial.println("ADEN bit set manually");
    
    // Wait for ADRDY
    start_time = millis();
    while ((millis() - start_time < timeout)) {
      if (ADC1->ISR & ADC_ISR_ADRDY) {
        Serial.println("ADC ready after manual enable (ADRDY flag set)");
        ADC1->ISR |= ADC_ISR_ADRDY;  // Clear flag
        adrdy_set = true;
        break;
      }
      delay(1);
    }
    
    if (!adrdy_set) {
      Serial.println("ERROR: ADC still not ready after manual enable!");
      Serial.println("This may indicate a hardware or clock configuration issue.");
    }
  }
  
  // Configure ADC channel: A0 → ADC1 Channel 0 (PA0)
  ADC_ChannelConfTypeDef sConfig = {0};
  sConfig.Channel = ADC_CHANNEL_0;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_8CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK) {
    Serial.println("ERROR: ADC Channel 0 config failed!");
    return;
  }
  
  // Debug: Print ADC state
  Serial.print("ADC State after init: ");
  Serial.println(hadc1.State);
  
  Serial.println("ADC1 initialized successfully (A0, Channel 0)");
}

/**
 * Initialize DAC1 with timer trigger
 * DAC output synchronized to same timer as ADC
 */
void HAL_DAC1_Init() {
  // Enable DAC1 clock
  __HAL_RCC_DAC12_CLK_ENABLE();
  
  // DAC configuration
  hdac1.Instance = DAC1;
  
  if (HAL_DAC_Init(&hdac1) != HAL_OK) {
    Serial.println("ERROR: DAC init failed!");
    return;
  }
  
  // Configure DAC channel 1 (PA4 - A12 on Giga)
  DAC_ChannelConfTypeDef sConfig = {0};
  sConfig.DAC_SampleAndHold = DAC_SAMPLEANDHOLD_DISABLE;
  sConfig.DAC_Trigger = DAC_TRIGGER_T6_TRGO;  // TIM6 trigger
  sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
  sConfig.DAC_ConnectOnChipPeripheral = DAC_CHIPCONNECT_DISABLE;
  sConfig.DAC_UserTrimming = DAC_TRIMMING_FACTORY;
  
  if (HAL_DAC_ConfigChannel(&hdac1, &sConfig, DAC_CHANNEL_1) != HAL_OK) {
    Serial.println("ERROR: DAC config failed!");
    return;
  }
  
  Serial.println("DAC1 initialized successfully");
}

// ============================================================================
// DMA Callback - Called when ADC conversion completes (CIRCULAR mode)
// ============================================================================

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {
  // Debug: Callback called
  static uint32_t callback_count = 0;
  callback_count++;
  
  if (callback_count <= 5 || callback_count % 50 == 0) {
    // Print first 5 callbacks and then every 50th
    Serial.print("Callback #");
    Serial.print(callback_count);
    Serial.print(" - Sample index: ");
    Serial.println(sample_index);
  }
  
  if (!control_loop_active || acquisition_complete) {
    return;
  }
  
  // Check if we've collected enough samples
  if (sample_index >= TOTAL_SAMPLES) {
    acquisition_complete = true;
    Serial.println("Acquisition complete in callback!");
    // Stop timer, ADC, and DAC
    HAL_TIM_Base_Stop(&htim6);
    HAL_ADC_Stop_DMA(&hadc1);
    HAL_DAC_Stop(&hdac1, DAC_CHANNEL_1);
    return;
  }
  
  // DMA has already transferred ADC value to adc_buffer[0]
  // Save ADC value (convert to voltage)
  // For 16-bit ADC: 0-65535 represents 0-3.3V
  input_voltage_buffer[sample_index] = (adc_buffer[0] * 3.3f) / 65535.0f;
  
  // Calculate output voltage (sine wave)
  float frequency = (float)SAMPLE_RATE / 20.0f;
  float time = (float)sample_index / (float)SAMPLE_RATE;
  float output_voltage = 1.65f + 1.65f * sin(2.0f * PI * frequency * time);
  output_voltage_buffer[sample_index] = output_voltage;
  
  // Update DAC value BEFORE next timer trigger
  // Convert voltage (0-3.3V) to 12-bit DAC value (0-4095)
  uint32_t dac_value = (uint32_t)((output_voltage / 3.3f) * 4095.0f);
  if (dac_value > 4095) dac_value = 4095;
  
  // Set DAC value - timer will trigger output on next cycle
  HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, dac_value);
  
  // Increment sample index
  sample_index++;
  
  // Check again if complete (after increment)
  if (sample_index >= TOTAL_SAMPLES) {
    acquisition_complete = true;
    // Stop timer, ADC, and DAC
    HAL_TIM_Base_Stop(&htim6);
    HAL_ADC_Stop_DMA(&hadc1);
    HAL_DAC_Stop(&hdac1, DAC_CHANNEL_1);
  }
}

// ============================================================================
// DMA Interrupt Handler - Required for HAL callbacks
// ============================================================================

extern "C" void DMA1_Stream0_IRQHandler(void) {
  HAL_DMA_IRQHandler(&hdma_adc1);
}

// ============================================================================
// Setup
// ============================================================================

void setup() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial && millis() < 5000) {
    delay(10);
  }
  
  Serial.println("========================================");
  Serial.println("STM32 HAL Hardware-Timed Control Loop");
  Serial.println("========================================");
  Serial.println("TRUE hardware timing with DMA (Single Channel)");
  Serial.print("Sample Rate: ");
  Serial.print(SAMPLE_RATE);
  Serial.println(" Hz");
  Serial.print("Total Samples: ");
  Serial.println(TOTAL_SAMPLES);
  Serial.println();
  
  Serial.println("Initializing HAL...");
  
  // Initialize HAL library (required for HAL to work)
  if (HAL_Init() != HAL_OK) {
    Serial.println("ERROR: HAL_Init failed!");
    while(1) delay(1000);
  }
  Serial.println("HAL initialized");
  
  Serial.println("Initializing hardware...");
  
  // Initialize hardware in order
  HAL_TIM6_Init(SAMPLE_RATE);
  HAL_ADC1_Init();
  HAL_DAC1_Init();
  
  Serial.println("\nHardware initialization complete!");
  Serial.println("Single channel ADC (A0) configured on ADC1 Channel 0");
  Serial.println("Send 'c' to start acquisition.");
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // Handle commands
  if (Serial.available() > 0) {
    char command = Serial.read();
    while (Serial.available() > 0) Serial.read();
    
    if ((command == 'c' || command == 'C') && !control_loop_active) {
      Serial.println("\nStarting hardware-timed acquisition...");
      
      // Reset state
      sample_index = 0;
      acquisition_complete = false;
      control_loop_active = true;
      
      // Set initial DAC value (before starting)
      float initial_voltage = 1.65f;  // Start at midpoint
      uint32_t dac_value = (uint32_t)((initial_voltage / 3.3f) * 4095.0f);
      HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, dac_value);
      
      // Start DAC (with timer trigger)
      HAL_DAC_Start(&hdac1, DAC_CHANNEL_1);
      
      // Debug: Check ADC and DMA state before starting
      Serial.print("ADC State before start: ");
      Serial.println(hadc1.State);
      Serial.print("DMA State: ");
      Serial.println(hdma_adc1.State);
      
      // Debug: Print ADC registers before starting
      Serial.print("ADC CR register: 0x");
      Serial.println(hadc1.Instance->CR, HEX);
      Serial.print("ADC ISR register: 0x");
      Serial.println(hadc1.Instance->ISR, HEX);
      Serial.print("ADC CFGR register: 0x");
      Serial.println(hadc1.Instance->CFGR, HEX);
      
      // IMPORTANT: Start timer BEFORE starting ADC DMA
      // The timer must be running to generate triggers for the ADC
      Serial.println("Starting timer...");
      HAL_TIM_Base_Start(&htim6);
      
      // Verify timer is running
      if (__HAL_TIM_IS_TIM_COUNTING_DOWN(&htim6)) {
        Serial.println("Timer is running (counting down)");
      } else if (htim6.Instance->CR1 & TIM_CR1_CEN) {
        Serial.println("Timer is running (CEN bit set)");
      } else {
        Serial.println("WARNING: Timer may not be running!");
      }
      
      // Small delay to let timer start
      delay(10);
      
      // Start ADC with DMA (buffer size = 1 for single channel)
      Serial.println("Starting ADC DMA...");
      HAL_StatusTypeDef status = HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, NUM_ADC_CHANNELS);
      Serial.print("HAL_ADC_Start_DMA returned: ");
      Serial.println(status);
      Serial.print("HAL_OK = ");
      Serial.println(HAL_OK);
      Serial.print("HAL_ERROR = ");
      Serial.println(HAL_ERROR);
      
      // Debug: Print ADC registers after attempting start
      Serial.print("ADC CR after start attempt: 0x");
      Serial.println(hadc1.Instance->CR, HEX);
      Serial.print("ADC ISR after start attempt: 0x");
      Serial.println(hadc1.Instance->ISR, HEX);
      
      if (status != HAL_OK) {
        Serial.println("ERROR: Failed to start ADC DMA!");
        
        // Diagnostic: Check ADC error code
        Serial.print("ADC Error Code: 0x");
        Serial.println(hadc1.ErrorCode, HEX);
        
        // Diagnostic: Check if ADRDY flag is set
        if (hadc1.Instance->ISR & ADC_ISR_ADRDY) {
          Serial.println("ADRDY flag is SET (ADC is ready)");
        } else {
          Serial.println("ADRDY flag is NOT SET (ADC not ready)");
        }
        
        // Diagnostic: Check ADC clock status
        if (__HAL_RCC_ADC12_IS_CLK_ENABLED()) {
          Serial.println("ADC12 clock is ENABLED");
        } else {
          Serial.println("ERROR: ADC12 clock is NOT ENABLED!");
        }
        
        // Diagnostic: Check if ADEN bit is set
        if (hadc1.Instance->CR & ADC_CR_ADEN) {
          Serial.println("ADEN bit is SET (ADC enable attempted)");
        } else {
          Serial.println("ADEN bit is NOT SET");
        }
        
        // Diagnostic: Check voltage regulator status
        if (hadc1.Instance->CR & ADC_CR_ADVREGEN) {
          Serial.println("ADVREGEN bit is SET (voltage regulator enabled)");
        } else {
          Serial.println("ERROR: ADVREGEN bit is NOT SET!");
        }
        
        // Diagnostic: Check deep power down status
        if (hadc1.Instance->CR & ADC_CR_DEEPPWD) {
          Serial.println("ERROR: DEEPPWD bit is SET (still in deep power down)!");
        } else {
          Serial.println("DEEPPWD bit is CLEAR (not in deep power down)");
        }
        
        control_loop_active = false;
        return;
      }
      
      Serial.println("Acquisition running...");
      Serial.print("Collecting ");
      Serial.print(TOTAL_SAMPLES);
      Serial.println(" samples...");
      Serial.println("Waiting for DMA callbacks...");
    }
  }
  
  // Periodic status output while acquisition is running
  if (control_loop_active && !acquisition_complete) {
    static unsigned long last_status = 0;
    unsigned long now = millis();
    
    // Print status every 500ms
    if (now - last_status > 500) {
      last_status = now;
      Serial.print("Status: sample_index=");
      Serial.print(sample_index);
      Serial.print("/");
      Serial.print(TOTAL_SAMPLES);
      Serial.print(", timer running=");
      Serial.print(htim6.Instance->CR1 & TIM_CR1_CEN ? "YES" : "NO");
      Serial.print(", ADC enabled=");
      Serial.print(hadc1.Instance->CR & ADC_CR_ADEN ? "YES" : "NO");
      Serial.println();
    }
  }
  
  // Check if complete (callback may have already stopped hardware)
  if (acquisition_complete && control_loop_active) {
    // Ensure everything is stopped (in case callback didn't stop it)
    HAL_TIM_Base_Stop(&htim6);
    HAL_ADC_Stop_DMA(&hadc1);
    HAL_DAC_Stop(&hdac1, DAC_CHANNEL_1);
    control_loop_active = false;
    
    Serial.println("\nAcquisition complete!");
    Serial.print("Samples collected: ");
    Serial.println(sample_index);
    Serial.println("Printing data...\n");
    
    // Print header
    Serial.println("time,output_voltage,input_A0");
    
    // Print data
    float time_step = 1.0f / SAMPLE_RATE;
    for (uint32_t i = 0; i < sample_index; i++) {
      Serial.print(i * time_step, 4);
      Serial.print(",");
      Serial.print(output_voltage_buffer[i], 4);
      Serial.print(",");
      Serial.println(input_voltage_buffer[i], 4);
    }
    
    Serial.println("\nSend 'c' for new acquisition.");
  }
  
  delay(10);
}
