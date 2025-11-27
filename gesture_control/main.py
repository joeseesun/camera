"""
Gesture Control Hub - 主程序入口
使用 Google MediaPipe Gesture Recognizer Task

重构原则（Linus Style）：
1. 数据结构优先 - 配置表驱动，零 if-elif 分支
2. 函数简短 - 主循环 < 40 行
3. 单一职责 - 每个函数只做一件事
"""

import cv2
import pyautogui
from .config import CAMERA_ID, WINDOW_NAME, CAMERA_WIDTH, CAMERA_HEIGHT
from .core.gestures import GestureRecognizer, GestureType
from .core.activation import ActivationManager
from .core.state_machine import GestureStateMachine
from .core.actions import (
    TimedAction,
    PositionAction,
    RepeatKeyAction,
    IdleAction,
)


def create_action_map(frame_height: int) -> dict:
    """
    创建手势 → 动作的配置表

    好品味：用配置表消除 if-elif 地狱
    """
    return {
        GestureType.FIST: TimedAction([
            (0.5, 'space', 'Play/Pause'),
            (3.0, 'f', 'Fullscreen'),
        ]),
        GestureType.POINTING_UP: PositionAction(frame_height),
        GestureType.VICTORY: RepeatKeyAction(0.5, 'left', 4, 'Rewind 20s'),
        GestureType.I_LOVE_YOU: RepeatKeyAction(0.5, 'right', 4, 'Forward 20s'),
        GestureType.OPEN_PALM: IdleAction('Point=Scroll | Fist=Pause/Full'),
    }


def main():
    """主程序 - 极简版"""
    print("=" * 50)
    print("  Gesture Control Hub (Refactored)")
    print("=" * 50)
    print("\nGesture Controls:")
    print("  Open_Palm 1.5s → Activate")
    print("  [After Activate]")
    print("    Pointing_Up → Scroll (position control)")
    print("    Closed_Fist 0.5s → Pause | 3s → Fullscreen")
    print("    Victory (✌) → Rewind 20s")
    print("    ILoveYou (🤟) → Forward 20s")
    print("\nKeys: 'p' = pin/unpin | 'q' = quit\n")

    # 初始化组件
    try:
        recognizer = GestureRecognizer()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1

    activation = ActivationManager()
    state_machine = GestureStateMachine()

    # 初始化摄像头
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        print("❌ Error: Cannot open camera")
        return 1

    # 设置窗口（小窗口模式）
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, CAMERA_WIDTH, CAMERA_HEIGHT)
    pinned = False

    # 主循环
    action_map = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # 延迟创建 action_map（需要 frame_height）
        if action_map is None:
            action_map = create_action_map(h)

        # 识别手势
        gesture, points = recognizer.recognize(frame, w, h)
        has_hand = gesture != GestureType.NONE

        # 更新激活状态
        act = activation.update(has_hand, gesture)

        # 执行动作并获取状态
        if not act['activated']:
            # 未激活
            if act['activation_progress'] > 0:
                status = f"Activating... {int(act['activation_progress']*100)}%"
                _draw_activating(frame, act['activation_progress'])
            else:
                status = "Show Palm to Activate"
                _draw_minimal(frame, status, (180, 180, 180))
        elif not act['ready_for_action']:
            # 激活中，等待松手
            status = "Release hand to start"
            _draw_minimal(frame, status, (0, 200, 0))
        else:
            # 已激活，执行手势动作
            hold_time = state_machine.update(gesture)
            action = action_map.get(gesture)

            if action:
                status = action.execute(hold_time, state_machine, points)
            else:
                status = "Unknown gesture"

            _draw_minimal(frame, status, (0, 200, 0))

            # 特殊：为 POINTING_UP 绘制辅助线
            if gesture == GestureType.POINTING_UP:
                _draw_scroll_guides(frame, h, w)

        # 显示置顶状态
        if pinned:
            cv2.putText(frame, "[PIN]", (w - 60, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.imshow(WINDOW_NAME, frame)

        # 键盘控制
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('p'):
            pinned = not pinned
            cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1.0 if pinned else 0.0)
            print(f"Window {'PINNED' if pinned else 'UNPINNED'}")

    # 清理
    cap.release()
    cv2.destroyAllWindows()
    recognizer.close()

    print("\nBye!")
    return 0


# ===== UI 函数 - 极简风格 =====

def _draw_minimal(frame, text: str, color: tuple):
    """极简 UI：只显示一行状态文本"""
    h, w = frame.shape[:2]

    # 半透明背景条
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 35), (40, 40, 40), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # 状态文本
    cv2.putText(frame, text, (10, 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def _draw_activating(frame, progress: float):
    """激活进度 - 简化版"""
    h, w = frame.shape[:2]

    # 橙色背景条
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 50), (0, 140, 255), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # 文字
    cv2.putText(frame, f"Activating... {int(progress*100)}%", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


def _draw_scroll_guides(frame, h: int, w: int):
    """绘制滚动辅助线（仅在 POINTING_UP 时）"""
    center_y = h // 2
    dead_zone = h // 6

    # 中线和死区
    cv2.line(frame, (0, center_y), (w, center_y), (0, 200, 0), 1)
    cv2.line(frame, (0, center_y - dead_zone), (w, center_y - dead_zone), (100, 100, 100), 1)
    cv2.line(frame, (0, center_y + dead_zone), (w, center_y + dead_zone), (100, 100, 100), 1)


if __name__ == "__main__":
    exit(main())
