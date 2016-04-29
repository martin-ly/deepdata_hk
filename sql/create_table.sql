/*
Navicat SQL Server Data Transfer

Source Server         : 192.168.0.232
Source Server Version : 105000
Source Host           : 192.168.0.232:1433
Source Database       : StockData
Source Schema         : dbo

Target Server Type    : SQL Server
Target Server Version : 105000
File Encoding         : 65001

Date: 2016-04-29 14:14:29
*/


-- ----------------------------
-- Table structure for DeepMarketShortSelling
-- ----------------------------
DROP TABLE [dbo].[DeepMarketShortSelling]
GO
CREATE TABLE [dbo].[DeepMarketShortSelling] (
[issuerdate] date NOT NULL ,
[timesign] int NOT NULL ,
[currency] char(3) NOT NULL ,
[totalShare] int NOT NULL ,
[totalTurnover] float(53) NOT NULL ,
[constituentTurnover] float(53) NOT NULL ,
[marketTurnover] float(53) NOT NULL 
)


GO

-- ----------------------------
-- Table structure for DeepSecurityHolder
-- ----------------------------
DROP TABLE [dbo].[DeepSecurityHolder]
GO
CREATE TABLE [dbo].[DeepSecurityHolder] (
[changedate] date NOT NULL ,
[securityid] varchar(10) NOT NULL ,
[stockcode] varchar(10) NOT NULL ,
[holdqty] bigint NOT NULL ,
[holdqtyper] float(53) NULL ,
[daychgqty] bigint NULL ,
[daychgper] float(53) NULL ,
[wekchgqty] bigint NULL ,
[wekchgper] float(53) NULL ,
[monchgqty] bigint NULL ,
[monchgper] float(53) NULL 
)


GO

-- ----------------------------
-- Table structure for DeepStockHolder
-- ----------------------------
DROP TABLE [dbo].[DeepStockHolder]
GO
CREATE TABLE [dbo].[DeepStockHolder] (
[changedate] date NOT NULL ,
[ename] nvarchar(255) NULL ,
[tname] nvarchar(255) NOT NULL ,
[sname] nvarchar(255) NOT NULL ,
[capicity] char(1) NULL ,
[eventcode] varchar(20) NOT NULL ,
[stockcode] varchar(10) NOT NULL ,
[avgprice] float(53) NOT NULL ,
[classofshares] nvarchar(255) NOT NULL ,
[changeQtyL] bigint NOT NULL ,
[holdQtyL] bigint NOT NULL ,
[issuerPerL] float(53) NOT NULL ,
[changePerL] float(53) NOT NULL ,
[changeQtyS] bigint NOT NULL ,
[holdQtyS] bigint NOT NULL ,
[issuerPerS] float(53) NOT NULL ,
[changePerS] float(53) NOT NULL ,
[changeQtyP] bigint NOT NULL ,
[holdQtyP] bigint NOT NULL ,
[issuerPerP] float(53) NOT NULL ,
[changePerP] float(53) NOT NULL 
)


GO

-- ----------------------------
-- Table structure for DeepStockShortSelling
-- ----------------------------
DROP TABLE [dbo].[DeepStockShortSelling]
GO
CREATE TABLE [dbo].[DeepStockShortSelling] (
[issuerdate] date NOT NULL ,
[timesign] int NOT NULL ,
[stockcode] varchar(10) NOT NULL ,
[stockname] nvarchar(100) NULL ,
[shares] int NOT NULL ,
[amount] float(53) NOT NULL ,
[shareChgPer] float(53) NULL ,
[turnoverChgPer] float(53) NULL ,
[currency] char(3) NULL 
)


GO

-- ----------------------------
-- Table structure for Security
-- ----------------------------
DROP TABLE [dbo].[Security]
GO
CREATE TABLE [dbo].[Security] (
[securityid] varchar(10) NOT NULL ,
[ename] nchar(255) NULL ,
[sname] nchar(255) NULL ,
[tname] nchar(255) NULL ,
[allname] nchar(255) NULL ,
[shortname] nchar(100) NULL ,
[industry] nchar(20) NULL ,
[contact] nchar(30) NULL ,
[Tel] char(30) NULL ,
[Fax] char(30) NULL ,
[address] nchar(255) NULL ,
[Email] char(100) NULL ,
[corporateRepresentative] nchar(30) NULL ,
[recordFrom] nchar(50) NULL ,
[relationid] char(50) NULL ,
[cdate] datetime NULL ,
[mdate] datetime NULL ,
[del] bit NULL 
)


GO

-- ----------------------------
-- Table structure for SecuritySeat
-- ----------------------------
DROP TABLE [dbo].[SecuritySeat]
GO
CREATE TABLE [dbo].[SecuritySeat] (
[NoCode] int NULL ,
[EndNoCode] int NULL ,
[securityid] varchar(10) NOT NULL ,
[RecordDate] datetime NULL ,
[EditDate] datetime NULL ,
[Remark] int NULL ,
[id] int NOT NULL IDENTITY(1,1) ,
[status] smallint NULL 
)


GO
DBCC CHECKIDENT(N'[dbo].[SecuritySeat]', RESEED, 1074)
GO

-- ----------------------------
-- Indexes structure for table DeepStockShortSelling
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table DeepStockShortSelling
-- ----------------------------
ALTER TABLE [dbo].[DeepStockShortSelling] ADD PRIMARY KEY ([issuerdate], [timesign], [stockcode])
GO

-- ----------------------------
-- Indexes structure for table Security
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table Security
-- ----------------------------
ALTER TABLE [dbo].[Security] ADD PRIMARY KEY ([securityid])
GO
