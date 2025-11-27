"""
手势动作系统 - 配置表驱动，消除 if-elif 地狱

好品味原则：
1. 数据结构优先 - 用配置表替代条件分支
2. 单一职责 - 每个 Action 类只做一件事
3. 可测试 - 所有动作逻辑独立，易于单元测试
"""

import pyautogui
from .gestures import GestureType


class GestureAction:
    """手势动作基类 - 统一接口"""

    def execute(self, hold_time: float, state_machine, points: dict) -> str:
        """
        执行手势动作

        Args:
            hold_time: 当前手势保持时间（秒）
            state_machine: GestureStateMachine 实例
            points: 手部关键点坐标

        Returns:
            str: 动作状态描述（用于 UI 显示）
        """
        raise NotImplementedError


class TimedAction(GestureAction):
    """
    时间触发动作 - 握拳 0.5s → 暂停，3s → 全屏

    配置示例：
        TimedAction([
            (0.5, 'space', 'Play/Pause'),
            (3.0, 'f', 'Fullscreen'),
        ])
    """

    def __init__(self, thresholds: list):
        """
        Args:
            thresholds: [(时间阈值, 按键, 描述), ...]
                       按键可以是字符串或可调用对象
        """
        self.thresholds = sorted(thresholds, key=lambda x: x[0])  # 按时间排序

    def execute(self, hold_time, state_machine, points):
        # 检查是否达到某个时间阈值
        for threshold, key, description in self.thresholds:
            if hold_time >= threshold:
                if state_machine.should_execute(threshold):
                    # 执行动作
                    if callable(key):
                        key()
                    else:
                        pyautogui.press(key)
                    return f"✓ {description}"
                else:
                    # 已执行过，显示完成状态
                    return f"✓ {description}"

        # 尚未达到任何阈值，显示进度
        next_threshold = self.thresholds[0][0]
        progress = int(hold_time / next_threshold * 100)
        return f"Hold {hold_time:.1f}s ({progress}%)"


class OnReleaseAction(GestureAction):
    """
    松开触发动作 - 松开握拳 → 暂停

    处理 "手势保持一段时间后松开" 的场景
    """

    def __init__(self, min_time: float, max_time: float, key, description: str):
        """
        Args:
            min_time: 最短保持时间（秒）
            max_time: 最长保持时间（秒），超过此时间不触发
            key: 按键或可调用对象
            description: 动作描述
        """
        self.min_time = min_time
        self.max_time = max_time
        self.key = key
        self.description = description
        self._last_gesture = GestureType.NONE
        self._last_hold_time = 0.0

    def execute(self, hold_time, state_machine, points):
        current_gesture = state_machine.current_gesture

        # 检测手势切换（松开）
        if self._last_gesture != GestureType.NONE and current_gesture == GestureType.NONE:
            # 检查保持时间是否在有效范围内
            if self.min_time <= self._last_hold_time < self.max_time:
                if callable(self.key):
                    self.key()
                else:
                    pyautogui.press(self.key)
                self._last_hold_time = 0.0
                return f"✓ {self.description}"

        # 更新状态
        self._last_gesture = current_gesture
        self._last_hold_time = hold_time

        return ""  # OnRelease 不显示保持状态


class PositionAction(GestureAction):
    """
    位置控制动作 - 食指 Y 轴位置 → 滚动速度

    好品味：用简单的线性映射替代复杂的 if-else
    """

    def __init__(self, frame_height: int):
        """
        Args:
            frame_height: 画面高度
        """
        self.frame_height = frame_height
        self.center_y = frame_height // 2
        self.dead_zone = frame_height // 6

    def execute(self, hold_time, state_machine, points):
        finger_y = points.get('index_y', self.center_y)

        # 计算与中心的距离
        offset = self.center_y - finger_y  # 正 = 上，负 = 下

        # 死区内不滚动
        if abs(offset) <= self.dead_zone:
            return "Center - Stop"

        # 滚动速度 = 距离 / 20，限制在 [-10, 10]
        scroll_speed = int((offset - (self.dead_zone if offset > 0 else -self.dead_zone)) / 20)
        scroll_speed = max(-10, min(10, scroll_speed))

        if scroll_speed != 0:
            pyautogui.scroll(scroll_speed)
            direction = "Up" if scroll_speed > 0 else "Down"
            return f"Scroll {direction} ({abs(scroll_speed)})"

        return "Pointing: Ready"


class RepeatKeyAction(GestureAction):
    """
    重复按键动作 - Victory → 按 4 次左键（后退 20s）

    配置示例：
        RepeatKeyAction(0.5, 'left', 4, 'Rewind 20s')
    """

    def __init__(self, hold_time: float, key: str, count: int, description: str):
        """
        Args:
            hold_time: 触发所需保持时间（秒）
            key: 按键
            count: 重复次数
            description: 动作描述
        """
        self.hold_time = hold_time
        self.key = key
        self.count = count
        self.description = description

    def execute(self, hold_time, state_machine, points):
        if hold_time >= self.hold_time:
            if state_machine.should_execute(self.hold_time):
                for _ in range(self.count):
                    pyautogui.press(self.key)
                return f"✓ {self.description}"
            else:
                return f"✓ {self.description}"

        # 显示进度
        progress = int(hold_time / self.hold_time * 100)
        return f"{self.description} ({progress}%)"


class IdleAction(GestureAction):
    """空闲动作 - 显示提示信息"""

    def __init__(self, message: str):
        self.message = message

    def execute(self, hold_time, state_machine, points):
        return self.message
