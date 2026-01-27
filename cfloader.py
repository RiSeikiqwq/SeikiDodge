import json


# 注意dict中布尔值True-False，json中布尔值true-false
DEFAULT_CF = {
  "paths": {
    "GAME_LOG_PATH": "C:/Users/Administrator/.lunarclient/profiles/lunar/1.8/logs/latest.log"
  },
  "player": {
    "USER_NAME": "Name_in_game"
  },
  "toggles": {
    "DodgeWhenPartyExit": True,
    "UserIsInParty": False
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
