"""
Gesture Control Hub - 极简手势控制
直接触发，无需激活
"""

import cv2
import time
import pyautogui
from .config import CAMERA_ID, WINDOW_NAME, CAMERA_WIDTH, CAMERA_HEIGHT
from .core.gestures import GestureRecognizer, GestureType


class SimpleGesture:
    """简单手势检测 - 保持 0.3s 触发"""

    HOLD_TIME = 0.3

    def __init__(self):
        self.current_gesture = GestureType.NONE
        self.gesture_start = 0
        self.triggered = False

    def update(self, gesture: GestureType) -> str:
        """返回要执行的动作，或 None"""
        now = time.time()

        # 手势变化，重置
        if gesture != self.current_gesture:
            self.current_gesture = gesture
            self.gesture_start = now
            self.triggered = False
            return None

        # 已触发过，不重复
        if self.triggered:
            return None

        # 检查保持时间
        hold_time = now - self.gesture_start
        if hold_time < self.HOLD_TIME:
            return None

        # 触发动作
        self.triggered = True

        if gesture == GestureType.FIST:
            return 'pause'
        elif gesture == GestureType.OPEN_PALM:
            return 'play'
        elif gesture == GestureType.VICTORY:
            return 'fullscreen'
        elif gesture == GestureType.THUMB_UP:
            return 'forward'
        elif gesture == GestureType.THUMB_DOWN:
            return 'rewind'

        return None

    def get_status(self, gesture: GestureType) -> str:
        """获取显示状态"""
        if gesture == GestureType.FIST:
            return "✊ Fist → Pause"
        elif gesture == GestureType.OPEN_PALM:
            return "🖐️ Palm → Play"
        elif gesture == GestureType.VICTORY:
            return "✌️ Victory → Fullscreen"
        elif gesture == GestureType.THUMB_UP:
            return "👍 → Forward"
        elif gesture == GestureType.THUMB_DOWN:
            return "👎 → Rewind"
        elif gesture == GestureType.POINTING_UP:
            return "☝️ Point → Scroll"
        elif gesture == GestureType.NONE:
            return "Ready"
        return gesture.name


def execute_action(action: str):
    """执行动作"""
    if action == 'pause':
        pyautogui.press('space')
        print("⏸️ Pause")
    elif action == 'play':
        pyautogui.press('space')
        print("▶️ Play")
    elif action == 'fullscreen':
        pyautogui.press('f')
        print("📺 Fullscreen")
    elif action == 'forward':
        for _ in range(4):
            pyautogui.press('right')
        print("⏩ Forward 20s")
    elif action == 'rewind':
        for _ in range(4):
            pyautogui.press('left')
        print("⏪ Rewind 20s")


def main():
    """主程序"""
    print("=" * 50)
    print("  Gesture Control Hub")
    print("=" * 50)
    print("\nGestures (0.3s hold):")
    print("  ✊ Fist     → Pause")
    print("  🖐️ Palm     → Play")
    print("  ✌️ Victory  → Fullscreen")
    print("  👍 Thumb Up → Forward 20s")
    print("  👎 Thumb Dn → Rewind 20s")
    print("  ☝️ Point Up → Scroll")
    print("\nKeys: 'p' = pin | 'q' = quit\n")

    try:
        recognizer = GestureRecognizer()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1

    detector = SimpleGesture()

    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return 1

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_EXPANDED)
    cv2.resizeWindow(WINDOW_NAME, CAMERA_WIDTH, CAMERA_HEIGHT)
    pinned = False

    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            gesture, points = recognizer.recognize(frame, w, h)

            # 检测并执行
            action = detector.update(gesture)
            if action:
                execute_action(action)

            # UI
            status = detector.get_status(gesture)
            _draw_status(frame, status)

            # 滚动：官方 Pointing_Up 或检测到单指伸出
            is_pointing = gesture == GestureType.POINTING_UP
            single_finger = points.get('single_finger', False) if points else False
            if (is_pointing or single_finger) and points:
                _draw_scroll_guides(frame, h, w)
                _do_scroll(points, h)

            if pinned:
                cv2.putText(frame, "[PIN]", (w - 60, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            cv2.imshow(WINDOW_NAME, frame)

            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                pinned = not pinned
                cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1.0 if pinned else 0.0)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    cap.release()
    cv2.destroyAllWindows()
    recognizer.close()
    print("\nBye!")
    return 0


# ===== UI 函数 =====

def _draw_status(frame, text: str):
    """显示状态文本"""
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 35), (40, 40, 40), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    cv2.putText(frame, text, (10, 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 0), 2)


def _draw_scroll_guides(frame, h: int, w: int):
    """绘制滚动辅助线"""
    center_y = h // 2
    dead_zone = h // 6
    cv2.line(frame, (0, center_y), (w, center_y), (0, 200, 0), 1)
    cv2.line(frame, (0, center_y - dead_zone), (w, center_y - dead_zone), (100, 100, 100), 1)
    cv2.line(frame, (0, center_y + dead_zone), (w, center_y + dead_zone), (100, 100, 100), 1)


# 滚动冷却
_last_scroll_time = 0

def _do_scroll(points: dict, frame_height: int):
    """根据手指方向滚动：向上指=向上滚，向下指=向下滚"""
    global _last_scroll_time

    if not points or 'pointing_up' not in points:
        return

    now = time.time()
    if now - _last_scroll_time < 0.05:  # 50ms 冷却，更灵敏
        return

    if points['pointing_up']:
        # 向上指 → 向上滚动
        pyautogui.scroll(5)
        _last_scroll_time = now
    else:
        # 向下指 → 向下滚动
        pyautogui.scroll(-5)
        _last_scroll_time = now


if __name__ == "__main__":
    exit(main())
