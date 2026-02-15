# 缓冲区大小，根据后续需求可调整
BUFFER_MAX_SIZE = 250


def init(cfg_listen):
    pass


def tail_log(log_path, file, buffer):
    """
    执行一次监听日志文件新增内容，返回新行
    :param log_path: 日志文件路径
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
        if len(buffer) > BUFFER_MAX_SIZE:
            buffer.popleft()
        # 打印示例输出
        print(f"读取到日志行: {line}")

        return line
    except FileNotFoundError:
        print(f"log files not found: {log_path}")
    except Exception as e:
        print(f"errors occurred when listening: {e}")
