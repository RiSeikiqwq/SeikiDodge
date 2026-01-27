import time
from collections import deque
from cfloader import loadcf
import listen
import process
import dodge


config = loadcf()
# 玩家用户名，传参process.process_line()，作为进入待命状态信号，大小写敏感
USER_NAME = config['player']['USER_NAME']
# minecraft游戏本体日志路径
LOG_PATH = config['paths']['GAME_LOG_PATH']
# 不仅在车队进入时Dodge，在车队集体退出时也触发Dodge，注意在json中填true/false
DodgeWhenPartyExit = config['toggles']['DodgeWhenPartyExit']
# 用户本人是否在组队中，若是，则用户加入该秒豁免检测
UserIsInParty = config['toggles']['UserIsInParty']


def main():
    try:
        log_buffer = deque()
        with open(LOG_PATH, 'r', encoding="utf-8", errors="ignore") as f:
            # 从日志最新一行读取，要求seek()第二参数为2
            f.seek(0, 2)
            ts_cache = None
            while True:
                # 监听最新一行日志
                line = listen.tail_log(LOG_PATH, f, log_buffer)
                if not line:
                    time.sleep(0.2)
                    continue
                # 更新waiting_for_game，初始化join_counters
                process.process_line(line, USER_NAME)
                # waiting_for_game=True，进入待命状态
                if process.waiting_for_game:
                    # 获取时间戳
                    ts_enter_raw, ts_exit_raw, exempt_signal = process.get_time(line, USER_NAME, UserIsInParty)
                    time_stamp_enter, ts_cache = process.maintain_ts(ts_enter_raw, ts_cache, exempt_signal)
                    time_stamp_exit, ts_cache = process.maintain_ts(ts_exit_raw, ts_cache, exempt_signal)
                    if not (time_stamp_enter or time_stamp_exit):
                        time.sleep(0.2)
                        continue
                    if time_stamp_enter:
                        # 与dict.get()相比，setdefault()在time_stamp已存在时不做改动，若尚未存在，则加入该键值对
                        process.join_counters.setdefault(time_stamp_enter, 0)
                        # 在相同时间，每加入一位玩家，time_stamp映射的值自增1
                        process.join_counters[time_stamp_enter] += 1
                        # 一旦dodge_execute()激活，立刻退出待命，避免重复/lobby
                        if dodge.trigger(process.join_counters, time_stamp_enter):
                            process.waiting_for_game = False
                            print("AutoDodge Off Guard")
                    elif time_stamp_exit and DodgeWhenPartyExit:
                        process.exit_counters.setdefault(time_stamp_exit, 0)
                        process.exit_counters[time_stamp_exit] += 1
                        if dodge.trigger(process.exit_counters, time_stamp_exit):
                            process.waiting_for_game = False
                            print("AutoDodge Off Guard")
    finally:
        f.close()


if __name__ == '__main__':
    main()
