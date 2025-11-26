"""
全局状态窗口 - 显示激活状态的小窗口
"""

import cv2
import numpy as np


class GlobalOverlay:
    """全局状态指示器 - 小窗口显示"""

    WINDOW_NAME = "Status"
    WIDTH = 280
    HEIGHT = 100

    def __init__(self):
        self.activated = False
        self.mode = ""
        self.action = ""
        self.progress = 0
        self.frame = None

    def start(self):
        """创建状态窗口"""
        cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.WINDOW_NAME, self.WIDTH, self.HEIGHT)
        # 移动到屏幕右上角
        cv2.moveWindow(self.WINDOW_NAME, 1100, 50)
        self._render()

    def stop(self):
        """关闭窗口"""
        try:
            cv2.destroyWindow(self.WINDOW_NAME)
        except:
            pass

    def update(self, activated: bool, mode: str = "", action: str = "", progress: float = 0):
        """更新状态并重绘"""
        self.activated = activated
        self.mode = mode
        self.action = action
        self.progress = progress
        self._render()

    def _render(self):
        """渲染状态窗口"""
        # 创建画布
        if self.progress > 0:
            bg_color = (0, 140, 255)  # 橙色 - 激活中
        elif self.activated:
            bg_color = (80, 200, 80)  # 绿色 - 已激活
        else:
            bg_color = (60, 60, 60)   # 灰色 - 未激活

        self.frame = np.full((self.HEIGHT, self.WIDTH, 3), bg_color, dtype=np.uint8)

        font = cv2.FONT_HERSHEY_SIMPLEX

        if self.progress > 0:
            # 激活进度
            text = "Activating..."
            cv2.putText(self.frame, text, (15, 35), font, 0.7, (255, 255, 255), 2)
            # 进度条
            bar_x, bar_y = 15, 55
            bar_w, bar_h = 250, 20
            cv2.rectangle(self.frame, (bar_x, bar_y),
                         (bar_x + bar_w, bar_y + bar_h), (255, 255, 255), 2)
            fill_w = int(bar_w * self.progress)
            cv2.rectangle(self.frame, (bar_x, bar_y),
                         (bar_x + fill_w, bar_y + bar_h), (255, 255, 255), -1)

        elif self.activated:
            # 已激活状态
            cv2.putText(self.frame, self.mode, (15, 35), font, 0.7, (255, 255, 255), 2)
            if self.action:
                cv2.putText(self.frame, self.action, (15, 70), font, 0.6, (255, 255, 255), 2)
            else:
                cv2.putText(self.frame, "Ready", (15, 70), font, 0.6, (200, 200, 200), 1)
        else:
            # 未激活
            cv2.putText(self.frame, "Show Palm", (15, 40), font, 0.8, (255, 255, 255), 2)
            cv2.putText(self.frame, "to activate", (15, 75), font, 0.6, (180, 180, 180), 1)

        cv2.imshow(self.WINDOW_NAME, self.frame)

