import json

# 玩家用户名，用于进入待命状态，注意大小写敏感
USER_NAME = 'PirateZY_Li'
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
        # 解析 JSON
        obj = json.loads(json_str)
        if isinstance(obj, dict):
            return obj

    except json.JSONDecodeError:
        return None


def process_line(line):
    """
    分析单条日志行，更新waiting_for_game，初始化join_counters
    当<本玩家> has joined，进入待命状态
    当进入bedwars大厅，服务器发送大厅json信息，退出待命状态
    :return:
    """
    global waiting_for_game, join_counters
    if USER_NAME + ' has joined' in line:
        waiting_for_game = True
        join_counters.clear()
        exit_counters.clear()
        print("AutoDodge Standby")
    json_obj = parse_json_line(line)
    if json_obj:
        # 例如 {"server":"minixx","gametype":"BEDWARS","mode":"...","map":"..."}
        if json_obj.get("gametype") == "BEDWARS" and "mode" in json_obj and "map" in json_obj:
            pass
        # 例如 {"server":"dynamiclobbyxx","gametype":"BEDWARS","lobbyname":"..."}
        elif json_obj.get("gametype") == "BEDWARS" and "lobbyname" in json_obj:
            # 除初始化作用外，与main()中激活dodge_execute()即退出待命的设计互为补充
            waiting_for_game = False
            join_counters.clear()
            exit_counters.clear()
            print("AutoDodge Off Guard")
