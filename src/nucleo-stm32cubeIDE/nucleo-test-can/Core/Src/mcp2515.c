/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    mcp2515.c
  * @brief   MCP2515 CAN Controller Driver Implementation
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software component is licensed by ST under BSD 3-Clause license.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "mcp2515.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/**
  * @brief  Pull CS pin low (activate)
  */
static inline void MCP2515_CS_Low(GPIO_TypeDef *cs_port, uint16_t cs_pin)
{
    HAL_GPIO_WritePin(cs_port, cs_pin, GPIO_PIN_RESET);
}

/**
  * @brief  Pull CS pin high (deactivate)
  */
static inline void MCP2515_CS_High(GPIO_TypeDef *cs_port, uint16_t cs_pin)
{
    HAL_GPIO_WritePin(cs_port, cs_pin, GPIO_PIN_SET);
}

/* USER CODE END 0 */

/**
  * @brief  Reset MCP2515
  */
HAL_StatusTypeDef MCP2515_Reset(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin)
{
    uint8_t cmd = MCP2515_INST_RESET;
    HAL_StatusTypeDef status;

    MCP2515_CS_Low(cs_port, cs_pin);
    status = HAL_SPI_Transmit(hspi, &cmd, 1, HAL_MAX_DELAY);
    MCP2515_CS_High(cs_port, cs_pin);

    /* Wait for reset to complete */
    HAL_Delay(10);

    return status;
}

/**
  * @brief  Write register to MCP2515
  */
HAL_StatusTypeDef MCP2515_WriteRegister(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, uint8_t reg, uint8_t data)
{
    uint8_t tx_data[3];
    HAL_StatusTypeDef status;

    tx_data[0] = MCP2515_INST_WRITE;
    tx_data[1] = reg;
    tx_data[2] = data;

    MCP2515_CS_Low(cs_port, cs_pin);
    status = HAL_SPI_Transmit(hspi, tx_data, 3, HAL_MAX_DELAY);
    MCP2515_CS_High(cs_port, cs_pin);

    return status;
}

/**
  * @brief  Read register from MCP2515
  */
HAL_StatusTypeDef MCP2515_ReadRegister(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, uint8_t reg, uint8_t *data)
{
    uint8_t tx_data[3];
    HAL_StatusTypeDef status;

    tx_data[0] = MCP2515_INST_READ;
    tx_data[1] = reg;
    tx_data[2] = 0x00;  /* Dummy byte for receive */

    MCP2515_CS_Low(cs_port, cs_pin);
    status = HAL_SPI_TransmitReceive(hspi, tx_data, tx_data, 3, HAL_MAX_DELAY);
    MCP2515_CS_High(cs_port, cs_pin);

    if (status == HAL_OK) {
        *data = tx_data[2];  /* Received data is in third byte */
    }

    return status;
}

/**
  * @brief  Set CAN bitrate to 1 Mbps
  */
HAL_StatusTypeDef MCP2515_SetBitrate(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin)
{
    HAL_StatusTypeDef status;

    /* Configure CNF1, CNF2, CNF3 for 1 Mbps with 8 MHz crystal */
    /* BRP = 3: TQ = 2 * (3 + 1) / 8 MHz = 1 us */
    /* TSEG1 = 4, TSEG2 = 1: Total = 8 TQ per bit */
    status = MCP2515_WriteRegister(hspi, cs_port, cs_pin, MCP2515_REG_CNF1, MCP2515_CNF1_1MBPS);
    if (status != HAL_OK) return status;

    status = MCP2515_WriteRegister(hspi, cs_port, cs_pin, MCP2515_REG_CNF2, MCP2515_CNF2_1MBPS);
    if (status != HAL_OK) return status;

    status = MCP2515_WriteRegister(hspi, cs_port, cs_pin, MCP2515_REG_CNF3, MCP2515_CNF3_1MBPS);
    if (status != HAL_OK) return status;

    return HAL_OK;
}

/**
  * @brief  Set MCP2515 to normal operation mode
  */
HAL_StatusTypeDef MCP2515_SetNormalMode(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin)
{
    return MCP2515_WriteRegister(hspi, cs_port, cs_pin, MCP2515_REG_CANCTRL, MCP2515_MODE_NORMAL);
}

