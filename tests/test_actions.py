"""
测试 Actions 系统 - 手势动作逻辑

运行方式：
    python -m pytest tests/test_actions.py -v
"""

import time
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesture_control.core.actions import (
    TimedAction,
    RepeatKeyAction,
    IdleAction,
    PositionAction,
)
from gesture_control.core.state_machine import GestureStateMachine
from gesture_control.core.gestures import GestureType


def test_timed_action_basic():
    """测试时间触发动作 - 基础功能"""
    with patch('gesture_control.core.actions.pyautogui') as mock_gui:
        action = TimedAction([
            (0.5, 'space', 'Play/Pause'),
            (3.0, 'f', 'Fullscreen'),
        ])

        sm = GestureStateMachine()
        sm.update(GestureType.FIST)

        # 0.3s：尚未触发
        result = action.execute(0.3, sm, {})
        assert 'Hold 0.3s' in result
        mock_gui.press.assert_not_called()

        # 0.6s：触发第一个阈值
        result = action.execute(0.6, sm, {})
        assert 'Play/Pause' in result
        mock_gui.press.assert_called_once_with('space')


def test_timed_action_no_repeat():
    """测试时间触发动作 - 防止重复触发"""
    with patch('gesture_control.core.actions.pyautogui') as mock_gui:
        action = TimedAction([
            (0.5, 'space', 'Play/Pause'),
        ])

        sm = GestureStateMachine()
        sm.update(GestureType.FIST)

        # 第一次触发
        action.execute(0.6, sm, {})
        assert mock_gui.press.call_count == 1

        # 第二次不应该触发
        action.execute(0.7, sm, {})
        assert mock_gui.press.call_count == 1


def test_repeat_key_action():
    """测试重复按键动作 - Victory → 4 次左键"""
    with patch('gesture_control.core.actions.pyautogui') as mock_gui:
        action = RepeatKeyAction(0.5, 'left', 4, 'Rewind 20s')

        sm = GestureStateMachine()
        sm.update(GestureType.VICTORY)

        # 0.3s：未触发
        result = action.execute(0.3, sm, {})
        assert 'Rewind 20s' in result
        assert '%' in result
        mock_gui.press.assert_not_called()

        # 0.6s：触发
        result = action.execute(0.6, sm, {})
        assert 'Rewind 20s' in result
        assert mock_gui.press.call_count == 4
        mock_gui.press.assert_called_with('left')


def test_idle_action():
    """测试空闲动作 - 显示提示信息"""
    action = IdleAction('Test Message')
    sm = GestureStateMachine()

    result = action.execute(0, sm, {})
    assert result == 'Test Message'


def test_position_action():
    """测试位置控制动作 - 滚动"""
    with patch('gesture_control.core.actions.pyautogui') as mock_gui:
        frame_height = 480
        action = PositionAction(frame_height)

        sm = GestureStateMachine()
        sm.update(GestureType.POINTING_UP)

        # 中心位置：不滚动
        points = {'index_y': frame_height // 2}
        result = action.execute(0, sm, points)
        assert 'Stop' in result
        mock_gui.scroll.assert_not_called()

        # 顶部：向上滚动
        points = {'index_y': 50}
        result = action.execute(0, sm, points)
        assert 'Scroll Up' in result
        mock_gui.scroll.assert_called()

        # 底部：向下滚动
        mock_gui.reset_mock()
        points = {'index_y': frame_height - 50}
        result = action.execute(0, sm, points)
        assert 'Scroll Down' in result
        mock_gui.scroll.assert_called()


if __name__ == "__main__":
    print("Running action tests...")

    test_timed_action_basic()
    print("✓ test_timed_action_basic")

    test_timed_action_no_repeat()
    print("✓ test_timed_action_no_repeat")

    test_repeat_key_action()
    print("✓ test_repeat_key_action")

    test_idle_action()
    print("✓ test_idle_action")

    test_position_action()
    print("✓ test_position_action")

    print("\n所有动作测试通过！")
