"""
测试 GestureStateMachine - 状态管理核心逻辑

运行方式：
    python -m pytest tests/test_state_machine.py -v
"""

import time
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesture_control.core.state_machine import GestureStateMachine
from gesture_control.core.gestures import GestureType


def test_initial_state():
    """测试初始状态"""
    sm = GestureStateMachine()
    assert sm.current_gesture == GestureType.NONE
    assert sm.start_time == 0.0
    assert len(sm.executed_thresholds) == 0


def test_gesture_tracking():
    """测试手势跟踪和计时"""
    sm = GestureStateMachine()

    # 第一次更新：握拳
    hold_time = sm.update(GestureType.FIST)
    assert hold_time == 0.0
    assert sm.current_gesture == GestureType.FIST

    # 等待 0.1 秒
    time.sleep(0.1)
    hold_time = sm.update(GestureType.FIST)
    assert 0.09 <= hold_time <= 0.15  # 允许一些误差


def test_gesture_switch():
    """测试手势切换时重置状态"""
    sm = GestureStateMachine()

    # 握拳 0.2 秒
    sm.update(GestureType.FIST)
    time.sleep(0.2)
    sm.update(GestureType.FIST)

    # 切换到 OPEN_PALM
    hold_time = sm.update(GestureType.OPEN_PALM)
    assert hold_time == 0.0  # 重置为 0
    assert sm.current_gesture == GestureType.OPEN_PALM
    assert len(sm.executed_thresholds) == 0  # 清空已执行标记


def test_should_execute():
    """测试动作执行标记（避免重复触发）"""
    sm = GestureStateMachine()

    # 第一次检查：应该执行
    assert sm.should_execute(0.5) is True

    # 第二次检查：不应该重复执行
    assert sm.should_execute(0.5) is False

    # 不同阈值：应该执行
    assert sm.should_execute(3.0) is True


def test_multiple_thresholds():
    """测试多个时间阈值（握拳 0.5s → 暂停，3s → 全屏）"""
    sm = GestureStateMachine()

    sm.update(GestureType.FIST)
    time.sleep(0.6)
    sm.update(GestureType.FIST)

    # 0.5s 阈值应该可以执行
    assert sm.should_execute(0.5) is True
    # 3s 阈值还不能执行（时间不够）
    assert sm.should_execute(3.0) is True  # 但是可以标记

    # 0.5s 不能重复执行
    assert sm.should_execute(0.5) is False


def test_reset():
    """测试重置功能"""
    sm = GestureStateMachine()

    sm.update(GestureType.FIST)
    sm.should_execute(0.5)

    sm.reset()

    assert sm.current_gesture == GestureType.NONE
    assert sm.start_time == 0.0
    assert len(sm.executed_thresholds) == 0


if __name__ == "__main__":
    # 简单运行测试
    print("Running tests...")
    test_initial_state()
    print("✓ test_initial_state")

    test_gesture_tracking()
    print("✓ test_gesture_tracking")

    test_gesture_switch()
    print("✓ test_gesture_switch")

    test_should_execute()
    print("✓ test_should_execute")

    test_multiple_thresholds()
    print("✓ test_multiple_thresholds")

    test_reset()
    print("✓ test_reset")

    print("\n所有测试通过！")
