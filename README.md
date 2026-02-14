## SeikiDodge <sub> a Hypixel bedwars auto dodge tool </sub>  
**SeikiDodge**是一款基于Python的Hypixel bedwars自动逃逸工具。通过实时检测游戏日志，SeikiDodge可识别车队加入游戏的事件，自动代替玩家输入`/lobby`实现逃逸。  
**SeikiDodge**旨在为低要求与预算不足玩家提供不同于市面上的辅助组件（如[Lilith Overlay](https://lilith.rip/)）的自动逃逸功能的选择。  

**SeikiDodge** is a Python-based auto-dodge tool for Hypixel bedwars. By monitoring game logs in real time, SeikiDodge can identify when a party joins the game and automatically input `/lobby` to dodge.  
**SeikiDodge** aims to provide players with fewer demands and lower budgets with an auto-dodge tool unlike other auxiliary components available (such as [Lilith Overlay](https://lilith.rip/)).
## 警告 <sub>Warning & Disclaimer  
**SeikiDodge**模拟玩家自动输入指令的行为有**违反Hypixel对外部组件合规性要求**的风险。即使脚本与游戏交互的方式决定了该风险极低，仍有概率导致**账户封禁**。更多细节，查阅[Hypixel的相关政策](https://support.hypixel.net/hc/en-us/articles/6472550754962-Hypixel-Allowed-Modifications)。  

**SeikiDodge**'s simulating player-generated commands violates **[Hypixel's compliance requirements for external components](https://support.hypixel.net/hc/en-us/articles/6472550754962-Hypixel-Allowed-Modifications)**. Even if the way the script interacts with the game makes this risk low, there is still a possibility of account banning.  
>Additionally, we do also note that anything which automates any player gameplay action is strictly disallowed, be those Minecraft modifications, external software or hardware. This includes things such as (but not limited to) auto/burst clicking buttons or macros, auto-sprint, and aim assists.
>
>Finally, modifications that alter the way in which your Minecraft client interacts with and communicates with our server are also strictly disallowed, even if they otherwise fall into an allowed category. Please ensure that any modifications which are used are strictly client-side only, with them not changing or altering the behavior of the game.
>
>If a modification does not fit clearly into any of the allowed modification categories, it should be assumed to be disallowed.
## 环境依赖 <sub>Dependencies</sub>  
Python 3  
pyautogui
## 功能 <sub>Func</sub>  
### AutoDodge  
检测到同一时刻超过一定人数玩家进入游戏，自动执行`/lobby bedwars`。  
When a gang of players entering the game at the same time, execute the `/lobby bedwars` command automatically.  
### UserInPartyExemption
在配置文件启用`toggles.UserIsInParty`后，玩家加入游戏该秒不检测车队或执行自动逃逸。适用于玩家自身在一个组队中的情形。  
When `toggles.UserIsInParty` is enabled in the configuration, the script will not detect parties nor execute [AutoDodge](#autododge-) for the first second the user joins. Practical function for those themselves are in a party.  
## 开发中 <sub>Still in progress...</sub>  
目前仅支持bedwars 4v4v4v4模式，设定车队人数阈值为4。后期将实现对duos, 3v3v3v3模式的支持，并支持自定义触发逃逸车队人数阈值。  
[近期计划](./Developing%20Features.md)  
For now only bedwars 4s mode is supported. And the threshold for the number of players to trigger [AutoDodge](#autododge-) is set to 4. Support for 3s and duos will be added later. The threshold mentioned will support customization soon.  
## 快速开始 <sub>Start</sub>  
**补全依赖**：安装Python，并在终端执行`/pip install pyautogui`  
**Setting up the environment**: Install Python and execute `/pip install pyautogui` in terminal.

**填写配置**：下载SeikiDodge脚本后，编辑`config.json`  
**init the config**:Download SeikiDodge. Edit `config.json`.  
```json
{
  "paths": {
    "GAME_LOG_PATH": "The directory of your minecraft latest.log" # 填入游戏日志路径
  },
  "player": {
    "USER_NAME": "Your profile name in game(Case sensitive)" # 游戏中的用户名（注意大小写）
  },
  "toggles": {
    "AutoRequeue": false, # 启用后，触发逃逸后自动重新加入一局新的同模式排队
    "DodgeWhenEnterRecentQueue": false, # 启用后，加入近期曾加入的排队会自动触发逃逸
    "DodgeWhenPartyExit": true, # 启用后，车队集体退出也会触发自动逃逸
    "UserIsInParty": false # 启用后，加入的第一秒不执行检测与逃逸，如果你在组队中，启用它
  },
  "debug": {}
}
```

**启动游戏**：启动**Minecraft**，进入Hypixel服务器，在服务器中设置语言为`English`  
**Launch Minecraft**: Launch the game and connect to Hypixel server. In `My Profile`-`Select Language` choose `English`  

**启动脚本**：双击`main.py`或在命令行中启动。在服务器中进入游戏，排队开始，AutoDodge进入待命状态  
**Launcher SeikiDodge**: Double click `main.py` or launch it in terminal. Once join the queue of the game, AutoDodge is set to standby.