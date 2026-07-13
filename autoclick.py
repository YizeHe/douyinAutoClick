"""
ADB 自动翻页脚本
- 自动检测设备连接
- 每 5-7s 随机向下滑动一次
- 每天 2:29-5:08 暂停并黑屏
"""

import subprocess
import time
import random
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def run_adb(args: list[str]) -> tuple[int, str]:
    """执行 adb 命令，返回 (returncode, output)"""
    cmd = ["adb"] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        return result.returncode, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return -1, ""


def is_device_connected() -> bool:
    """检查是否有设备在线"""
    _, output = run_adb(["devices"])
    lines = output.strip().splitlines()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return True
    return False


def swipe_down():
    """向下滑动"""
    run_adb(["shell", "input", "swipe", "540", "1500", "540", "500", "300"])


def screen_off():
    """关闭屏幕"""
    run_adb(["shell", "input", "keyevent", "26"])


def screen_on():
    """打开屏幕"""
    run_adb(["shell", "input", "keyevent", "26"])


def wait_for_device():
    """等待设备连接"""
    print("等待 ADB 设备连接...", flush=True)
    while True:
        if is_device_connected():
            print("设备已连接", flush=True)
            return
        time.sleep(3)


def is_sleep_time() -> bool:
    """判断当前是否在暂停时段 (2:29 - 5:08)"""
    now = datetime.now()
    t = now.hour * 60 + now.minute
    start = 2 * 60 + 29   # 2:29
    end = 5 * 60 + 8      # 5:08
    return start <= t < end


def wait_until_wake():
    """等待到 5:08 后唤醒"""
    print("[暂停] 进入休息时段 2:29-5:08，黑屏中...", flush=True)
    screen_off()
    while is_sleep_time():
        time.sleep(30)
    print("[恢复] 5:08 已到，亮屏继续", flush=True)
    screen_on()
    time.sleep(2)


def main():
    wait_for_device()

    swipe_count = 0

    while True:
        # 检查是否进入暂停时段
        if is_sleep_time():
            wait_until_wake()

        # 检查设备是否还在
        if not is_device_connected():
            print("设备断开，等待重新连接...", flush=True)
            wait_for_device()

        # 执行滑动
        swipe_down()
        swipe_count += 1
        print(f"[滑动 #{swipe_count}]", flush=True)

        # 随机等待 5-7 秒
        wait = random.uniform(5, 7)
        print(f"  等待 {wait:.1f}s...", flush=True)
        time.sleep(wait)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已停止")
        sys.exit(0)
