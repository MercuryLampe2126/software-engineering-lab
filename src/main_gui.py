import sys
import os

# 将项目根目录加入 python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    # 设置简单的样式
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()