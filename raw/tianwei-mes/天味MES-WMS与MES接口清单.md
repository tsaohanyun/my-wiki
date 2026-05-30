---
source_url: 接口说明\天味食品_WMS&博依特MES_接口清单_V1.1_20230620.xlsx
ingested: 2026-05-26
project: 天味家园B栋MES
tags:
- MES
- WMS
- 原始资料
- 天味
- 食品
---

SOURCE: 接口说明\天味食品_WMS&[已脱敏]MES_接口清单_V1.1_20230620.xlsx
DESC: 接口清单-WMS&MES
============================================================
[Sheet: sheet1]
序号	模块	接口名称	描述	传递方向	设计负责人	开发负责人	计划开始日期	计划完成日期	接口联调日期	开发状态	接口地址	备注
1.0	生产执行	备料需求下达接口	MES制定备料需求，备料需求生效时，调用WMS备料信息下达接口，由WMS提供接口供MES调用	POIT->WMS
2.0	生产执行	备料信息反馈接口(罐区)	WMS收到MES的备料指令之后，WMS依据实际情况给MES反馈具体的备料信息，MES提供接口供WMS调用。	WMS->POIT
3.0	生产执行	备料信息反馈接口	WMS收到MES的备料指令之后，WMS依据实际情况给MES反馈具体的备料信息，MES提供接口供WMS调用。	WMS->POIT
4.0	生产执行	备料信息签收接口	MES收到WMS反馈的实际备料信息，生成备料记录，然后针对实物情况进行签收或者拒收，WMS提供接口供MES调用	POIT->WMS
5.0	生产执行	备料需求关闭接口	对于已经备料完成的备料需求，或者需要异常关闭的备料需求，WMS需要告诉MES对该备料需求进行关单操作，MES提供接口供WMS调用	WMS->POIT
6.0	生产执行	车间物料退料信息下达接口	MES触发退料时，退料信息给WMS，WMS提供接口供MES调用	POIT->WMS
7.0	生产执行	车间物料退料确认接口	WMS收到退料消息后，确认是否进行退料，调用MES接口传递信息	WMS->POIT
8.0	生产执行	外包装工单下达接口	MES下推包装信息传递给WMS，用于WMS进行F栋三楼辅料包仓库出库调度使用，WMS提供接口供MES调用	POIT->WMS
9.0	生产执行	外包装工单报工接口(产成品入库)	WMS调用MES接口进行包装工单报工。MES提供接口供WMS调用	WMS->POIT
10.0	生产执行	取消外包装工单报工接口	WMS调用MES接口进行取消包装工单报工。MES提供接口供WMS调用	WMS->POIT
11.0	生产执行	返工出库反馈接口	WMS将返工品出库信息同步给MES，MES提供接口供WMS调用	WMS->POIT
12.0	生产执行	返工出库签收接口	MES收到WMS反馈的实际返工信息，然后针对实物情况进行签收或者拒收，WMS提供接口供MES调用	POIT->WMS

[Sheet: sheet10]
返回
接口概述：
接口编号
接口名称	取消外包装工单报工接口
接口传递方向	WMS->POIT
传输协议
接口频率
接口类型
触发类型
接口简介	1、WMS调用MES接口进行取消包装工单报工。MES提供接口供WMS调用。
2、备注：WMS给SAP传取消入库，MES给SAP进行取消工时报工。
接口逻辑：
在报工成功入库之后，发现有问题，需要取消报工，用到此接口
接口传输数据字段及格式：
WMS传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
productCode	String	产品编码
batch	String	生产批次
Long	取消数量
sapbillno	String	SAP订单号
TYPE	String	报工类型	0 报工 1取消报工
WMS接收返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码
data	响应数据
msg	响应信息

