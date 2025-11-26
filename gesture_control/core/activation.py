"""
激活状态管理器 - 控制手势识别的激活/待机状态
"""

import time
from ..core.gestures import GestureType
from ..config import CLAP_HOLD_TIME


class ActivationManager:
    """管理激活状态，减少误触发"""

    ACTIVATION_TIME = 1.5      # 张开手掌激活所需时间（1.5秒）
    DEACTIVATION_TIME = 3.0    # 手离开后自动退出时间
    COOLDOWN_TIME = 0.3        # 激活后的冷却时间
    ACTION_HOLD_TIME = 0.5     # 动作需要保持的时间

    def __init__(self):
        self.is_activated = False
        self.palm_start_time = None
        self.hand_lost_time = None
        self.activation_time = None
        self.need_release = False
        self.action_start_time = None
        self.current_action_gesture = None
        self.action_triggered = False  # 是否已触发动作（防连续触发）

    def update(self, has_hand: bool, gesture: GestureType) -> dict:
        """
        更新激活状态

        Args:
            has_hand: 是否检测到手
            gesture: 当前手势类型

        Returns:
            dict: 激活状态信息
        """
        current_time = time.time()
        is_open_palm = gesture == GestureType.OPEN_PALM

        result = {
            'activated': self.is_activated,
            'activation_progress': 0,
            'just_activated': False,
            'ready_for_action': False,  # 是否可以执行动作
        }

        if not has_hand:
            self.palm_start_time = None
            self.need_release = False

            if self.is_activated:
                if self.hand_lost_time is None:
                    self.hand_lost_time = current_time
                elif current_time - self.hand_lost_time >= self.DEACTIVATION_TIME:
                    self.is_activated = False
                    self.hand_lost_time = None

            result['activated'] = self.is_activated
            return result

        self.hand_lost_time = None

        if not self.is_activated:
            # 未激活：检测单手张开激活（3秒）
            if is_open_palm:
                if self.palm_start_time is None:
                    self.palm_start_time = current_time

                elapsed = current_time - self.palm_start_time
                result['activation_progress'] = min(elapsed / self.ACTIVATION_TIME, 1.0)

                if elapsed >= self.ACTIVATION_TIME:
                    self.is_activated = True
                    self.activation_time = current_time
                    self.need_release = True  # 需要先收手才能操作
                    self.palm_start_time = None
                    result['just_activated'] = True
            else:
                self.palm_start_time = None
        else:
            # 已激活：检查是否可以执行动作
            if self.need_release:
                # 需要先收手（不是张开手掌）才能开始操作
                if not is_open_palm:
                    self.need_release = False
            else:
                result['ready_for_action'] = True

        result['activated'] = self.is_activated
        return result

    def check_action_hold(self, gesture_type) -> bool:
        """检查握拳等动作是否保持足够时间"""
        if gesture_type == GestureType.NONE:
            self.current_action_gesture = None
            self.action_start_time = None
            return False

        current_time = time.time()

        if gesture_type != self.current_action_gesture:
            self.current_action_gesture = gesture_type
            self.action_start_time = current_time
            return False

        if current_time - self.action_start_time >= self.ACTION_HOLD_TIME:
            self.action_start_time = current_time
            return True

        return False

    def get_action_progress(self, gesture_type) -> float:
        """获取当前动作的保持进度"""
        if gesture_type != self.current_action_gesture or not self.action_start_time:
            return 0
        elapsed = time.time() - self.action_start_time
        return min(elapsed / self.ACTION_HOLD_TIME, 1.0)

    def get_hold_time(self, gesture_type) -> float:
        """获取当前手势已保持的时间（秒）"""
        if gesture_type != self.current_action_gesture or not self.action_start_time:
            # 新手势，开始计时
            self.current_action_gesture = gesture_type
            self.action_start_time = time.time()
            self.action_triggered = False
            return 0
        return time.time() - self.action_start_time

    def reset_action(self):
        """重置动作状态"""
        self.action_start_time = None
        self.current_action_gesture = None
        self.action_triggered = False

