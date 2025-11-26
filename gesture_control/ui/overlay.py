"""
UI 覆盖层 - 视觉反馈
"""

import cv2
from ..config import (
    COLOR_GREEN, COLOR_RED, COLOR_YELLOW, COLOR_WHITE,
    COLOR_MAGENTA, COLOR_CYAN,
    FONT_SCALE, FONT_THICKNESS,
)


class Overlay:
    """UI 覆盖层，提供视觉反馈"""

    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw(self, frame, mode_info, gesture_points, status):
        """绘制所有 UI 元素"""
        h, w = frame.shape[:2]
        activated = status.get('activated', False)

        # 激活状态边框
        if activated:
            cv2.rectangle(frame, (5, 5), (w-5, h-5), COLOR_GREEN, 3)
        else:
            # 未激活时显示激活进度
            progress = status.get('activation_progress', 0)
            if progress > 0:
                self._draw_activation_progress(frame, progress, w, h)
            else:
                cv2.putText(frame, "Show palm to activate", (10, 30),
                            self.font, 0.6, COLOR_WHITE, 2)
            return

        # 绘制模式名称
        self._draw_mode_name(frame, mode_info.get('mode_name', ''), w)

        # 绘制操作提示
        self._draw_hints(frame, mode_info.get('hints', []), h)

        # 绘制手指位置指示器
        if gesture_points and 'index_x' in gesture_points:
            self._draw_finger_indicator(
                frame, gesture_points['index_x'], gesture_points['index_y']
            )

        # 绘制模式切换进度
        if status.get('menu_progress', 0) > 0:
            self._draw_switch_progress(frame, status['menu_progress'], w, h)

    def _draw_activation_progress(self, frame, progress, w, h):
        """绘制激活进度"""
        bar_width = int(w * 0.6)
        bar_height = 25
        x = (w - bar_width) // 2
        y = h // 2

        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height),
                      COLOR_WHITE, 2)
        fill_width = int(bar_width * progress)
        cv2.rectangle(frame, (x, y), (x + fill_width, y + bar_height),
                      (0, 165, 255), -1)  # 橙色
        cv2.putText(frame, "Activating...", (x, y - 10),
                    self.font, 0.7, COLOR_WHITE, 2)

    def _draw_mode_name(self, frame, mode_name, width):
        """绘制当前模式名称"""
        cv2.putText(
            frame, mode_name, (10, 30),
            self.font, FONT_SCALE, COLOR_CYAN, FONT_THICKNESS
        )

    def _draw_hints(self, frame, hints, height):
        """绘制操作提示"""
        y = height - 20 - (len(hints) - 1) * 25
        for hint in hints:
            cv2.putText(
                frame, hint, (10, y),
                self.font, 0.5, COLOR_WHITE, 1
            )
            y += 25

    def _draw_finger_indicator(self, frame, x, y):
        """绘制手指位置指示器"""
        cv2.circle(frame, (x, y), 15, COLOR_MAGENTA, -1)

    def _draw_switch_progress(self, frame, progress, w, h):
        """绘制模式切换进度条"""
        bar_width = int(w * 0.6)
        bar_height = 20
        x = (w - bar_width) // 2
        y = h // 2

        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height),
                      COLOR_WHITE, 2)
        fill_width = int(bar_width * progress)
        cv2.rectangle(frame, (x, y), (x + fill_width, y + bar_height),
                      COLOR_GREEN, -1)
        cv2.putText(frame, "Switching mode...", (x, y - 10),
                    self.font, 0.6, COLOR_WHITE, 2)

