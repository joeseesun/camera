"""
激活状态管理器 - 控制手势识别的激活/待机状态

重构后：只负责激活/待机逻辑
手势计时和动作触发由 GestureStateMachine 和 Actions 处理
"""

import time
from ..core.gestures import GestureType


class ActivationManager:
    """
    管理激活状态，减少误触发

    单一职责：只管理 激活/待机 状态切换
    """

    ACTIVATION_TIME = 1.5      # 张开手掌激活所需时间（1.5秒）
    DEACTIVATION_TIME = 3.0    # 手离开后自动退出时间

    def __init__(self):
        self.is_activated = False
        self.palm_start_time = None
        self.hand_lost_time = None
        self.need_release = False  # 激活后需要先松手才能操作

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

