
[TOC]

```
当日证券代码表
http://www.hkexnews.hk/sdw/search/stocklist_c.asp?SortBy=StockCode&Lang=CHI&ShareholdingDate=20160613
股份解码
http://sdinotice.hkex.com.hk/di/NSSrchCorp.aspx?src=MAIN&lang=ZH&in=1&
券商追踪
http://www.hkexnews.hk/sdw/search/search_sdw_c.asp  POST
```

# 系统架构

## 在设计框架时考虑的问题

1. 爬虫框架与数据处理框架分开。
	2. 每一步处理的问题相对独立，有利于以后修改成分布式爬虫框架。
	3. 易于隔离故障，及时发现及修复故障点。
	4. 爬虫框架和数据处理业务有着不同的技术实现方式，隔离以后双方可以独立发展，互不影响。

1. 完善的异常报错机制。
	2. 集成zabbix的异常检测，及时发现异常。
	3. 保留异常现场，及时适配web页面的修改。

1. 支持多进程并发运行模式。
	2. 充分利用每一个CPU核心，缩短任务消耗时间，及时发现问题。
	3. 为以后修改成分布式爬虫打好基础。

1. 作为框架，需要支持javascript技术。
	2. javascript在现代web技术中起到越来越重要的作用，很多反爬虫技术使用了javascript，传统爬虫技术受到越来越多的限制，作为一个通用型爬虫框架，有必要支持使用javascript技术的网站。
	3. 不使用javascript技术的网页具有加载速度快的优势，框架也必须支持这样的爬虫，以提高运行效率。

## 系统结构图

![][spider_frame]

## 系统文件结构说明

文件/目录名称 | 说明
------------------ | -----------------------------
`hk_codemap` | 爬虫：港股参与者编号与经纪编号的对应关系
`hk_qszz_gfjm` | 爬虫：港股券商追踪和股份解码
`hk_shortselling` | 爬虫：港股市场沽空
`hkexe` | 以上三个爬虫需要的外部工具
`main.py` | 框架引擎
`settings.py` | 配置文件

* 系统采用插件式结构，不同的爬虫安装在不同的目录下面，互不干扰，同时在配置文件中配置初始爬虫任务。
* 抓取、分析和提交模块各自独立，一旦出现故障，比较容易确定故障位置，提高故障响应速度。
* 系统支持灵活调度爬虫，可按照需要启动一个、数个或者全部爬虫。
* 系统采用多进程来调度爬虫，每个爬虫运行在单独的进程中，以充分利用CPU的多个核心，并且互不干扰。
* 爬虫可以向系统动态提交新的爬虫任务，系统将统一分配到进程池来处理新的爬虫。
* 统一处理输出，系统收集各爬虫运行过程中的标准输出，将其统一编码后输出到标准输出和日志文件中。
* 统一处理异常，系统截获各爬虫运行过程中抛出的异常，尽量将其转换成可阅读的格式，并输出到标准输出和日志文件中。
* 统一处理超时，系统设置进程级别的超时定时器，当爬虫任务运行超时时，系统将主动结束该任务，同时爬虫任务的超时时间由该任务的提交者来确定。
* 编写爬虫需要严格遵循系统规范，详见代码注释。

# 数据库表结构

## Security

> 经纪公司基本状况表

列名       | 说明 | 字段类型 | 长度 | NULL | PK | INDEX | 备注
-----------|-----|---------|----:|------|-----|------|-----
securityid|参与者编码|varchar|10|N|Y|N|自增长主键
ename           | 英文公司名
sname           | 简体公司名
tname           | 繁体公司名
allname     | 公司全称
shortname       | 公司简称
industry        | 所属行业
contact     | 联系方式
Tel             | 电话
Fax             | 传真
Email           | 邮箱
corporateRepresentative     | 法人代表
address                     | 地址
recordFrom                      |
relationid                      | 关联ID
cDate                           | 创建日期
mDate                           | 修改日期
del                             |

## SecuritySeat

> 经纪公司席位关系表

列名       | 说明 | 字段类型 | 长度 | NULL | PK | INDEX | 备注
-----------|-----|---------|----:|------|-----|------|-----
NoCode             | 经纪编号起始编码|||Y||Y|
EndNoCode   | 经纪编号结束编码|||Y||Y|
securityid|参与者编码|varchar|10|N||Y|
RecordDate         | 记录日期
EditDate               | 编辑日期
Remark             |
id                     | id
status             | 状态

## DeepSecurityHolder

