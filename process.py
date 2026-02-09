import json
import re

# status (bool)
waiting_for_game = False
# count players joining or exiting at the same time (dict)
join_counters = {}
exit_counters = {}


def parse_json_line(line):
    """
        尝试将日志行解析为 JSON，返回 dict 或 None
        """
    try:
        # 定位第一个 "{"
        start = line.find("{")
        if start == -1:
            return None
        # 定位最后一个 "}"
        end = line.rfind("}")
        if end == -1 or end <= start:
            return None
        # 提取花括号内的部分
        json_str = line[start:end + 1]
        # 解析JSON
        obj = json.loads(json_str)
        if isinstance(obj, dict):
            return obj

    except json.JSONDecodeError:
        return None


def process_line(line, user_name):
    """
    分析单条日志行，更新waiting_for_game，初始化join_counters
    当<本玩家> has joined，进入待命状态
    当进入bedwars大厅，服务器发送大厅json信息，退出待命状态
    :return json_obj, NeedUpdateObj: 若line为进入的游戏等待厅信息，返回存储该信息的字典json_obj与更新信号，否则返回None, False
    """
    global waiting_for_game, join_counters
    if user_name + ' has joined' in line:
        waiting_for_game = True
        join_counters.clear()
        exit_counters.clear()
        print("AutoDodge Standby")
    json_obj = parse_json_line(line)
    if json_obj:
        # 例如 {"server":"minixx","gametype":"BEDWARS","mode":"...","map":"..."}
        if json_obj.get("gametype") == "BEDWARS" and "mode" in json_obj and "map" in json_obj:
            return json_obj, True
        # 例如 {"server":"dynamiclobbyxx","gametype":"BEDWARS","lobbyname":"..."}
        elif json_obj.get("gametype") == "BEDWARS" and "lobbyname" in json_obj:
            # 除初始化作用外，与main()中激活dodge_execute()即退出待命的设计互为补充
            waiting_for_game = False
            join_counters.clear()
            exit_counters.clear()
            print("AutoDodge Off Guard")
            return None, False
    return None, False


class TimeStamp(str):
    """
    Standard pattern of timestamp fetched from the head of single line of log
    """
    def __new__(cls, value, exempt=False):
        """
        TimeStamp是以'hh:mm:ss'为标准格式的字符串，表明单行日志开头的时间戳
        常见需要豁免检测的情形-用户本人在party中
        :param exempt: 需要添加的豁免属性，对于.exempt==True的TimeStamp，该TimeStamp加入的玩家一律豁免检测
        """
        # 作为不可变类型str的子类，TimeStamp的值是在实例化之前构造的，实际内容必须在__new__()而非__init__()中构造
        # 继承str的__new__()，创建str示例
        obj = super().__new__(cls, value)
        # 额外属性.exempt
        obj.exempt = exempt
        return obj


def get_time(line, user_name, is_user_in_party):
    """
    从日志每行开头[hh:mm:ss]格式中获取时间戳
    :param user_name: 玩家用户名
    :param line: listen模块监听到的单行日志
    :param is_user_in_party: 检测用户本人是否在车队中，若是，返回豁免信号，该秒豁免检测
    :return (ts1, ts2, exempt_signal): 时间戳字符串'hh:mm:ss'，分别向process.join/exit_counters输入键； 豁免信号，向维护缓存的maintain_ts()传参
    """
    try:
        # re.match方法返回Match对象，在line开头匹配形如[hh:mm:ss]格式内容
        ts_match = re.match(r"\[{1}(\d{2}:\d{2}:\d{2})\]", line)
        if not ts_match:
            return None, None, False
        # 去掉匹配对象的中括号
        raw_ts = ts_match.group(1)
        exempt_signal = is_user_in_party and (user_name + ' has joined') in line
        if 'has joined' in line:
            return raw_ts, None, exempt_signal
        elif 'has quit' in line:
            return None, raw_ts, exempt_signal
        else:
            # 对于含时间戳但无join/quit的消息，如倒计时信息，必须指定返回值，避免unpack non-iterable NoneType异常
            return None, None, exempt_signal

    except Exception:
        print(f"errors occurred when getting time stamp")


def maintain_ts(raw, ts_cache, exempt_signal=False):
    """
    接受时间戳字符串,返回带exempt属性的TimeStamp类型，检查前一TimeStamp属性以决定新TimeStamp属性；
    若收到豁免信号，则相同时间戳(hash)的TimeStamp.exempt强制为True
    :param raw: 时间戳字符串源
    :param ts_cache: 储存前一对象属性的缓存，并最终被更新为raw的TimeStamp对象
    :param exempt_signal: 豁免检测信号
    :return:
    """
    if raw is None:
        return None, ts_cache
    ts = TimeStamp(raw)
    # 若新ts和旧ts时间戳为同一秒，继承旧ts的exempt属性
    if ts_cache and str(ts_cache) == raw:
        ts.exempt = getattr(ts_cache, 'exempt', False)
    # 若收到豁免信号，从该ts起则相同时间戳(hash)的TimeStamp.exempt强制为True
    if exempt_signal:
        ts.exempt = True
    # 更新缓存
    ts_cache = ts
    return ts, ts_cache


def update_counter(counter_dict, ts):
    """
    根据时间戳ts(TimeStamp类型)更新计数字典counter_dict，可能是join字典，也可能是exit字典
    :param counter_dict: 待更新的join_counters或exit_counters
    :param ts: TimeStamp类型时间戳，用于向字典插入键
    :return:
    """
    # 与dict.get()相比，setdefault()在ts的内容已存在时不做改动，若尚未存在，则加入该键值对
    counter_dict.setdefault(ts, 0)
    # 在相同时间，每加入/退出一位玩家，time_stamp映射的值自增1
    counter_dict[ts] += 1
    return
