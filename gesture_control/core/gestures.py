"""
手势识别器 - 使用 Google MediaPipe Gesture Recognizer Task
官方预训练模型，识别准确度更高
"""

from enum import Enum, auto
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os


class GestureType(Enum):
    """手势类型枚举 - 对应 MediaPipe 官方手势"""
    NONE = auto()           # 无识别手势
    FIST = auto()           # Closed_Fist 握拳 ✊
    OPEN_PALM = auto()      # Open_Palm 张开手掌 🖐️
    POINTING_UP = auto()    # Pointing_Up 向上指 ☝️
    VICTORY = auto()        # Victory 双指 ✌️
    I_LOVE_YOU = auto()     # ILoveYou 三指 🤟
    THUMB_UP = auto()       # Thumb_Up 大拇指 👍
    THUMB_DOWN = auto()     # Thumb_Down 大拇指向下 👎


# MediaPipe 手势名称到我们枚举的映射
GESTURE_MAP = {
    'Closed_Fist': GestureType.FIST,
    'Open_Palm': GestureType.OPEN_PALM,
    'Pointing_Up': GestureType.POINTING_UP,
    'Victory': GestureType.VICTORY,
    'ILoveYou': GestureType.I_LOVE_YOU,
    'Thumb_Up': GestureType.THUMB_UP,
    'Thumb_Down': GestureType.THUMB_DOWN,
}


class GestureRecognizer:
    """使用 MediaPipe Gesture Recognizer Task 的手势识别器"""

    SMOOTHING_FRAMES = 3  # 平滑窗口：3 帧（从 4 降到 3，更快响应）

    def __init__(self, model_path='gesture_recognizer.task'):
        """初始化识别器"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found: {model_path}\n"
                "Download: https://storage.googleapis.com/mediapipe-models/"
                "gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"
            )

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,  # 从 0.6 → 0.5，更容易检测到手
            min_hand_presence_confidence=0.5,   # 从 0.6 → 0.5
            min_tracking_confidence=0.5,        # 从 0.6 → 0.5
        )
        self.recognizer = vision.GestureRecognizer.create_from_options(options)
        self.frame_count = 0
        # 多帧平滑
        from collections import deque
        self.gesture_history = deque(maxlen=self.SMOOTHING_FRAMES)
        self.confirmed_gesture = GestureType.NONE
        self.raw_gesture = GestureType.NONE
        self.raw_confidence = 0.0

    def recognize(self, frame, frame_width, frame_height):
        """识别当前帧中的手势（带多帧平滑）"""
        import cv2

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        self.frame_count += 1
        timestamp_ms = int(self.frame_count * 33)

        result = self.recognizer.recognize_for_video(mp_image, timestamp_ms)

        # 解析原始手势
        raw_gesture = GestureType.NONE
        self.raw_confidence = 0.0
        points = {}

        if result.gestures and len(result.gestures) > 0:
            top_gesture = result.gestures[0][0]
            gesture_name = top_gesture.category_name
            confidence = top_gesture.score
            self.raw_confidence = confidence

            # 置信度阈值 0.5（从 0.6 降低，提高灵敏度）
            if confidence > 0.5 and gesture_name in GESTURE_MAP:
                raw_gesture = GESTURE_MAP[gesture_name]

        self.raw_gesture = raw_gesture

        # 多帧平滑 - 使用多数投票（好品味：不要求全部相同）
        self.gesture_history.append(raw_gesture)
        if len(self.gesture_history) >= self.SMOOTHING_FRAMES:
            # 统计最常出现的手势
            from collections import Counter
            gesture_counts = Counter(self.gesture_history)
            most_common_gesture, count = gesture_counts.most_common(1)[0]

            # 多数投票：至少 2/3 帧相同（3 帧中至少 2 帧）
            if count >= (self.SMOOTHING_FRAMES * 2 // 3):
                self.confirmed_gesture = most_common_gesture

            # 手离开时快速重置（优先级更高）
            if raw_gesture == GestureType.NONE:
                self.confirmed_gesture = GestureType.NONE

        # 获取手部关键点
        if result.hand_landmarks and len(result.hand_landmarks) > 0:
            landmarks = result.hand_landmarks[0]
            index_tip = landmarks[8]   # 食指尖
            index_base = landmarks[5]  # 食指根部
            wrist = landmarks[0]       # 手腕

            # 判断手指方向
            pointing_up = index_tip.y < index_base.y

            # 检测单指伸出（用于向下指滚动）
            # 食指伸出：指尖到手腕距离 > 指根到手腕距离
            index_extended = self._distance(index_tip, wrist) > self._distance(index_base, wrist) * 1.1
            # 其他手指收起（放宽条件）
            middle_tip = landmarks[12]
            middle_base = landmarks[9]
            middle_folded = self._distance(middle_tip, wrist) < self._distance(middle_base, wrist) * 1.5

            single_finger = index_extended and middle_folded

            points = {
                'index_x': int(index_tip.x * frame_width),
                'index_y': int(index_tip.y * frame_height),
                'pointing_up': pointing_up,
                'single_finger': single_finger,
            }

        return self.confirmed_gesture, points

    def _distance(self, p1, p2) -> float:
        """计算两点距离"""
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2) ** 0.5

    def get_debug_info(self):
        """返回调试信息"""
        return f"Raw:{self.raw_gesture.name}({self.raw_confidence:.2f})"

    def close(self):
        """释放资源"""
        if hasattr(self, 'recognizer'):
            self.recognizer.close()