/**
  * @brief  Send CAN message via MCP2515
  */
HAL_StatusTypeDef MCP2515_SendMessage(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, MCP2515_CanMessage_t *msg)
{
    uint8_t tx_buffer[14];
    uint8_t i;
    HAL_StatusTypeDef status;

    /* Check if TX buffer 0 is available */
    uint8_t txb0ctrl;
    MCP2515_ReadRegister(hspi, cs_port, cs_pin, MCP2515_REG_TXB0CTRL, &txb0ctrl);
    if (txb0ctrl & MCP2515_TXB_TXREQ) {
        /* TX buffer is still busy */
        return HAL_BUSY;
    }

    /* Prepare TX buffer data */
    tx_buffer[0] = MCP2515_INST_WRITE;
    tx_buffer[1] = MCP2515_REG_TXB0SIDH;
    
    /* CAN ID (11-bit standard) */
    tx_buffer[2] = (uint8_t)((msg->id >> 3) & 0xFF);  /* SIDH: bits 10-3 */
    tx_buffer[3] = (uint8_t)((msg->id << 5) & 0xE0);  /* SIDL: bits 2-0 in upper 3 bits */
    
    /* DLC (Data Length Code) */
    tx_buffer[4] = msg->dlc & 0x0F;  /* DLC: 4 bits, max 8 */
    
    /* Data bytes */
    for (i = 0; i < 8; i++) {
        tx_buffer[5 + i] = (i < msg->dlc) ? msg->data[i] : 0x00;
    }

    /* Write to TX buffer */
    MCP2515_CS_Low(cs_port, cs_pin);
    status = HAL_SPI_Transmit(hspi, tx_buffer, 13, HAL_MAX_DELAY);
    MCP2515_CS_High(cs_port, cs_pin);

    if (status != HAL_OK) {
        return status;
    }

    /* Request transmission */
    tx_buffer[0] = MCP2515_INST_RTS;
    tx_buffer[1] = 0x01;  /* RTS TXB0 */

    MCP2515_CS_Low(cs_port, cs_pin);
    status = HAL_SPI_Transmit(hspi, tx_buffer, 2, HAL_MAX_DELAY);
    MCP2515_CS_High(cs_port, cs_pin);

    return status;
}

/**
  * @brief  Initialize MCP2515 CAN controller
  */
HAL_StatusTypeDef MCP2515_Init(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin)
{
    HAL_StatusTypeDef status;
    uint8_t read_val;

    /* Ensure CS pin is high initially */
    MCP2515_CS_High(cs_port, cs_pin);
    HAL_Delay(10);

    /* Reset MCP2515 */
    status = MCP2515_Reset(hspi, cs_port, cs_pin);
    if (status != HAL_OK) {
        return status;
    }

    /* Set configuration mode */
    status = MCP2515_WriteRegister(hspi, cs_port, cs_pin, MCP2515_REG_CANCTRL, MCP2515_MODE_CONFIG);
    if (status != HAL_OK) {
        return status;
    }

    /* Verify we're in config mode */
    HAL_Delay(10);
    MCP2515_ReadRegister(hspi, cs_port, cs_pin, MCP2515_REG_CANCTRL, &read_val);
    if ((read_val & 0xE0) != MCP2515_MODE_CONFIG) {
        return HAL_ERROR;
    }

    /* Configure bitrate to 1 Mbps */
    status = MCP2515_SetBitrate(hspi, cs_port, cs_pin);
    if (status != HAL_OK) {
        return status;
    }

    /* Disable interrupts (not needed for basic TX) */
    MCP2515_WriteRegister(hspi, cs_port, cs_pin, MCP2515_REG_CANINTE, 0x00);

    /* Set to normal mode */
    status = MCP2515_SetNormalMode(hspi, cs_port, cs_pin);
    if (status != HAL_OK) {
        return status;
    }

    /* Verify we're in normal mode */
    HAL_Delay(10);
    MCP2515_ReadRegister(hspi, cs_port, cs_pin, MCP2515_REG_CANCTRL, &read_val);
    if ((read_val & 0xE0) != MCP2515_MODE_NORMAL) {
        return HAL_ERROR;
    }

    return HAL_OK;
}

/* USER CODE BEGIN 1 */

/* USER CODE END 1 */