> 券商追踪原始数据表

列名       | 说明 | 字段类型 | 长度 | NULL | PK | INDEX | 备注
-----------|-----|---------|----:|------|-----|------|-----
changedate|变更日期|date||N|N|Y|
securityid|参与者编码|varchar|10|N|N|Y|只记录'B'，'C'开头的参与者
stockcode|证券代码|varchar|10|N|N|Y|
holdqty|持股量|bigint||N|N|N|
holdqtyper|持股量占已发行股本的百分比|float||Y|N|N|
daychgqty|持股量日变化量|bigint||N|N|N|当日持股量-相同证券代码和参与者编码的前第1条记录的持股量
daychgper|持股量百分比日变化量|float||N|N|N|当日持股量占比-相同证券代码和参与者编码的前第1条记录的持股量占比
wekchgqty|持股量周变化量|bigint||N|N|N|当日持股量-相同证券代码和参与者编码的前第5条记录的持股量
wekchgper|持股量百分比周变化量|float||N|N|N|当日持股量占比-相同证券代码和参与者编码的前第5条记录的持股量占比
monchgqty|持股量月变化量|bigint||N|N|N|当日持股量-相同证券代码和参与者编码的前第20条记录的持股量
monchgper|持股量百分比月变化量|float||N|N|N|当日持股量占比-相同证券代码和参与者编码的前第20条记录的持股量占比

## DeepStockHolder

> 股份解码原始数据表

列名       | 说明 | 字段类型 | 长度 | NULL | PK | INDEX | 备注
-----------|-----|---------|----:|------|-----|------|-----
changedate|变更日期|date||N|Y|Y|
ename |股东英文名|varchar|255|Y|N|Y|
tname |股东繁体名|varchar|255|Y|Y|Y|
sname |股东简体名|varchar|255|Y|N|Y|
capicity|股东身份|char|1|N|N|N|0-所有权益披露者<br>1-个人大股东<br>2-法团大股东<br>3-董事/最高行政人员<br>4-董事/行政人员投资于法团相联公司<br>-1-未知
eventcode|事件编号|varchar|20|N|N|N|
stockcode|证券代码|varchar|10|N|Y|Y|
avgprice|均价|float||Y|N|N|
classofshares|权益代号|varchar|50|Y|N|N|
changeQtyL|好仓变更数量|bigint||Y|N|N|
holdQtyL|好仓持仓数量|bigint||Y|N|N|
issuerPerL|好仓佔巳發行股本之百分比|float||Y|N|N|
changePerL|好仓佔巳發行股本之百分比-变化量|float||Y|N|N|
changeQtyS|淡仓变更数量|bigint||Y|N|N|
holdQtyS|淡仓持仓数量|bigint||Y|N|N|
issuerPerS|淡仓佔巳發行股本之百分比|float||Y|N|N|
changePerS|淡仓佔巳發行股本之百分比-变化量|float||Y|N|N|
changeQtyP|可借出仓变更数量|bigint||Y|N|N|
holdQtyP|可借出仓持仓数量|bigint||Y|N|N|
issuerPerP|可借出仓佔巳發行股本之百分比|float||Y|N|N|
changePerP|可借出仓佔巳發行股本之百分比-变化量|float||Y|N|N|

## DeepMarketShortSelling

> 大盘沽空原始数据表

列名       | 说明 | 字段类型 | 长度 | NULL | PK | INDEX | 备注
-----------|-----|---------|----:|------|-----|------|-----
issuerdate| 发生日期|date||N|Y|Y
timesign| 时间段标志|int||N|Y|Y|0-上午<br>1-下午
currency | 交易币种|char|3|N|Y|N|该币种不影响大市成交额和成分股成交额的币种<br>HKD-港币<br>CNY-人民币<br>USD-美元
totalShare| 大市沽空量|int||N|N|N|
totalTurnover| 大市沽空额|float||N|N|N|
constituentTurnover| 成分股成交额|float||N|N|N|以港币为货币单位
marketTurnover| 大市成交额|float||N|N|N|以港币为货币单位

## DeepStockShortSelling

> 证券沽空原始数据表

