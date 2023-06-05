from concurrent.futures import ProcessPoolExecutor
from threading import Thread

# 独自モジュール
from .data_formatter import DataFormatter
from .live_chat_downloader import LiveChatDownloader
from .analyzer_ui import AnalyzerUi
from .gpt_handler import チャットGPTハンドラークラス



def main_process(live_id: str, gpt_handler:チャットGPTハンドラークラス):
    AnalyzerUi(gpt_handler, live_id)

    # プロセスを作成
    executor = ProcessPoolExecutor(max_workers=2)

    # プロセスを開始（別スレッドで実行）
    data_formatter = DataFormatter(live_id, gpt_handler)
    live_chat_downloader = LiveChatDownloader(live_id)

    t1 = Thread(target=lambda: executor.submit(data_formatter.replace_watch_comment))
    t1.start()

    t2 = Thread(target=lambda: executor.submit(live_chat_downloader.get_chat))
    t2.start()