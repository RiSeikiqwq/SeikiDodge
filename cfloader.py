import json
from dataclasses import dataclass

"""
默认配置，用于在config.json中有缺失时补全
注意此处为dict，布尔值为True-False对；而json中布尔值为true-false对
"""
DEFAULT_CF = {
  "paths": {
    # minecraft游戏本体日志路径
    "GAME_LOG_PATH": "C:/Users/Administrator/.lunarclient/profiles/lunar/1.8/logs/latest.log"
  },
  "player": {
    # 玩家用户名，传参process.process_line()，作为进入待命状态信号，大小写敏感
    "USER_NAME": "Name_in_game"
  },
  "capacities": {
    # 监听缓冲区大小，用于丢弃旧数据
    "LISTEN_BUFFER": 250,
    # 存储最近排队的双端队列容量，DodgeWhenEnterRecentQueue开启后，最近该次内加入过同一局排队自动执行逃逸
    "RECENT_QUEUE_RECORD": 5
  },
  "toggles": {
    # 逃逸后立即加入下一场游戏
    "AutoRequeue": False,
    # 将最近加入的排队列入黑名单，下次加入时自动逃逸
    "DodgeWhenEnterRecentQueue": False,
    # 不仅在车队进入时Dodge，在车队集体退出时也触发Dodge
    "DodgeWhenPartyExit": True,
    # 用户本人是否在组队中，若是，则用户加入该秒豁免检测
    "IsUserInParty": False
  },
  "debug": {}
}


def merge_default_cf(user_cf, default_cf):
    """
    递归迭代排查config.json中是否缺如，若有，则用默认值代替并返回
    :param default_cf: 默认设置(dict)
    :param user_cf: config.json中的设置(dict)
    :return: 配置文件的加载结果，若有缺如，用默认值补全(dict)
    """
    result = default_cf.copy()
    for cf_key, cf_value in user_cf.items():
        if cf_key and isinstance(cf_value, dict) in result:
            result[cf_key] = merge_default_cf(cf_value, result[cf_key])
        else:
            # 递归边界条件
            result[cf_key] = cf_value
    return result


def loadcf(cfname = "config.json"):
    """
    加载配置文件，缺如项填充默认参数
    :param cfname: 配置文件的相对路径，默认为config.json
    :return: 配置文件的加载结果，若有缺如，用默认值补全(dict)
    """
    with open(cfname, 'r', encoding='utf-8') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid Config File: {e}")
    return merge_default_cf(config, DEFAULT_CF)


# 定义dataclass装饰的数据类，构建配置对象，缓存配置信息
@dataclass
class RuntimeCfg:
    LOG_PATH: str
    DodgeWhenEnterRecentQueue: bool
    DodgeWhenPartyExit: bool


@dataclass
class ListenCfg:
    LISTEN_BUFFER: int


@dataclass
class ProcessCfg:
    USER_NAME: str
    IsUserInParty: bool
    RECENT_QUEUE_RECORD: int


@dataclass
class ExecuteCfg:
    AutoRequeue: bool


@dataclass
class Config:
    runtime: RuntimeCfg
    listen: ListenCfg
    process: ProcessCfg
    execute: ExecuteCfg
