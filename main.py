import time
from collections import deque
from cfloader import loadcf, Config, RuntimeCfg, ListenCfg, ProcessCfg, ExecuteCfg
import listen
import process
import execute

"""
读取配置并初始化
思路：loadcf()后，在main中构造processcfg, listencfg, executecfg类，并以其为对象构造appcfg类
随后在各模块中定义初始化函数init()，并在main中调用，将需要的配置参数由main向外分发
"""
config = loadcf()
cfg = Config(
    runtime=RuntimeCfg(
        LOG_PATH=config['paths']['GAME_LOG_PATH'],
        DodgeWhenEnterRecentQueue=config['toggles']['DodgeWhenEnterRecentQueue'],
        DodgeWhenPartyExit=config['toggles']['DodgeWhenPartyExit']
    ),
    listen=ListenCfg(

    ),
    process=ProcessCfg(
        USER_NAME=config['player']['USER_NAME'],
        IsUserInParty=config['toggles']['IsUserInParty'],
        RECENT_QUEUE_RECORD=config['capacities']['RECENT_QUEUE_RECORD']
    ),
    execute=ExecuteCfg(
        AutoRequeue=config['toggles']['AutoRequeue']
    )
)


# 待初始化的运行时配置
log_path = ''
dodge_when_enter_recent_queue = False
dodge_when_party_exit = False


def init(cfg_runtime):
    """主程序配置初始化，并将配置向各模块分发"""
    # 初始化运行时配置
    global log_path, dodge_when_enter_recent_queue, dodge_when_party_exit
    log_path = cfg_runtime.LOG_PATH
    dodge_when_enter_recent_queue = cfg_runtime.DodgeWhenEnterRecentQueue
    dodge_when_party_exit = cfg_runtime.DodgeWhenPartyExit
    # 向各模块分发注入配置
    listen.init(cfg.listen)
    process.init(cfg.process)
    execute.init(cfg.execute)


def handle_trigger(counter_dict, ts, queue_json_obj):
    """在main()中抽象出execute.trigger及其副作用"""
    # 一旦dodge_execute()激活，立刻退出待命，避免重复/lobby
    if execute.trigger(counter_dict, ts):
        process.waiting_for_game = False
        print("AutoDodge Off Guard")
        if execute.requeue_execute(queue_json_obj):
            print("AutoRequeue Executed")
    return


def handle_recent_server_trigger(queue_json_obj, *counters: dict):
    """
    接收到process.maintain_blocked_server()的逃逸信号后执行逃逸或再加入
    :param queue_json_obj: 用于传递给requeue_execute()
    :param counters: 待清空的计数字典
    :return:
    """
    print("Recently Exited Queue Detected")
    for counter in counters:
        counter.clear()
    execute.dodge_execute()
    process.waiting_for_game = False
    print("AutoDodge Off Guard")
    if execute.requeue_execute(queue_json_obj):
        print("AutoRequeue Executed")
    return


def main():
    init(cfg.runtime)
    try:
        log_buffer = deque()
        process.blocked_server.clear()
        with open(log_path, 'r', encoding="utf-8", errors="ignore") as f:
            # 从日志最新一行读取，要求seek()第二参数为2
            f.seek(0, 2)
            ts_cache = None
            queue_json_obj = {"server": "", "gametype": "BEDWARS", "mode": "", "map": ""}
            while True:
                # 监听最新一行日志
                line = listen.tail_log(log_path, f, log_buffer)
                if not line:
                    time.sleep(0.2)
                    continue
                # 更新waiting_for_game，初始化join_counters，若进入排队返回这个等待大厅的信息
                queue_obj_cache, queue_obj_update = process.process_line(line)
                if queue_obj_update:
                    queue_json_obj = queue_obj_cache
                    # 记录近期加入的排队，若再次加入且开关打开，执行逃逸操作
                    if dodge_when_enter_recent_queue and process.maintain_blocked_server(queue_json_obj):
                        handle_recent_server_trigger(queue_json_obj, process.join_counters, process.exit_counters)
                # waiting_for_game=True，进入待命状态
                if process.waiting_for_game:
                    # 获取时间戳
                    ts_enter_raw, ts_exit_raw, exempt_signal = process.get_time(line)
                    time_stamp_enter, ts_cache = process.maintain_ts(ts_enter_raw, ts_cache, exempt_signal)
                    time_stamp_exit, ts_cache = process.maintain_ts(ts_exit_raw, ts_cache, exempt_signal)
                    if not (time_stamp_enter or time_stamp_exit):
                        time.sleep(0.2)
                        continue
                    if time_stamp_enter:
                        process.update_counter(process.join_counters, time_stamp_enter)
                        handle_trigger(process.join_counters, time_stamp_enter, queue_json_obj)
                    elif time_stamp_exit and dodge_when_party_exit:
                        process.update_counter(process.exit_counters, time_stamp_exit)
                        handle_trigger(process.exit_counters, time_stamp_exit, queue_json_obj)
    finally:
        f.close()


if __name__ == '__main__':
    main()
