/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    mcp2515.h
  * @brief   MCP2515 CAN Controller Driver Header
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

#ifndef __MCP2515_H
#define __MCP2515_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stm32g4xx_hal.h"

/* Exported types ------------------------------------------------------------*/

/* MCP2515 CAN message structure */
typedef struct {
    uint32_t id;        /* CAN identifier (11-bit standard) */
    uint8_t dlc;        /* Data length code (0-8) */
    uint8_t data[8];    /* Data bytes */
} MCP2515_CanMessage_t;

/* Exported constants --------------------------------------------------------*/

/* MCP2515 Instruction Set */
#define MCP2515_INST_RESET           0xC0
#define MCP2515_INST_READ            0x03
#define MCP2515_INST_WRITE            0x02
#define MCP2515_INST_READ_STATUS      0xA0
#define MCP2515_INST_RTS              0x80
#define MCP2515_INST_BIT_MODIFY       0x05

/* MCP2515 Registers */
#define MCP2515_REG_CANCTRL          0x0F
#define MCP2515_REG_CNF1             0x2A
#define MCP2515_REG_CNF2             0x29
#define MCP2515_REG_CNF3             0x28
#define MCP2515_REG_CANINTF          0x2C
#define MCP2515_REG_CANINTE          0x2B
#define MCP2515_REG_TXB0CTRL          0x30
#define MCP2515_REG_TXB0SIDH         0x31
#define MCP2515_REG_TXB0SIDL         0x32
#define MCP2515_REG_TXB0DLC          0x35
#define MCP2515_REG_TXB0D0           0x36
#define MCP2515_REG_RXB0CTRL          0x60
#define MCP2515_REG_RXB0SIDH         0x61
#define MCP2515_REG_RXB0SIDL         0x62
#define MCP2515_REG_RXB0DLC          0x65
#define MCP2515_REG_RXB0D0           0x66

/* CANCTRL Register Bits */
#define MCP2515_MODE_NORMAL          0x00
#define MCP2515_MODE_SLEEP           0x20
#define MCP2515_MODE_LOOPBACK        0x40
#define MCP2515_MODE_LISTENONLY       0x60
#define MCP2515_MODE_CONFIG           0x80

/* TXB0CTRL Register Bits */
#define MCP2515_TXB_TXREQ            0x08
#define MCP2515_TXB_ABTF             0x40

/* CANINTF Register Bits */
#define MCP2515_INT_TX0IF            0x04
#define MCP2515_INT_RX0IF            0x01
#define MCP2515_INT_RX1IF            0x02

/* Bitrate Configuration for 1 Mbps (8 MHz crystal) */
/* Time Quanta = 2 * (BRP + 1) / FOSC */
/* For 1 Mbps with 8 MHz: TQ = 1/1000000 = 1 us */
/* TQ = 2 * (BRP + 1) / 8000000 => BRP = 3 */
/* Sample Point at 75%: TSEG1 = 4, TSEG2 = 1, Total = 8 TQ */
#define MCP2515_CNF1_1MBPS            ((3 << 0))  /* BRP = 3 */
#define MCP2515_CNF2_1MBPS            ((1 << 6) | (4 << 3) | (1 << 0))  /* BTLMODE, TSEG1=4, SAM=1 */
#define MCP2515_CNF3_1MBPS            ((1 << 0))  /* TSEG2=1 */

/* Exported macro ------------------------------------------------------------*/

/* Exported functions prototypes ---------------------------------------------*/

/**
  * @brief  Initialize MCP2515 CAN controller
  * @param  hspi: SPI handle pointer
  * @param  cs_port: GPIO port for chip select
  * @param  cs_pin: GPIO pin for chip select
  * @retval HAL_StatusTypeDef: HAL_OK if successful, HAL_ERROR otherwise
  */
HAL_StatusTypeDef MCP2515_Init(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin);

/**
  * @brief  Reset MCP2515
  * @param  hspi: SPI handle pointer
  * @param  cs_port: GPIO port for chip select
  * @param  cs_pin: GPIO pin for chip select
  * @retval HAL_StatusTypeDef: HAL_OK if successful
  */
HAL_StatusTypeDef MCP2515_Reset(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin);

/**
  * @brief  Write register to MCP2515
  * @param  hspi: SPI handle pointer
  * @param  cs_port: GPIO port for chip select
  * @param  cs_pin: GPIO pin for chip select
  * @param  reg: Register address
  * @param  data: Data to write
  * @retval HAL_StatusTypeDef: HAL_OK if successful
  */
HAL_StatusTypeDef MCP2515_WriteRegister(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, uint8_t reg, uint8_t data);

/**
  * @brief  Read register from MCP2515
  * @param  hspi: SPI handle pointer
  * @param  cs_port: GPIO port for chip select
  * @param  cs_pin: GPIO pin for chip select
  * @param  reg: Register address
  * @param  data: Pointer to store read data
  * @retval HAL_StatusTypeDef: HAL_OK if successful
  */
HAL_StatusTypeDef MCP2515_ReadRegister(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, uint8_t reg, uint8_t *data);

/**
  * @brief  Set CAN bitrate to 1 Mbps
  * @param  hspi: SPI handle pointer
  * @param  cs_port: GPIO port for chip select
  * @param  cs_pin: GPIO pin for chip select
  * @retval HAL_StatusTypeDef: HAL_OK if successful
  */
HAL_StatusTypeDef MCP2515_SetBitrate(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin);

/**
  * @brief  Set MCP2515 to normal operation mode
  * @param  hspi: SPI handle pointer
  * @param  cs_port: GPIO port for chip select
  * @param  cs_pin: GPIO pin for chip select
  * @retval HAL_StatusTypeDef: HAL_OK if successful
  */
HAL_StatusTypeDef MCP2515_SetNormalMode(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin);

/**
  * @brief  Send CAN message via MCP2515
  * @param  hspi: SPI handle pointer
  * @param  cs_port: GPIO port for chip select
  * @param  cs_pin: GPIO pin for chip select
  * @param  msg: Pointer to CAN message structure
  * @retval HAL_StatusTypeDef: HAL_OK if successful
  */
HAL_StatusTypeDef MCP2515_SendMessage(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, MCP2515_CanMessage_t *msg);

/**
  * @brief  Check if CAN message is available and receive it
  * @param  hspi: SPI handle pointer
  * @param  cs_port: GPIO port for chip select
  * @param  cs_pin: GPIO pin for chip select
  * @param  msg: Pointer to CAN message structure to store received message
  * @retval HAL_StatusTypeDef: HAL_OK if message received, HAL_ERROR if no message
  */
HAL_StatusTypeDef MCP2515_ReceiveMessage(SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, MCP2515_CanMessage_t *msg);

#ifdef __cplusplus
}
#endif

#endif /* __MCP2515_H */

