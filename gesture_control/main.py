"""
Gesture Control Hub - 主程序入口
"""

import cv2
import pyautogui
from .config import CAMERA_ID, WINDOW_NAME
from .core.detector import HandDetector
from .core.gestures import GestureRecognizer, GestureType
from .core.activation import ActivationManager


def main():
    """主程序入口"""
    print("=" * 50)
    print("  Gesture Control Hub")
    print("=" * 50)

    # 初始化组件
    detector = HandDetector()
    recognizer = GestureRecognizer()
    activation = ActivationManager()
    last_scroll_y = None      # 用于滚动检测
    last_fist_time = 0        # 记录上次握拳时长
    scroll_mode = False       # 滚动模式
    one_finger_start = None   # 单指开始时间

    # 初始化摄像头
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        print("❌ 错误: 无法打开摄像头")
        return 1

    # 创建窗口
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    pinned = False  # 置顶状态

    print("\n手势控制:")
    print("  Palm  -> Activate")
    print("  Fist 0.5s -> Pause  |  3s -> Fullscreen")
    print("  1 Finger -> Scroll")
    print("  2 Fingers -> Rewind 20s")
    print("  3 Fingers -> Forward 20s")
    print("\nKeys: 'p' = pin/unpin  |  'q' = quit\n")

    # 主循环
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # 检测手部
        landmarks = detector.detect(frame)
        gesture, points = recognizer.recognize(landmarks, w, h)

        # 更新激活状态（单手 palm 3秒）
        act = activation.update(landmarks is not None, gesture)

        # 绘制手部骨架
        detector.draw_landmarks(frame, landmarks)

        # 显示当前识别的手势（调试用）
        gesture_name = gesture.name if gesture else "NONE"
        cv2.putText(frame, f"Gesture: {gesture_name}", (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # 单指滚动（独立于激活状态）
        if gesture == GestureType.ONE_FINGER:
            current_time = __import__('time').time()
            if one_finger_start is None:
                one_finger_start = current_time

            hold_time = current_time - one_finger_start

            if hold_time >= 1.5:
                scroll_mode = True

            if scroll_mode:
                current_y = points.get('index_y', 0)
                if last_scroll_y is not None:
                    dy = last_scroll_y - current_y
                    if abs(dy) > 5:
                        pyautogui.scroll(int(dy / 3))
                        action = "Scroll Up" if dy > 0 else "Scroll Down"
                last_scroll_y = current_y
                _draw_status(frame, "Scroll Mode", action or "Move finger up/down", (255, 150, 0))
            else:
                progress = hold_time / 1.5
                _draw_status(frame, "Hold 1 Finger", f"{hold_time:.1f}s / 1.5s", (100, 100, 100))
                _draw_action_progress(frame, progress)
                last_scroll_y = None
        else:
            one_finger_start = None
            if scroll_mode and gesture != GestureType.ONE_FINGER:
                scroll_mode = False
                last_scroll_y = None

        # 根据状态绘制不同的 UI（非滚动模式）
        if gesture != GestureType.ONE_FINGER:
            action = ""
            if not act['activated']:
                if act['activation_progress'] > 0:
                    _draw_activating(frame, act['activation_progress'])
                elif not scroll_mode:
                    _draw_inactive(frame, gesture_name)
            else:
                # Activated
                if not act['ready_for_action']:
                    _draw_status(frame, "Active", "Release hand to start", (0, 200, 0))
                else:
                    # FIST: >=3s立即全屏, 0.5-3s松手暂停
                    if gesture == GestureType.FIST:
                        fist_time = activation.get_hold_time(gesture)
                        last_fist_time = fist_time

                        if fist_time >= 3.0 and not activation.action_triggered:
                            pyautogui.press('f')
                            activation.action_triggered = True
                            _draw_status(frame, "Active", "Fullscreen!", (0, 200, 0))
                        else:
                            progress = min(fist_time / 3.0, 1.0)
                            _draw_status(frame, "Active", f"Fist {fist_time:.1f}s", (0, 200, 0))
                            _draw_action_progress(frame, progress)

                    # 松手时：如果 0.5-3秒 且没触发过全屏，则暂停
                    elif last_fist_time >= 0.5 and last_fist_time < 3.0:
                        pyautogui.press('space')
                        _draw_status(frame, "Active", "Play/Pause", (0, 200, 0))
                        last_fist_time = 0

                    # TWO_FINGER: rewind 20s
                    elif gesture == GestureType.TWO_FINGER:
                        hold_time = activation.get_hold_time(gesture)
                        if hold_time >= 0.5 and not activation.action_triggered:
                            for _ in range(4):
                                pyautogui.press('left')
                            activation.action_triggered = True
                            action = "Rewind 20s"
                        _draw_status(frame, "Active", action or f"Rewind {int(hold_time/0.5*100)}%", (0, 200, 0))
                        _draw_action_progress(frame, min(hold_time/0.5, 1.0))

                    # THREE_FINGER: forward 20s
                    elif gesture == GestureType.THREE_FINGER:
                        hold_time = activation.get_hold_time(gesture)
                        if hold_time >= 0.5 and not activation.action_triggered:
                            for _ in range(4):
                                pyautogui.press('right')
                            activation.action_triggered = True
                            action = "Forward 20s"
                        _draw_status(frame, "Active", action or f"Forward {int(hold_time/0.5*100)}%", (0, 200, 0))
                        _draw_action_progress(frame, min(hold_time/0.5, 1.0))

                    else:
                        _draw_status(frame, "Active", "Fist|2F|3F", (0, 200, 0))

        # 显示置顶状态
        if pinned:
            cv2.putText(frame, "[PINNED]", (w - 100, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.imshow(WINDOW_NAME, frame)

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
    detector.close()

    print("\n👋 已退出")
    return 0


def _draw_inactive(frame, gesture_name=""):
    """绘制未激活状态"""
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 50), (60, 60, 60), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    cv2.putText(frame, "Show Palm to Activate", (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def _draw_activating(frame, progress):
    """绘制激活进度"""
    h, w = frame.shape[:2]
    # 橙色遮罩
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 80), (0, 140, 255), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    # 文字
    cv2.putText(frame, "Activating...", (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    # 进度条
    bar_w = int((w - 20) * progress)
    cv2.rectangle(frame, (10, 50), (w - 10, 70), (255, 255, 255), 2)
    cv2.rectangle(frame, (10, 50), (10 + bar_w, 70), (255, 255, 255), -1)


def _draw_status(frame, title, subtitle, color):
    """绘制激活状态"""
    h, w = frame.shape[:2]
    # 绿色边框
    cv2.rectangle(frame, (3, 3), (w-3, h-3), color, 4)
    # 顶部状态栏
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 70), color, -1)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
    # 文字
    cv2.putText(frame, title, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, subtitle, (10, 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def _draw_action_progress(frame, progress):
    """绘制动作进度圆环"""
    h, w = frame.shape[:2]
    center = (w // 2, h // 2)
    radius = 50
    cv2.circle(frame, center, radius, (100, 100, 100), 3)
    angle = int(360 * progress)
    cv2.ellipse(frame, center, (radius, radius), -90, 0, angle, (0, 255, 0), 6)


if __name__ == "__main__":
    exit(main())

