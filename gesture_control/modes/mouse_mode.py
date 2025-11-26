"""
鼠标模式 - 用 ✌️ 两指控制鼠标
"""

import time
import pyautogui
from .base_mode import BaseMode
from ..core.gestures import GestureType
from ..config import ACTION_COOLDOWN

# 禁用 pyautogui 的安全限制
pyautogui.FAILSAFE = False


class MouseMode(BaseMode):
    """鼠标控制模式 - ✌️两指控制光标，握拳点击"""

    def __init__(self):
        super().__init__(
            name="🖱️ 鼠标模式",
            description="两指控制鼠标"
        )
        self.last_click_time = 0
        self.last_action = ""
        self.screen_width, self.screen_height = pyautogui.size()
        self.frame_width = 640
        self.frame_height = 480
        self.smoothing = 0.25
        self.last_x = None
        self.last_y = None
        self.was_peace = False  # 上一帧是否是 ✌️

    def set_frame_size(self, width, height):
        """设置摄像头画面尺寸"""
        self.frame_width = width
        self.frame_height = height

    def handle_gesture(self, gesture: GestureType, points: dict,
                       action_confirmed: bool = False) -> str:
        """处理手势，控制鼠标"""
        current_time = time.time()
        action = ""

        # ✌️ 两指移动鼠标
        if gesture == GestureType.PEACE and 'index_x' in points:
            self._move_mouse(points['index_x'], points['index_y'])
            self.was_peace = True
            action = "🖱️ 移动中"

        # ✌️→✊ 两指收拢成拳 = 点击
        elif gesture == GestureType.FIST and self.was_peace:
            if current_time - self.last_click_time >= ACTION_COOLDOWN:
                pyautogui.click()
                self.last_click_time = current_time
                action = "🖱️ 点击!"
                self.last_action = action
            self.was_peace = False

        else:
            self.was_peace = False
            self.last_x = None
            self.last_y = None

        return action

    def _move_mouse(self, finger_x, finger_y):
        """将手指位置映射到屏幕坐标"""
        screen_x = int((1 - finger_x / self.frame_width) * self.screen_width)
        screen_y = int((finger_y / self.frame_height) * self.screen_height)

        # 平滑处理
        if self.last_x is not None:
            screen_x = int(self.last_x + (screen_x - self.last_x) * self.smoothing)
            screen_y = int(self.last_y + (screen_y - self.last_y) * self.smoothing)

        self.last_x = screen_x
        self.last_y = screen_y

        screen_x = max(0, min(screen_x, self.screen_width - 1))
        screen_y = max(0, min(screen_y, self.screen_height - 1))

        pyautogui.moveTo(screen_x, screen_y)

    def get_overlay_info(self) -> dict:
        """返回覆盖层信息"""
        return {
            'mode_name': self.name,
            'hints': [
                "✌️ 两指 → 移动鼠标",
                "✌️→✊ 收拢 → 点击",
            ],
            'last_action': self.last_action,
        }

