"""
ADB 自动翻页脚本
- 自动检测设备连接
- 每 5-10s 随机向下滑动一次
"""

import subprocess
import time
import random
import sys
import io

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
    for line in lines[1:]:  # 跳过标题行
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return True
    return False


def swipe_down():
    """向下滑动"""
    run_adb(["shell", "input", "swipe", "540", "1500", "540", "500", "300"])


def wait_for_device():
    """等待设备连接"""
    print("等待 ADB 设备连接...", flush=True)
    while True:
        if is_device_connected():
            print("设备已连接 ✓", flush=True)
            return
        time.sleep(3)


def main():
    wait_for_device()

    swipe_count = 0

    while True:
        # 检查设备是否还在
        if not is_device_connected():
            print("设备断开，等待重新连接...", flush=True)
            wait_for_device()

        # 执行滑动
        swipe_down()
        swipe_count += 1
        print(f"[滑动 #{swipe_count}]", flush=True)

        # 随机等待 5-10 秒
        wait = random.uniform(5, 10)
        print(f"  等待 {wait:.1f}s...", flush=True)
        time.sleep(wait)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已停止")
        sys.exit(0)
