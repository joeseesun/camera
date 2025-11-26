"""
视频模式 - 控制 YouTube / B站 等视频播放
"""

import time
import pyautogui
from .base_mode import BaseMode
from ..core.gestures import GestureType
from ..config import ACTION_COOLDOWN, VIDEO_SEEK_TIMES


class VideoMode(BaseMode):
    """视频控制模式"""

    def __init__(self):
        super().__init__(
            name="📺 视频模式",
            description="控制视频播放"
        )
        self.last_action_time = 0
        self.last_action = ""

    def handle_gesture(self, gesture: GestureType, points: dict,
                       action_confirmed: bool = False) -> str:
        """
        处理手势，执行视频控制

        Args:
            gesture: 手势类型
            points: 手势坐标
            action_confirmed: 是否已确认动作（保持足够时间）
        """
        current_time = time.time()

        # 冷却检查
        if current_time - self.last_action_time < ACTION_COOLDOWN:
            return ""

        action = ""

        if not action_confirmed:
            return ""

        # ✊ 握拳 → 播放/暂停
        if gesture == GestureType.FIST:
            pyautogui.press('space')
            action = "⏯️ 播放/暂停"

        # ☝️ 单指 → 快退20秒
        elif gesture == GestureType.POINTING:
            pyautogui.press('left')
            pyautogui.press('left')
            pyautogui.press('left')
            pyautogui.press('left')
            action = "⏪ 快退 20s"

        # ✌️ 双指 → 快进20秒
        elif gesture == GestureType.PEACE:
            pyautogui.press('right')
            pyautogui.press('right')
            pyautogui.press('right')
            pyautogui.press('right')
            action = "⏩ 快进 20s"

        if action:
            self.last_action_time = current_time
            self.last_action = action

        return action

    def play_pause(self) -> str:
        """播放/暂停"""
        pyautogui.press('space')
        self.last_action = "⏯️ 播放/暂停"
        return self.last_action

    def fullscreen(self) -> str:
        """全屏切换"""
        pyautogui.press('f')
        self.last_action = "🖥️ 全屏"
        return self.last_action

    def get_overlay_info(self) -> dict:
        """返回覆盖层信息"""
        return {
            'mode_name': self.name,
            'hints': [
                "✊ 握拳 → 暂停",
                "☝️ 单指 → 快退20s",
                "✌️ 双指 → 快进20s",
            ],
            'last_action': self.last_action,
        }