[Sheet: sheet11]
返回
接口概述：
接口编号
接口名称	返工出库反馈接口
接口传递方向	WMS->POIT
传输协议
接口频率
接口类型
触发类型	实时触发
接口简介	1、WMS将立体库的返工品出库信息同步给MES，MES提供接口供WMS调用
接口逻辑：
一步签收，针对返工品的物料，从成品仓库返回给车间的场景。
接口传输数据字段及格式：
WMS传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	必填	备注	MES字段	MES字段描述	备注
materialCode	String	物料编码	是	物料编码
batch	String	批次	是	备料指令单表头ID	批次
outputNumber	Long	数量	是	出库仓库编码	数量
inwareCode	String	入库仓库编码	是	入库仓库编码	接收仓库编码
outwareCode	String	出库仓库编码	是	出库仓库编码	发出仓库编码
outPlant	String	出库工厂编码	是	出库工厂编码
orderNo	String	返工出库单号	是	返工出库单号	纯文本记录
pickDetailKey	String	拣货行号	是	拣货行号
lot05	到期日期
WMS接收返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码
data	响应数据
msg	响应信息
入参
类型	参数格式
[        {			"materialCode": "10000679",			"batch": "2107211656",			"outputNumber": 10,			"inwareCode":"T01",			"outwareCode": "T02",			"outPlant" : "TW1F",			"orderNo":"WMS:2021081101"        },          {			"materialCode": "10000679",			"batch": "2107211656",			"outputNumber": 10,			"inwareCode":"T01",			"outwareCode": "T02",			"outPlant" : "TW1F",			"orderNo":"WMS:2021081102"        }]
说明：一个返工单号可组成一条报文，包含多条明细。但多个返工单号不可在同一条报文中
返回结果示例：
类型	结果格式
成功	{    "code": 200,    "data": null,    "message": "操作成功"}
失败	{    "code": 500,    "data": null,    "message": "【1000067229】对应物料不存在！"}

