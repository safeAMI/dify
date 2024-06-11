import logging
import os

def setup_logging():
    # 获取当前工作目录
    current_dir = os.getcwd()
    log_file_path = os.path.join(current_dir, 'app.log')

    # 配置日志记录器
    logging.basicConfig(
        level=logging.DEBUG,  # 设置最低日志级别为 DEBUG
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 配置日志格式
        handlers=[
            logging.FileHandler(log_file_path),  # 将日志写入文件
        ]
    )

    # 记录日志消息
    logging.debug('这是一个调试信息')
    logging.info('这是一个信息')
    logging.warning('这是一个警告')
    logging.error('这是一个错误')
    logging.critical('这是一个严重错误')

    print(log_file_path)

if __name__ == '__main__':
    setup_logging()