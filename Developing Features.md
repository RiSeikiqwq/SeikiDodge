## 漏洞修复  
以`{"server":"minixx","gametype":"BEDWARS","mode":"...","map":"..."}`为待命标识  
而非`[本玩家] has joined the game`  
导致在少数情况下车队在server json消息发出前加入，无法识别  
**已修复**  

## 待实现功能  
**配置文件json格式化** 使用json文件存储玩家名、日志路径等设置，读取常量统一在main()实现  
**AutoQueue** 输入`/lobby`后自动输入`/play bedwars_<mode>`  
**房间黑名单** 向自定义容量队列`lobby_blocklist`存储近期逃逸的房间号，再次加入时自动逃逸  
**兼容车队集体退出消息** 车队集体退出消息视作加入，一并触发Dodge **已实现**  

## 近期不考虑  
**对非英文字符和非英文环境的读取支持** 