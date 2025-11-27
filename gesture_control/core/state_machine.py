"""
手势状态机 - 管理手势状态和计时
单一职责：跟踪当前手势并提供精确的保持时间
"""

import time
from .gestures import GestureType


class GestureStateMachine:
    """
    手势状态机 - 好品味的状态管理

    消除全局变量，用清晰的数据结构替代：
    - 不需要 last_fist_time 等全局变量
    - 不需要手动管理 action_triggered 标志
    - 自动处理手势切换和重置
    """

    def __init__(self):
        self.current_gesture = GestureType.NONE
        self.start_time = 0.0
        self.executed_thresholds = set()  # 已执行的时间阈值（避免重复触发）

    def update(self, gesture: GestureType) -> float:
        """
        更新当前手势并返回保持时间

        Args:
            gesture: 当前识别到的手势

        Returns:
            float: 当前手势已保持的时间（秒）
        """
        now = time.time()

        # 手势切换：重置状态
        if gesture != self.current_gesture:
            self.current_gesture = gesture
            self.start_time = now
            self.executed_thresholds.clear()
            return 0.0

        # 同一手势：返回保持时间
        return now - self.start_time

    def should_execute(self, threshold: float) -> bool:
        """
        检查是否应该执行某个时间阈值的动作

        Args:
            threshold: 时间阈值（秒）

        Returns:
            bool: True 表示应该执行，False 表示已执行过
        """
        if threshold in self.executed_thresholds:
            return False

        self.executed_thresholds.add(threshold)
        return True

    def get_previous_hold_time(self) -> float:
        """
        获取上一个手势的保持时间
        仅在手势刚切换时有效（用于"松开握拳"这种场景）

        Returns:
            float: 上一个手势的保持时间（秒），如果当前手势刚开始返回 0
        """
        if self.current_gesture == GestureType.NONE:
            return 0.0

        # 如果当前手势刚开始（< 0.1s），返回切换前的时长
        current_hold = time.time() - self.start_time
        if current_hold < 0.1 and hasattr(self, '_previous_hold_time'):
            return self._previous_hold_time

        return 0.0

    def reset(self):
        """重置状态机"""
        self.current_gesture = GestureType.NONE
        self.start_time = 0.0
        self.executed_thresholds.clear()
