import random
import time

def worker(file_name, test):
    with open(file_name, "w") as f:
        for _ in range(100):
            time.sleep(1)  # 1秒ごとに数値を書き出す
            f.write(str(random.randint(1, 10)) + "\n")
            f.flush()  # 追加: バッファをフラッシュして即座にファイルを更新
    return True
