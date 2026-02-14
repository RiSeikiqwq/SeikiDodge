import time
from collections import deque
from cfloader import loadcf
import listen
import process
import execute


config = loadcf()
# 玩家用户名，传参process.process_line()，作为进入待命状态信号，大小写敏感
USER_NAME = config['player']['USER_NAME']
# minecraft游戏本体日志路径
LOG_PATH = config['paths']['GAME_LOG_PATH']
# 逃逸后立即加入下一场游戏
AutoRequeue = config['toggles']['AutoRequeue']
# 将最近加入的排队列入黑名单，下次加入时自动逃逸
DodgeWhenEnterRecentQueue = config['toggles']['DodgeWhenEnterRecentQueue']
# 不仅在车队进入时Dodge，在车队集体退出时也触发Dodge
DodgeWhenPartyExit = config['toggles']['DodgeWhenPartyExit']
# 用户本人是否在组队中，若是，则用户加入该秒豁免检测
IsUserInParty = config['toggles']['IsUserInParty']


def handle_trigger(counter_dict, ts, queue_json_obj):
    """
    在main()中抽象出execute.trigger及其副作用
    """
    # 一旦dodge_execute()激活，立刻退出待命，避免重复/lobby
    if execute.trigger(counter_dict, ts):
        process.waiting_for_game = False
        print("AutoDodge Off Guard")
        if execute.requeue_execute(queue_json_obj, AutoRequeue):
            print("AutoRequeue Executed")
    return


def handle_recent_server_trigger(queue_json_obj, AutoRequeue, *counters: dict):
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
    if execute.requeue_execute(queue_json_obj, AutoRequeue):
        print("AutoRequeue Executed")
    return


def main():
    try:
        log_buffer = deque()
        process.blocked_server.clear()
        with open(LOG_PATH, 'r', encoding="utf-8", errors="ignore") as f:
            # 从日志最新一行读取，要求seek()第二参数为2
            f.seek(0, 2)
            ts_cache = None
            queue_json_obj = {"server": "", "gametype": "BEDWARS", "mode": "", "map": ""}
            while True:
                # 监听最新一行日志
                line = listen.tail_log(LOG_PATH, f, log_buffer)
                if not line:
                    time.sleep(0.2)
                    continue
                # 更新waiting_for_game，初始化join_counters，若进入排队返回这个等待大厅的信息
                queue_obj_cache, queue_obj_update = process.process_line(line, USER_NAME)
                if queue_obj_update:
                    queue_json_obj = queue_obj_cache
                    # 记录近期加入的排队，若再次加入且开关打开，执行逃逸操作
                    if DodgeWhenEnterRecentQueue and process.maintain_blocked_server(queue_json_obj, process.blocked_server):
                        handle_recent_server_trigger(queue_json_obj, AutoRequeue, process.join_counters, process.exit_counters)
                # waiting_for_game=True，进入待命状态
                if process.waiting_for_game:
                    # 获取时间戳
                    ts_enter_raw, ts_exit_raw, exempt_signal = process.get_time(line, USER_NAME, IsUserInParty)
                    time_stamp_enter, ts_cache = process.maintain_ts(ts_enter_raw, ts_cache, exempt_signal)
                    time_stamp_exit, ts_cache = process.maintain_ts(ts_exit_raw, ts_cache, exempt_signal)
                    if not (time_stamp_enter or time_stamp_exit):
                        time.sleep(0.2)
                        continue
                    if time_stamp_enter:
                        process.update_counter(process.join_counters, time_stamp_enter)
                        handle_trigger(process.join_counters, time_stamp_enter, queue_json_obj)
                    elif time_stamp_exit and DodgeWhenPartyExit:
                        process.update_counter(process.exit_counters, time_stamp_exit)
                        handle_trigger(process.exit_counters, time_stamp_exit, queue_json_obj)
    finally:
        f.close()


if __name__ == '__main__':
    main()
