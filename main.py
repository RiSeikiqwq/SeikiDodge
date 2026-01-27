import time
from collections import deque
import listen
import process
import dodge


def main():
    try:
        log_buffer = deque()
        with open(listen.LOG_PATH, 'r', encoding="utf-8", errors="ignore") as f:
            # 从日志最新一行读取，要求seek()第二参数为2
            f.seek(0, 2)
            while True:
                # print(process.waiting_for_game) 调试用
                # 监听最新一行日志
                line = listen.tail_log(listen.LOG_PATH, f, log_buffer)
                if not line:
                    time.sleep(0.2)
                    continue
                # 更新waiting_for_game，初始化join_counters
                process.process_line(line)
                # waiting_for_game=True，进入待命状态
                if process.waiting_for_game:
                    # 获取时间戳
                    time_stamp_enter, time_stamp_exit = dodge.get_time(line)
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
                    elif time_stamp_exit:
                        process.exit_counters.setdefault(time_stamp_exit, 0)
                        process.exit_counters[time_stamp_exit] += 1
                        if dodge.trigger(process.exit_counters, time_stamp_exit):
                            process.waiting_for_game = False
                            print("AutoDodge Off Guard")
    finally:
        f.close()


if __name__ == '__main__':
    main()
