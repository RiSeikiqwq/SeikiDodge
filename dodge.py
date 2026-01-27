import time
import pyautogui
import re


def dodge_execute():
    """
    代替玩家在 Minecraft 游戏中输入 /lobby 并按回车
    """
    try:
        # 暂停一下以确保 Minecraft 窗口已经是活动状态
        time.sleep(0.5)
        # 打开聊天框（Minecraft 默认聊天键为 “t”）
        pyautogui.press("/")
        time.sleep(0.02)
        # 输入要执行的命令
        pyautogui.write("lobby bedwars", interval=0.01)
        time.sleep(0.02)
        # 按下回车发送
        pyautogui.press("enter")
        return 1
    except Exception:
        return


def get_time(line):
    """
    从日志每行开头[hh:mm:ss]格式中获取时间戳
    :param line: listen模块监听到的单行日志
    :return (timestamp_enter, timestamp_exit): 时间戳字符串'hh:mm:ss'，以备向process.join/exit_counters输入键
    """
    try:
        # re.match方法返回Match对象，在line开头匹配形如[hh:mm:ss]格式内容
        ts_match = re.match(r"\[{1}(\d{2}:\d{2}:\d{2})\]", line)
        if ts_match and "has joined" in line:
            # Match对象group方法，参数0返回整个匹配对象，1返回被（）包裹的'hh:mm:ss'
            timestamp_enter = ts_match.group(1)
            timestamp_exit = ""
        elif ts_match and "has quit" in line:
            timestamp_exit = ts_match.group(1)
            timestamp_enter = ""
        else:
            timestamp_enter, timestamp_exit = "", ""
        return timestamp_enter, timestamp_exit
    except Exception:
        print(f"errors occurred when getting time stamp")


def trigger(counters, time_stamp):
    if counters.get(time_stamp, 0) >= 4:
        dodge_execute()
        print(f"Dodge Executed")
        # 清空计数防止重新触发
        counters.clear()
        return True
    else:
        return
