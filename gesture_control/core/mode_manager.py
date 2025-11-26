"""
模式管理器 - 管理模式切换
"""

import time
from ..config import PALM_HOLD_TIME
from ..core.gestures import GestureType
from ..modes.video_mode import VideoMode
from ..modes.scroll_mode import ScrollMode
from ..modes.mouse_mode import MouseMode


class ModeManager:
    """模式管理器，处理模式切换逻辑"""

    SWITCH_HOLD_TIME = 1.5  # 切换模式需要保持的时间

    def __init__(self):
        self.modes = [
            VideoMode(),
            ScrollMode(),
            MouseMode(),
        ]
        self.current_mode_index = 0
        self.palm_start_time = None

    @property
    def current_mode(self):
        """获取当前模式"""
        return self.modes[self.current_mode_index]

    def check_mode_switch(self, gesture: GestureType) -> dict:
        """检查是否需要切换模式（在激活状态下张开手掌）"""
        result = {
            'menu_progress': 0,
            'switched_mode': False,
        }

        if gesture == GestureType.OPEN_PALM:
            if self.palm_start_time is None:
                self.palm_start_time = time.time()

            elapsed = time.time() - self.palm_start_time
            result['menu_progress'] = min(elapsed / self.SWITCH_HOLD_TIME, 1.0)

            if elapsed >= self.SWITCH_HOLD_TIME:
                self._switch_to_next_mode()
                self.palm_start_time = None
                result['switched_mode'] = True
        else:
            self.palm_start_time = None

        return result

    def _switch_to_next_mode(self):
        """切换到下一个模式"""
        self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)

    def set_frame_size(self, width, height):
        """设置画面尺寸"""
        for mode in self.modes:
            if hasattr(mode, 'set_frame_size'):
                mode.set_frame_size(width, height)

