import time
import pyautogui


# 待初始化的execute配置
auto_requeue = False


def init(cfg_execute):
    """接收main分发的execute配置"""
    global auto_requeue
    auto_requeue = cfg_execute.AutoRequeue


def dodge_execute():
    """代替玩家在游戏中输入/lobby并按回车"""
    try:
        # 暂停一下以确保 Minecraft 窗口已经是活动状态
        time.sleep(0.5)
        # 打开聊天框（Minecraft 默认聊天键为 “t”）
        pyautogui.press("/")
        time.sleep(0.01)
        # 输入要执行的命令
        pyautogui.write("lobby bedwars", interval=0.01)
        time.sleep(0.02)
        # 按下回车发送
        pyautogui.press("enter")
        return 1
    except Exception:
        return


def requeue_execute(queue_json_obj):
    """
    代替玩家自动执行/play bedwars_<mode>
    :param queue_json_obj: 上一局的游戏信息，存储房间号/模式/地图(dict)
    :return:
    """
    # pattern: 'BEDWARS_<teams>_<member_num>'
    raw_current_mode = queue_json_obj.get('mode')
    requeue_command = 'play ' + raw_current_mode
    try:
        if auto_requeue:
            time.sleep(0.4)
            pyautogui.press("/")
            time.sleep(0.01)
            pyautogui.write(requeue_command, interval=0.01)
            time.sleep(0.02)
            pyautogui.press("enter")
            return 1
        else:
            return
    except Exception:
        return


def trigger(counters, time_stamp):
    """
    判断同一时刻进入或退出玩家数，判断该时刻是否豁免，满足要求即触发AutoDodge
    :param counters: 存储 '时间戳':相应行为玩家数 的字典
    :param time_stamp: 时间戳，必须是TimeStamp对象，禁止传入str，其str内容用于键检索，exempt属性用于判断豁免
    :return: 若成功执行，更新process.waiting_for_game
    """
    if time_stamp is None:
        return False
    # 为防止传参非TimeStamp类型或缺失exempt参数，使用getattr()，在参数缺失时返回False
    if not getattr(time_stamp, 'exempt', False) and (counters.get(time_stamp, 0) >= 4):
        dodge_execute()
        print(f"Dodge Executed")
        # 清空计数防止重新触发
        counters.clear()
        return True
    else:
        return False