[Sheet: sheet12]
返回
接口概述：
接口编号
接口名称	返工签收接口
接口传递方向	POIT->WMS
传输协议
接口频率
接口类型
触发类型	实时触发
接口简介	1、MES收到WMS反馈的实际返工信息，然后针对实物情况进行签收或者拒收，WMS提供接口供MES调用
2、备注：MES签收后，备料移库数据由WMS同步给SAP（311），MES拒收后，WMS不同步数据给SAP。
接口逻辑：
接口传输数据字段及格式：
WMS要求传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
orderNo	String	返工出库单号	备料指令单号
sku	String	物料号	物料号
quantity	BigDecimal	数量	数量
batch	String	批号	批号
status	String	状态	1签收，2拒签	状态
factoryCode	String	工厂编码 MESPLANT	工厂编码
pickDetailKey	拣货行号	拣货行号	整行签收或者拒收
WMS返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码	100成，500失败
message	响应信息
success	是否成功	True成功，false失败
请求地址：	测试环境：http://172.16.17.11:18088/wms/external/exteralbasic
入参示例
{
    "application": "MES",
    "async": true,
    "code": "MESPOIT2BMIBUS_ORDERRECEIPT",
    "token": "8DDCFF3A80F4189CA1C9D4D902C3C909",
    "data": [
        {
            "batch": "A230224002",
            "externlineno": "371356996760832",
            "externorderkey": "prepareMaterialNeed_20230626_001",
            "factoryCode": "TW0A",
            "pickDetailKey": "0000116285",
            "quantity": 30.0,
            "sku": "10000490",
            "status": "1"
        }
    ]

[Sheet: sheet2]
返回
接口概述：
接口编号
接口名称	备料需求下达接口
接口传递方向	POIT->WMS
传输协议	HTTP
接口频率
接口类型
触发类型	实时触发
接口简介	1、MES制定备料需求，备料需求生效时，调用WMS备料信息下达接口，由WMS提供接口供MES调用。
2、MES端的备料需求生效时，触发WMS备料信息下达接口
接口逻辑：
接口传输数据字段及格式：
WMS要求传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	必填	备注	MES字段	MES字段描述	备注
inWarehouse	String	目的仓库	是	SAP库存地点，一个库存地点一个单	接收仓库
externorderkey	String	备料指令单号	是	入库单号
planDate	String	计划送货时间	是	yyyy-MM-dd hh:mm:ss	计划发货日期
type	String	类型	是	1：删除检查，2：新增，3：删除	类型
sku	String	物料号	是	物料编码
istank	String	是否罐区	是	1：是，0：否	是否罐区	默认统一：否
externlineno	String	行号	是	MES传备料指令单的ID号	行号
quantity	BigDecimal	数量	是	数量
tankName	String	罐号	否	转料源设备编码	罐号	可以为空
factoryCode	String	工厂编码	是	工厂编码	工厂编码	是指收料的工厂
outWarehouse	String	出库仓库	是	SAP库存地点，一个库存地点一个单	发出仓库	仓库编码
WMS返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码
data	响应数据	Status=1:可以删除；status=2:不能删除
message	响应信息
success	是否成功	True成功，false失败
请求地址：	测试环境：http://172.16.17.11:18088/wms/external/exteralbasic
入参示例
类型	参数格式
备料信息新增	{    "async": true,    "code": "MESPOIT2BMIBUS_ORDER",    "token": "8DDCFF3A80F4189CA1C9D4D902C3C909",    "data": [{        "factoryCode":"TW0A",        "inWarehouse":"T002",        "externorderkey": "000000123",        "planDate": "2021-01-01 00:00:00",        "istank" : "0",        "tankName" : "tank01",        "type": "2",        "sku": "c001",        "externlineno": "1",        "quantity": 4.00    }]}
备料信息删除检查	{	"async": true,	"code": "MESPOIT2BMIBUS_ORDER",	"token": "8DDCFF3A80F4189CA1C9D4D902C3C909",	"data": [{		"factoryCode":"TW0A",		"externorderkey": "000000123",		"type": "1",		"externlineno": "1"	}]}
备料信息删除	{	"async": true,	"code": "MESPOIT2BMIBUS_ORDER",	"token": "8DDCFF3A80F4189CA1C9D4D902C3C909",	"data": [{		"factoryCode":"TW0A",		"externorderkey": "000000123",		"type": "3",		"externlineno": "1"	}]}
返回结果示例：
类型	结果格式
成功	{    "success": true,    "code": "100",    "message": "成功",    "data": 	{		"status": "1"	}}
失败	{    "success": false,    "code": "500",    "message": "失败",    "data": 	{		"status": "2"	}}

[Sheet: sheet3]
返回
接口概述：
接口编号
接口名称	备料信息反馈接口
接口传递方向	WMS->POIT
传输协议
接口频率
接口类型
触发类型	实时触发
接口简介	1、WMS收到MES的备料指令之后，WMS依据实际情况给MES反馈具体的备料信息，MES提供接口供WMS调用。
2、对于罐区和非罐区，MES提供两个不同的服务供WMS调用
3、WMS填写完具体的备料信息之后，回填给MES，MES生成本地的备料记录
接口逻辑：
接口传输数据字段及格式：
WMS传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	必填	备注	MES字段	MES字段描述	备注
orderTableNo	String	备料指令单号	是	入库单号
orderId	String	行号	是	备料指令单表头ID	行号
outWare	String	出库仓库编码	是	出库仓库编码	发出仓库编码
materialCode	String	物料编码	是	物料编码
materialBatchNum	String	备料批号	是	批次号
quantity	BigDecimal	备料数量	是	备料数量
lot05	date	到期日期	是	2.0230627E7	到期日期	为了后续做先进先出处理
pickDetailKey	拣货行号	是	拣货行号	纯文本记录，后续签收回传
WMS接收返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码	备料指令单号
data	响应数据	状态	1成功2失败
message	响应信息
[{
 "dataList": [{
  "materialBatchNum": "A230601002",
  "outWare": "T022",
  "pickDetailKey": "0000116632",
  "quantity": 33800
 }, {
  "materialBatchNum": "A230601001",
  "outWare": "T022",
  "pickDetailKey": "0000116633",
  "quantity": 16200
 }],
 "materialCode": "20004362",
 "orderId": "371783946863872",
 "orderTableNo": "prePraOrder_2023_06_27_018"
}]

[Sheet: sheet4]
返回
接口概述：
接口编号
接口名称	备料信息签收接口
接口传递方向	POIT->WMS
传输协议
接口频率
接口类型
触发类型	实时触发
接口简介	1、MES收到WMS反馈的实际备料信息，生成备料记录，然后针对实物情况进行签收或者拒收，WMS提供接口供MES调用。
2、备注：MES签收后，备料移库数据由WMS同步给SAP（311），MES拒收后，WMS不同步数据给SAP。
接口逻辑：
接口传输数据字段及格式：
WMS要求传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
externorderkey	String	备料指令单号	备料指令单号
sku	String	物料号	物料号
externlineno	String	行号	MES传备料指令的ID号	行号
quantity	BigDecimal	数量	数量
batch	String	批号	批号
status	String	状态	1签收，2拒签	状态
factoryCode	String	工厂编码 MESPLANT	工厂编码
pickDetailKey	拣货行号	拣货行号	整行签收或者拒收
WMS返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码	100成，500失败
message	响应信息
success	是否成功	True成功，false失败
请求地址：	测试环境：http://172.16.17.11:18088/wms/external/exteralbasic
入参示例
{
    "application": "MES",
    "async": true,
    "code": "MESPOIT2BMIBUS_ORDERRECEIPT",
    "token": "8DDCFF3A80F4189CA1C9D4D902C3C909",
    "data": [
        {
            "batch": "A230224002",
            "externlineno": "371356996760832",
            "externorderkey": "prepareMaterialNeed_20230626_001",
            "factoryCode": "TW0A",
            "pickDetailKey": "0000116285",
            "quantity": 30.0,
            "sku": "10000490",
            "status": "1"
        }
    ]
}

[Sheet: sheet5]
返回
接口概述：
接口编号
接口名称	备料需求关闭接口
接口传递方向	WMS->POIT
传输协议
接口频率
接口类型
触发类型	实时触发
接口简介	1、对于已经备料完成的备料需求，或者需要异常关闭的备料需求，WMS需要告诉MES对该备料需求进行关单操作，MES提供接口供WMS调用
接口逻辑：
备料关单是整单关闭，只获取备料需求单号，其需求状态是完成即可关单
接口传输数据字段及格式：
WMS传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
orderTableNo	String	备料需求单号
orderId	String	行号	备料指令单表头ID
materialCode	String	物料编码
status	String	需求单状态	complete：完成
WMS接收返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码
data	响应数据
message	响应信息
[{
	"materialCode": "10000082",
	"orderId": "202587394438400",
	"orderTableNo": "prepareMaterialNeed_20220306_001",
	"status": "complete"
}]

[Sheet: sheet6]
返回
接口概述：
接口编号
接口名称	车间物料退料信息下达接口
接口传递方向	POIT->WMS
传输协议
接口频率
接口类型
触发类型	实时触发
接口简介	接口1：MES触发退料时，退料信息给WMS，WMS提供接口供MES调用
备注：MES给WMS的同时，需要同步给SAP（303）。
接口2：WMS收到退料消息后，确认是否进行退料，调用MES接口传递信息。
备注：WMS返回退料结果给MES后，MES同步给SAP（接收：305，拒收：304）。
接口1：MES车间物料退料单提交时
接口2：WMS确认消息后
接口逻辑：
接口传输数据字段及格式：
WMS要求传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
tableNo	String	退货单号	退货单号	出库单号
materialCode	String	物料编码	物料编码
batch	String	批次	批次
rejectNum	Long	退货数量	退货数量
source	String	退料标识	车间物料退料
家园固定传递”F”
双流固定传递“A”	退料标识	默认S
factoryCode	String	工厂编码	工厂编码	申请退料的工厂
rejectWareCode	String	退料入库仓库编码	退料入库仓库	接收仓库编码
outWarehouse	String	出库仓库	发出仓库	发出仓库编码
WMS返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码
data	响应数据
msg	响应信息
请求地址：	测试环境：http://172.16.17.11:18088/wms/external/exteralbasic
入参示例
{
    "application": "MES",
    "async": true,
    "code": "MESPOIT2BMIBUS_LKPORETURN",
    "token": "8DDCFF3A80F4189CA1C9D4D902C3C909",
    "data": [
        {
            "rejectNum": "10.000",
            "rejectWareCode": "wm1",
            "outWarehouse": "A",
            "factoryCode": "TW0A",
            "batch": "A230619001",
            "materialCode": "10000314",
            "source": "A",
            "tableNo": "rejectMaterilal_20230625_003"
        }
    ]
}

[Sheet: sheet7]
返回
接口概述：
接口编号
接口名称	车间物料退料确认接口
接口传递方向	WMS->POIT
传输协议
接口频率
接口类型
触发类型	实时触发
接口简介	接口1：MES触发退料时，退料信息给WMS，WMS提供接口供MES调用
备注：MES给WMS的同时，需要同步给SAP（303）。
接口2：WMS收到退料消息后，确认是否进行退料，调用MES接口传递信息。
备注：WMS回退料结果给MES后，MES同步给SAP（接收：305，拒收：304）。
接口1：MES车间物料退料单提交时
接口2：WMS确认消息后
接口逻辑：
接口传输数据字段及格式：
WMS传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
tableNo	退料单号	Y	退料单号
materialCode	物料编码	物料编码
batch	批次	批次
rejectNum	退料数量	退料数量	忽略
isReject	是否拒收	车间物料WMS拒收：true
车间物料WMS接收：false	是否拒收	整行签收，否则拒收
WMS接收返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码
data	响应数据
msg	响应信息
[{
 "batch": "A230506001",
 "isReject": false,
 "materialCode": "20005020",
 "rejectNum": 54.2,
 "tableNo": "rejectMaterilal_20230625_004"
}]

[Sheet: sheet8]
返回
接口概述：
接口编号
接口名称	外包装工单下达接口（完工工单）
接口传递方向	POIT->WMS
传输协议
接口频率
接口类型
触发类型	实时触发
接口简介	1、外包装工单生效时MES下推外包装工单信息传递给WMS，WMS进行B栋成品入库时使用，WMS提供接口供MES调用。
接口逻辑：
开始生产才传
接口传输数据字段及格式：
WMS要求传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
productCode	String	产品编码	产品编码
batch	String	生产批次	传递10位的生产批次	生产批次
outputNum	Long	计划数量	计划数量
factory	String	工厂代码	用于区分家园立库和双流立库	工厂代码
sapbillno	String	SAP订单号	SAP生产订单号（12位）	SAP订单号
WMS返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码
data	响应数据
message	响应信息
success	是否成功
请求地址：	测试环境：http://172.16.17.11:18088/wms/external/exteralbasic
{	{
 "batch": "B23062611F",	 "application": "MES",
 "factory": "TW1F",	 "async": true,
 "outputNum": 1500.0,	 "code": "MESPOIT2BMIBUS_LKPOTASK",
 "productCode": "60000024",	 "token": "8DDCFF3A80F4189CA1C9D4D902C3C909",
 "sapbillno": "F01230626043"	 "data": {
}	  "batch": "B23062611F",
  "factory": "TW1F",
  "outputNum": 1500.0,
  "productCode": "60000024",
  "sapbillno": "F01230626043"
 }
}

[Sheet: sheet9]
返回
接口概述：
接口编号
接口名称	外包装工单报工接口(产成品入库)
接口传递方向	WMS->POIT
传输协议
接口频率
接口类型
触发类型
接口简介	1、WMS调用MES接口进行包装工单报工。MES提供接口供WMS调用。
2、备注：WMS给SAP传入库，MES给SAP进行工时报工。
3、备注：MES也不生成生产入库单（因为成品库MES不做管控）
接口逻辑：
接口传输数据字段及格式：
WMS传入参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
productCode	String	产品编码	产品编码
batch	String	生产批次	生产批次
outputNum	Long	完工数量	完工数量
sapbillno	String	SAP订单号	SAP生产订单号（12位）	SAP订单号
TYPE	String	报工类型	0 报工 1取消报工
WMS接收返回参数
表名	字段名	数据元素	数据类型	长度	允许小数位	字段描述	主键	备注	MES字段	MES字段描述	备注
code	响应编码
data	响应数据
msg	响应信息

## 相关页面

- [[tianwei-mes-f000.xlsx]]
- [[tianwei-mes-f001.docx]]
- [[tianwei-mes-f002.docx]]
- [[tianwei-mes-f003.docx]]
- [[tianwei-mes-f004.docx]]
