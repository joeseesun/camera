#!/usr/bin/env python3
"""
运行所有单元测试

不需要 pytest，直接运行测试
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("  Gesture Control Hub - 单元测试")
    print("=" * 60)
    print()

    all_passed = True

    # 运行 state_machine 测试
    print("[1/2] 测试 GestureStateMachine...")
    try:
        from tests import test_state_machine
        test_state_machine.test_initial_state()
        test_state_machine.test_gesture_tracking()
        test_state_machine.test_gesture_switch()
        test_state_machine.test_should_execute()
        test_state_machine.test_multiple_thresholds()
        test_state_machine.test_reset()
        print("      ✓ 所有 GestureStateMachine 测试通过\n")
    except Exception as e:
        print(f"      ✗ 测试失败: {e}\n")
        all_passed = False

    # 运行 actions 测试
    print("[2/2] 测试 Actions 系统...")
    try:
        from tests import test_actions
        test_actions.test_timed_action_basic()
        test_actions.test_timed_action_no_repeat()
        test_actions.test_repeat_key_action()
        test_actions.test_idle_action()
        test_actions.test_position_action()
        print("      ✓ 所有 Actions 测试通过\n")
    except Exception as e:
        print(f"      ✗ 测试失败: {e}\n")
        all_passed = False

    # 总结
    print("=" * 60)
    if all_passed:
        print("✓ 所有测试通过！代码质量良好。")
    else:
        print("✗ 部分测试失败，请检查错误信息。")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(run_tests())
