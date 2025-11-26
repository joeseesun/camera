"""
滚动模式 - 用手掌上下移动控制页面滚动
"""

import time
import pyautogui
from .base_mode import BaseMode
from ..core.gestures import GestureType
from ..config import SCROLL_COOLDOWN


class ScrollMode(BaseMode):
    """滚动控制模式 - 手掌移动控制滚动"""

    def __init__(self):
        super().__init__(
            name="📜 滚动模式",
            description="手掌移动滚动"
        )
        self.last_scroll_time = 0
        self.last_action = ""
        self.last_palm_y = None
        self.frame_height = 480

    def set_frame_size(self, width, height):
        """设置画面尺寸"""
        self.frame_height = height

    def handle_gesture(self, gesture: GestureType, points: dict,
                       action_confirmed: bool = False) -> str:
        """处理手势，手掌上下移动控制滚动"""
        current_time = time.time()

        # 冷却检查
        if current_time - self.last_scroll_time < SCROLL_COOLDOWN:
            return ""

        action = ""

        # 张开手掌时，根据移动方向滚动
        if gesture == GestureType.OPEN_PALM and 'palm_y' in points:
            current_y = points['palm_y']

            if self.last_palm_y is not None:
                delta = current_y - self.last_palm_y

                if delta < -0.03:  # 手向上移动
                    pyautogui.scroll(3)
                    action = "⬆️ 向上滚动"
                    self.last_scroll_time = current_time
                elif delta > 0.03:  # 手向下移动
                    pyautogui.scroll(-3)
                    action = "⬇️ 向下滚动"
                    self.last_scroll_time = current_time

            self.last_palm_y = current_y
        else:
            self.last_palm_y = None

        if action:
            self.last_action = action

        return action

    def get_overlay_info(self) -> dict:
        """返回覆盖层信息"""
        return {
            'mode_name': self.name,
            'hints': [
                "🖐️ 手掌上移 → 向上滚动",
                "🖐️ 手掌下移 → 向下滚动",
            ],
            'last_action': self.last_action,
        }

