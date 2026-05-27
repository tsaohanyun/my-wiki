---
source_url: 接口说明\集成测试\系统联调测试方案V1.0.docx
ingested: 2026-05-26
project: 天味家园B栋MES
tags:
- MES
- SAP
- WMS
- 原始资料
- 天味
---

SOURCE: 接口说明\集成测试\系统联调测试方案V1.0.docx
DESC: 接口-系统联调测试方案
============================================================
[/body/p[@paraId=648A637E]] MES-SAP-WMS系统集成联调测试方案
[/body/p[@paraId=2C17CF89]] • 测试目标
[/body/p[@paraId=288190CA]] MES-SAP-WMS三系统共同完成业务功能集成测试。
[/body/p[@paraId=0D9C5CF1]] 
[/body/p[@paraId=42A64EEF]] • 测试对象与测试业务
[/body/p[@paraId=012F084F]] 测试对象：MES-SAP-WMS集成接口及相关业务；
[/body/p[@paraId=381DC533]] 测试业务：
[/body/tbl[1]] [Table: 12 rows]
[/body/p[@paraId=0F9A6A42]] 
[/body/p[@paraId=2472BAD9]] 
[/body/p[@paraId=69230F19]] 
[/body/p[@paraId=01071D4F]] • 测试准备
[/body/tbl[2]] [Table: 8 rows]
[/body/p[@paraId=2E9FEB39]] 
[/body/p[@paraId=480FAC05]] 
[/body/p[@paraId=1C470C24]] 1、炒锅设备的组网如下：
[/body/p[@paraId=6CA99020]] 
[/body/p[@paraId=400B0DAB]] ①炒锅设备的交换机是利用设备控制箱内的电源，若某个炒锅在不用的情况下，则该交换机就断电，现场约定该部分交换机的电源修改由设备部进行调整。
[/body/p[@paraId=03181E49]] ②现在的炒锅设备网络，连接到每个柜体内的交换机，每个柜内的交换机和设备是同一路，当哪个设备不用的情况下，生产人员均会断电，故此时交换机也中断，需将交换机电源改为一直通电的电源上。
[/body/p[@paraId=4F4E7CBB]] 2、数据采集完毕
[/body/p[@paraId=11140434]] 3、数据核对完毕
[/body/p[@paraId=47F20972]] 
[/body/p[@paraId=2B6129FD]] • 测试计划和参加人员
[/body/p[@paraId=4994A501]] 测试时间：2023年08月14日 9：00 ----2023年08月15日 17：00
[/body/p[@paraId=668AE5E3]] 参加人员：甲方项目组、[已脱敏]、双贝、厍文君、余春、刘春雷。
[/body/tbl[3]] [Table: 11 rows]
[/body/p[@paraId=4DC6118F]] 
[/body/p[@paraId=429C8114]] 
[/body/p[@paraId=0910A5D9]] 
[/body/p[@paraId=5EB7378B]] • 测试步骤
[/body/p[@paraId=35DAB4CD]] 1. 平台侧维护配方信息：
[/body/p[@paraId=2256E621]] 工艺人员在MES平台上维护好测试用的配方信息。
[/body/p[@paraId=7AC748AA]] 
[/body/p[@paraId=4A3BA94E]] 1. 根据配方信息，在现场进行配料：
[/body/p[@paraId=6DDADF70]] 操作工在现场准备好物料（用自来水代替模拟）、物料桶（贴好二维码）、电子秤、PDA，根据测试配方信息进行配料操作。
[/body/p[@paraId=00BABE2F]] 
[/body/p[@paraId=171EB32B]] 1. 配料完成后，拉料到炒锅：
[/body/p[@paraId=0FCC44E7]] 操作工在现场准备好拖车（贴好二维码），将配好的物料通过拖车拉到炒锅（贴好二维码）旁边。
[/body/p[@paraId=2A7C0D73]] 
[/body/p[@paraId=741CC775]] 1. 用PDA将物料桶、拖车、炒锅进行扫码校验
[/body/p[@paraId=0F1CD16D]] 操作工通过PDA扫描拖车、炒锅上的二维码，进行绑定校验。
[/body/p[@paraId=5F9AEC7B]] 
[/body/p[@paraId=556F1920]] 5、炒制工艺数据下发到设备PLC：
[/body/p[@paraId=2223D6CA]] ① 双贝验证在设备侧PLC和触摸屏中是否有收到工艺数据，以及数据是否一致；
[/body/p[@paraId=53F3C804]] ② 数据一致即代表验证通过。
[/body/p[@paraId=4A4D29FA]] 
[/body/p[@paraId=0D504493]] 6、工步执行（1）：
[/body/p[@paraId=5B636C54]] ① 操作工进行放油、点火操作，验证MES是否收到“第一步执行中”信号；
[/body/p[@paraId=103FC3CF]] ② 加热过程中，[已脱敏]验证MES侧接收到的油温数据变化是否与现场设备一致，操作工验证当火力、温度不符合工艺要求时，设备侧是否有异常提醒；
[/body/p[@paraId=7947A840]] ③ 操作工提前对物料桶进行扫码，验证MES物料诊断，以及诊断成功信号的下发；
[/body/p[@paraId=4D0E871A]] ④ 油温加热到工艺要求的数值后，[已脱敏]验证MES是否读取到第一步完成信号，操作工验证设备侧是否有提醒人工倒料；
[/body/p[@paraId=4161C0FE]] ⑤ 物料信息诊断成功、第一步完成均满足后，操作工验证设备是否有提醒进行投料；
[/body/p[@paraId=5E35B43A]] ⑥ 操作工完成投料后，[已脱敏]验证MES是否接收到投料完成信号，操作工验证设备侧是否开始计时下一步的炒制时长。
[/body/p[@paraId=4D4FFABF]] 
[/body/p[@paraId=10535DE3]] 7、工步执行（N）：
[/body/p[@paraId=6945818A]] ① MES接收到投料完成信号后，下发工步信号，操作工验证现场设备侧是否成功接收到工步信号，以及在触摸屏主界面是否正确显示该工步的工艺参数；
[/body/p[@paraId=2A876E31]] ② 工步执行过程中，[已脱敏]验证MES是否读取到“执行中”信号，操作工验证当搅拌频率、火力、温度不符合工艺要求时，设备侧是否有异常提醒；
[/body/p[@paraId=289B0639]] ③ 操作工提前对物料桶进行扫码，验证MES物料诊断及诊断成功信号下发；
[/body/p[@paraId=5E4A89EE]] ④ 物料信息诊断成功、提前提醒投料时间达到均满足后，操作工验证设备侧是否成功解锁提升机，以及设备侧是否有提醒操作工进行投料；
[/body/p[@paraId=6C9A4567]] ⑤ 炒制时长达到设定值后，[已脱敏]验证MES是否有接收到工步完成信号；
[/body/p[@paraId=7565675E]] ⑥ 操作工完成投料后，[已脱敏]验证MES是否接收到投料完成信号，操作工验证设备侧是否开始计时下一步的炒制时长；
[/body/p[@paraId=4E3B712A]] ⑦ 进入下一步，继续重复第①步往后的步骤。
[/body/p[@paraId=59714760]] 
[/body/p[@paraId=69CC1606]] 8、排料，完成炒锅配方：
[/body/p[@paraId=5575D073]] ① 最后一步炒制完成后，操作工在设备侧开启排料开关（排料阀开），并验证系统是否有开始计时排料时长；
[/body/p[@paraId=23CAB7AD]] ② 排料完成后，操作工在设备侧开启排料开关（排料阀关），并验证系统是否正常结束计时排料时长。
[/body/p[@paraId=32F530E7]] 
[/body/p[@paraId=0361EB95]] 9、特殊场景1（未收到物料诊断成功信号）验证：
[/body/p[@paraId=5E97688D]] 炒制过程中，设备已经到达工艺标准（温度、时长），若未收到物料诊断成功信号，操作工需验证设备侧是否有触发告警提醒。
[/body/p[@paraId=7192D69E]] 
[/body/p[@paraId=29404CBB]] 10、特殊场景2（炒锅设备跳闸）验证：
[/body/p[@paraId=22CC79FA]] 炒制过程中，若炒锅设备跳闸，在恢复上电后，操作工观察设备与MES的通讯指示灯，恢复通讯后，在领班权限下，手动触发当步的工步完成信号，人工解锁、进行投料。若未能恢复通讯，则采用其他异常处理方案。
[/body/p[@paraId=19702FB5]] 
[/body/p[@paraId=7FE2FBF5]] 11、特殊场景3（一个工步多个物料桶）验证：
[/body/p[@paraId=41E8D19A]] ① 操作工需在MES系统对每桶进行逐步扫码，即先在MES系统扫第一个物料桶，成功后下发诊断成功信号，设备侧收到信号后，再结合工步提前完成信号进行解锁提升机，人工投料。投料完成后，需人工再扫第二桶的码，依次重复；
[/body/p[@paraId=1BBDD47E]] ② 当人工未及时校验物料并投料时，操作工需验证设备侧是否会延时告警，其中延时时长可人工设定；
[/body/p[@paraId=5C8DAD8E]] ③ 设备收到诊断成功信号后，设备侧组合其他条件后解锁提升机，进行倒料，设备自身判断执行一个周期；
[/body/p[@paraId=4247FAE0]] ④ [已脱敏]验证MES系统在收到提升机动作后，是否就断开诊断成功信号，以保证设备侧收到一个脉冲信号。
[/body/p[@paraId=5E70387E]] 
[/body/p[@paraId=123420CE]] • 测试总结
[/body/p[@paraId=74DB28F1]] 总结本次测试准备、测试执行、问题跟踪等过程中的主要问题、问题解决经验、改进建议等内容；
[/body/p[@paraId=16BEA8E7]] 对测试结果认可，则需各方对《MES系统与设备PLC的交付方案》进行签字确认。
[/body/p[@paraId=2B62696E]] 
[/body/p[@paraId=79736DAF]] • 附件1：设备类表
[/body/tbl[4]] [Table: 50 rows]
[/body/p[@paraId=6920B0BC]] 
[/body/p[@paraId=262910F6]] 
[/body/p[@paraId=107C8017]] • 附件2：IP分配表
[/body/tbl[5]] [Table: 47 rows]
[/body/p[@paraId=613B1F93]] 
[/body/p[@paraId=34372CEF]] 网闸设备：
[/body/tbl[6]] [Table: 17 rows]
[/body/p[@paraId=3DE0AF03]]


## 相关页面

- [[tianwei-mes-f000.xlsx]]
- [[tianwei-mes-f001.docx]]
- [[tianwei-mes-f002.docx]]
- [[tianwei-mes-f003.docx]]
- [[tianwei-mes-f004.docx]]
