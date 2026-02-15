# 待初始化配置
buffer_max_size = 0


def init(cfg_listen):
    """接收main分发的listen配置"""
    global buffer_max_size
    buffer_max_size = cfg_listen.LISTEN_BUFFER


def tail_log(log_path: str, file, buffer):
    """
    执行一次监听日志文件新增内容，返回新行
    :param buffer: 缓冲区，在main中声明并传入该函数(deque)
    :param file: 打开日志生成的文件实例(TextIO)
    :param log_path: 日志文件路径(str)
    :return line: f.readline对象
    """
    try:
        line = file.readline()
        if not line:
            return
        # 去除换行符
        line = line.rstrip("\n")

        # 将读取的一行内容追加到缓冲区
        buffer.append(line)
        # 若缓冲区过大，则丢弃最旧的数据
        if len(buffer) > buffer_max_size:
            buffer.popleft()
        # 打印示例输出
        print(f"读取到日志行: {line}")

        return line
    except FileNotFoundError:
        print(f"log files not found: {log_path}")
    except Exception as e:
        print(f"errors occurred when listening: {e}")