列名       | 说明 | 字段类型 | 长度 | NULL | PK | INDEX | 备注
-----------|-----|---------|----:|------|-----|------|-----
issuerdate| 发生日期|date||N|Y|Y
timesign| 时间段标志|int||N|Y|Y|0-上午<br>1-下午
stockcode|证券代码|varchar|10|N|Y|Y|
stockname|证券名称|varchar|50|Y|N|N|
currency | 交易币种|char|3|N|Y|N|HKD-港币<br>CNY-人民币<br>USD-美元
shares| 沽空量|int||N|N|N|
amount| 沽空额|float||N|N|N|
shareChgPer| 沽空量变幅|float||N|N|N|
turnoverChgPer| 沽空额变幅|float||N|N|N|

# 处理流程

## 经纪编号与参与者编号维护流程

``` sequence
spider-->txt: 定时执行，产生参与者编号、经纪编号和券商基本情况
Note right of spider: spider finished
spider->exe: notify
exe->txt: read
exe->DB: Security & SecuritySeat
exe->spider: notify
```

## 券商追踪

``` sequence
spider-->txt: 定时执行，产生券商追踪基本数据
Note right of spider: spider finished
spider->exe: notify
exe->txt: read
exe->data: 维护本地21日数据文件
Note right of exe: 产生本地sql文件
Note right of exe: 计算日变化、周变化、月变化，产生本地xml文件
exe->DB: DeepSecurityHolder
exe->spider: notify
```

## 股份解码

``` sequence
spider-->exe: 获得DeepMarketShortSelling相应股票的最后一日的日期
spider-->txt: 定时执行，产生股份解码基本数据
Note right of spider: spider finished
spider->exe: notify
exe->txt: read
exe->DB: DeepMarketShortSelling
exe->spider: notify
```

## 市场沽空

``` sequence
spider-->txt: 定时执行，产生沽空基本数据
Note right of spider: spider finished
spider->exe: notify
exe->txt: read
exe->rds: 请求成分股成交额和大市成交额
exe->DB: DeepStockHolder & DeepStockShortSelling
exe->spider: notify
```

# 系统运维监控说明

## 环境安装

1. 从[Python主页]安装Python2的32位版本，安装到C:\Python27，并在系统路径中加入安装路径C:\Python27
2. 从[CasperJS主页]安装CasperJS，安装到C:\casperjs，安装路径为`$CasperJS`
3. 从[PhantomJS主页]安装PhantomJS，直接解压到C盘根目录，安装路径为`$PhantomJS`
4. 在系统路径中添加`$CasperJS\bin`目录和`$PhantomJS\bin`目录
5. 安装zmq：`pip install pyzmq`
6. 安装简繁转换库opencc：`pip install opencc-python`

## 系统初始化

1. sql目录下保存了系统初始化需要的sql脚本。
2. create_table.sql：建表脚本。
2. init.sql《券商追踪》《股份解码》：根据原表数据初始化新表数据。
3. init.sql《经纪公司简称》：根据原表数据的公司简称部分初始化新表的公司简称，**必须**在新表数据的“参与者编号与经纪编号的对应关系”至少执行过一次以后才能执行，否则没有效果。
4. searchHolderStock.sql替换了原来的存储过程，**请先备份原存储过程**。
5. sp_GetShortSelling.sql替换了原来的存储过程，**请先备份原存储过程**。

## 系统配置

> 配置项的详细含义参见配置文件注释

1. settings.py
2. hkexe/config.ini
3. hkexe/tsci.udl

## 运维监控

1. 每日备份基础表：Security，SecuritySeat。
2. 定义计划任务，定时调度相应爬虫。
	3. 参与者编号与经纪编号的对应关系，以及券商追踪，股份解码可以一起调度。
	4. 市场沽空分两次调度，一次是调度上午的数据，一次是调度全日的数据。
2. 使用zabbix对系统进行监控。
2. 使用监控日志的方式（Host>>目标主机>>item>>create item）添加监控项，参考[zabbix log monitor]。
3. 要监控的日志文件，位于安装路径的log目录下，名为yyyymmdd.log的文件。
4. 处理异常时，根据log目录下的日志文件分析是入库产生的问题还是爬虫数据问题。
	5. 入库问题可以在hkexe/log目录下参考入库日志。
	6. 爬虫数据问题可以参考相应爬虫生成的现场文件，一般有两个：png和html，分别保存了故障时的网页截图和网页内容，一般可以快速定位到故障原因。


[spider_frame]: https://dl.dropboxusercontent.com/u/641927/myspider/spider_frame.png
[zabbix log monitor]: https://www.ttlsa.com/zabbix/zabbix-monitor-logs/
[Python主页]: http://www.python.org
[CasperJS主页]: http://casperjs.org/
[PhantomJS主页]: http://phantomjs.org/