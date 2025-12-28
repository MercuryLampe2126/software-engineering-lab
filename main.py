# main.py
def say_hello():
    print("=" * 50)
    print("软件工程实验1：环境搭建")
    print("作者：[黎嘉麟]")
    print("学号：[2023150399]")
    print("=" * 50)

    # 展示系统信息
    import platform
    import sys

    print(f"\n系统信息：")
    print(f"Python版本：{sys.version}")
    print(f"操作系统：{platform.system()} {platform.release()}")

    # 计算演示
    print(f"\n计算演示：")
    numbers = list(range(1, 11))
    total = sum(numbers)
    average = total / len(numbers)

    print(f"1-10的数字：{numbers}")
    print(f"总和：{total}")
    print(f"平均值：{average:.2f}")

    print(f"\n✅ 环境配置成功！")
    print("可以开始软件工程课程设计了。")


if __name__ == "__main__":
    say_hello()