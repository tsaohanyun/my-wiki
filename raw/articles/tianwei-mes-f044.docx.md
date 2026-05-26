---
source_url: 部署方案评审会\天味食品运维部署文档-v3.docx
ingested: 2026-05-26
project: 天味家园B栋MES
---

SOURCE: 部署方案评审会\天味食品运维部署文档-v3.docx
DESC: 部署-运维文档
============================================================
[/body/p[@paraId=727099F3]] 
[/body/p[@paraId=64CEF896]] 
[/body/p[@paraId=73236F53]] 
[/body/p[@paraId=3172C561]] 
[/body/p[@paraId=1B0AE864]] 
[/body/p[@paraId=0C82091E]] 天味老车间MES平台
[/body/p[@paraId=73A46DA1]] 部署概要方案
[/body/p[@paraId=060EC05D]] 
[/body/p[@paraId=7EF66176]]  
[/body/p[@paraId=4D05D61D]] 
[/body/p[@paraId=73F40640]] 
[/body/p[@paraId=73A0BEC8]] 
[/body/p[@paraId=78C3F078]] 
[/body/p[@paraId=0FED2881]] 
[/body/p[@paraId=1837888D]] 
[/body/p[@paraId=257E38BB]] 
[/body/p[@paraId=7653178D]] 
[/body/p[@paraId=6CBB7036]] 
[/body/p[@paraId=6DCCA859]]                                               
[/body/p[@paraId=5F634B5A]] [已脱敏]
[/body/p[@paraId=7F4EA09F]] 2023年06月
[/body/p[@paraId=0674E74E]] 
[/body/p[@paraId=4DDA5268]] 
[/body/p[@paraId=4B984D07]] 一、项目和部署概述
[/body/p[@paraId=2CCFD8F1]] 面对食品行业数字化智能化发展的变化与挑战，[已脱敏]通过数据化运营平台(MES)的实施，引入先进的管理理念和模式，打造食品生产执行层中的关节环节，通过建立一体化平台，可实现对生产数据的实时采集、展示、MES的接入，实现数据的分析利用及基于数据决策运营，解决信息孤岛效应，促进天味的生产数字化转型升级。
[/body/p[@paraId=3CC24F65]] 本方案将从 网络接入→安全发布→安全访问→服务器以及交换机等硬件→硬件虚拟化→应用部署→数据库和中间件部署→大数据平台部署→运维支持部署→网络端口开放等方面来进行阐述说明。
[/body/p[@paraId=056CB83A]] 最后将综合以上的内容，整理出天味食品在平台部署方面需要提供和准备的清单。
[/body/p[@paraId=36E43714]] 本计划将按照测试环境和生产环境，进行资源的评估和汇总评估。
[/body/p[@paraId=6C21C1F8]] • 超融合网络拓扑图和系统拓扑图
[/body/p[@paraId=661B40C6]] 
[/body/p[@paraId=3E90EB88]] 图（1-1）
[/body/p[@paraId=58A8A70F]] 
[/body/p[@paraId=591DBE71]] 
[/body/p[@paraId=651FE6A4]] 图（1-2）
[/body/p[@paraId=13E00982]] 业务交互图，车间访问，其他网络访问，均通过核心交换机访问系统。
[/body/p[@paraId=14D9713C]] 
[/body/p[@paraId=74D9B654]] 
[/body/p[@paraId=5F34A2CF]] 图（1-3）
[/body/p[@paraId=0156C76E]] 
[/body/p[@paraId=792D6D79]] 如上拓扑图所示，部署涉及到了网络接入（含用户访问与安全防护）、安全访问、安全发布、服务器硬件、硬件虚拟化、应用集群部署、中间件与数据存储、大数据集群部署、底层运维支持等多个方面。接下来就对上述的这些方面做出描述和资源预估。
[/body/p[@paraId=5ECDA2BB]] 
[/body/p[@paraId=11E8DB58]] 
[/body/p[@paraId=2D3378AA]] 
[/body/p[@paraId=2AA8E65A]] 三、部署描述
[/body/p[@paraId=2C99E74F]] 1、网络接入
[/body/p[@paraId=274B88A8]] 如拓扑图（1-1）和（1-3）所示，天味的网络接入采用内网访问，依据部署环境调研，网络接入资源描述如下表（1）所示：
[/body/tbl[1]] [Table: 5 rows]
[/body/p[@paraId=1D2FDAE7]] 表（1-1）
[/body/p[@paraId=4FEDA2DD]] 服务器侧物料清单：
[/body/tbl[2]] [Table: 6 rows]
[/body/p[@paraId=60BA041C]] 表（1-2）
[/body/p[@paraId=5B3C9836]] 2、安全访问
[/body/p[@paraId=3EA83AFD]] 安全访问，就是在部署服务之前，以及在部署完成后的运维维护，都要访问企业里的虚拟机进行操作，我们建议采用VPN+实施服务器的方式访问服务器。
[/body/p[@paraId=56EBE0EA]] 企业需要在企业内网部署VPN服务端，并设置好VPN权限后，分配VPN账号给研发和运维人员。
[/body/p[@paraId=32204527]] 研发和运维人员VPN拨号后，可访问实施服务器；企业对VPN做权限控制；VPN权限可以限制VPN用户具体能访问到什什么机器；实施服务器可访问局域网内部业务平台域名。
[/body/p[@paraId=1B09C256]] 	
[/body/p[@paraId=60711690]] 安全访问资源描述如下表（2）所示：
[/body/tbl[3]] [Table: 4 rows]
[/body/p[@paraId=6768704D]] 表（2）
[/body/p[@paraId=2CA93083]] 
[/body/p[@paraId=71B6D2B3]] 3、安全发布
[/body/p[@paraId=0DBE1750]] 安全发布是为了在业务系统功能有更新或者bug修复的时候，发布新的代码镜像进行版本迭代。
[/body/p[@paraId=50911C52]] 如上述拓扑图所示，企业需要将镜像仓库harbor端口nat映射到公网地址，并且绑定域名和证书，并限制仅有[已脱敏]公司固定ip地址访问。[已脱敏]运维域名，可以将镜像上传到企业的镜像仓库中。
[/body/p[@paraId=69F861D5]] 注意：镜像仓库域名需要绑定证书并且解析到nat公网地址，并且限制[已脱敏]可以访问；而内网的服务器则解析到内网的harbor机器，同样需要证书。
[/body/p[@paraId=78CE25BB]] 需要说明的是，[已脱敏]推送的镜像里并不包含敏感数据（如数据库信息、密码密钥等信息），敏感信息我们已经从镜像中抽离，在镜像启动的时候，才从环境变量中获取，所以镜像的安全保护等级并不用太高，因此建议企业将镜像仓库harbor端口nat映射到公网地址，并限制[已脱敏]公司固定ip访问即可达到较高的安全等级。
[/body/p[@paraId=178A72B8]] 出于安全考虑，不需要企业暴露k8s的api或者ssh端口到公网，只需要在企业私有云内网部署一个服务发布系统，所有的发布都通过这个内网的发布系统进行。这个服务发布的操作，可以由[已脱敏]代发布，也可以由企业掌控发布。
[/body/p[@paraId=355FB305]] 		安全发布资源描述如下表（3）所示：
[/body/tbl[4]] [Table: 2 rows]
[/body/p[@paraId=19712E3B]] 表（3）
[/body/p[@paraId=26073B37]] 
[/body/p[@paraId=7E778624]] 4、服务器硬件
[/body/p[@paraId=4A621920]] 根据初步评估的资源，我们预计需要使用物理CPU128C,超线程（双线程），256线程，1024G内存RAM，约48TB磁盘存储(超融合双副本)。我们在选择虚拟化厂商的时候，需要厂商能提供以下几个方面的高可靠：
[/body/p[@paraId=306AB8D1]] 1）、硬件高可用（涵盖硬件健康检测、CPU高可靠、内存高可靠、硬盘高可靠、网卡高可靠、RAID卡高可靠、电源高可靠、告警机制等）；
[/body/p[@paraId=0940FBC0]] 2）、计算层高可用（涵盖虚拟机高可用HA、虚拟机快照、虚拟机热迁移、动态资源调度、虚拟机优先级等）；
[/body/p[@paraId=1D06B5B7]] 3）、存储层高可用（涵盖数据多副本保护、数据仲裁保护、数据热备盘保护、IO QOS保护、硬盘亚健康检测、数据快速重建、数据延时删除等）；
[/body/p[@paraId=2575F377]] 4）、网络高可用（涵盖网络管里面高可靠、网络控制面高可靠、数据转发面高可靠、三层转发网络可靠性、网络连通性探测、VXLAN网络可靠性、网口故障自动恢复等）。
[/body/p[@paraId=3909E8BC]] 
[/body/p[@paraId=4C32393B]] 服务器硬件资源描述如下表（4）所示：
[/body/tbl[5]] [Table: 2 rows]
[/body/p[@paraId=6F349900]] 表（4）
[/body/p[@paraId=4FDE7DE6]] 
[/body/p[@paraId=2590C5C9]] 5、需天味食品决策或准备的资源信息汇总
[/body/p[@paraId=3E0072B5]] 上述多个方面都较为详细的说明了每个方面所需的资源信息，包括资源描述、资源准备方等相关信息。接下来就统一汇总企业所需准备和提供的资源。
[/body/p[@paraId=323D568E]] 涉及到需要企业决策或者准备的资源如下表（5）所示：
[/body/tbl[6]] [Table: 18 rows]
[/body/p[@paraId=3EF23DFF]] 表（5）
[/body/p[@paraId=6E41277E]] 
[/body/p[@paraId=5494EE08]] 	上述表（5）中最后一列标黄的为企业所需决策或准备的资源必选项。在表中未列出的如硬件虚拟化、虚拟机创建、应用集群部署、中间件与数据存储、大数据集群部署、底层运维支持等则由[已脱敏]与虚拟化厂商共同完成即可。
[/body/p[@paraId=707C7A0D]] 域名清单如下（均是内网解析）：
[/body/p[@paraId=72633A0F]] 
[/body/tbl[7]] [Table: 25 rows]
[/body/p[@paraId=3504C900]] 
[/body/p[@paraId=139FD686]] 域名解析详细信息如下：
[/body/tbl[8]] [Table: 25 rows]
[/body/p[@paraId=093172A2]] 
[/body/p[@paraId=490764DA]] 
[/body/p[@paraId=3BB4DB48]] 目前有生产和测试环境，所以建议生产和测试环境网络隔离，即测试、生产环境网络隔离，通过vlan隔离。
[/body/p[@paraId=244D3C10]] 建议网段：
[/body/p[@paraId=420602A9]] 生产环境（未分配）：192.168.240.0/24;（使用其他网段也可以）
[/body/p[@paraId=7BA0E6DB]] 测试环境（已分配）：192.168.230.0/24；
[/body/p[@paraId=66C55B1D]] 特别说明：其中harbor镜像仓库的机器和jenkins发布的机器在生产环境的网段下，且需要与测试、生产环境互相通讯。
[/body/p[@paraId=3C45559B]] 生产环境网段：至少需预留 60个IP（一期约使用40个）；
[/body/p[@paraId=4AF1EEA1]] 测试环境网段：至少需预留 40个IP（一期约使用25个）；
[/body/p[@paraId=3E5C6FBA]] 2023-07-18更新：已确认生产环境与测试环境，不做网段隔离（注意：部署完成后，IP将不可再修改，届时若需做隔离，只能在现有IP基础上做隔离）
