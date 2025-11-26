"""
手部检测器 - 封装 MediaPipe Hands
"""

import cv2
import mediapipe as mp
from ..config import (
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
)


class HandDetector:
    """手部检测器，提供手部关键点检测功能"""

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )

    def detect(self, frame):
        """
        检测手部关键点

        Args:
            frame: BGR 格式的图像帧

        Returns:
            landmarks: 单手关键点（第一只手），如果没有检测到则返回 None
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            return results.multi_hand_landmarks[0]
        return None

    def detect_all(self, frame):
        """
        检测所有手部关键点（支持双手）

        Args:
            frame: BGR 格式的图像帧

        Returns:
            list: 所有手部关键点列表，如果没有检测到则返回空列表
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            return results.multi_hand_landmarks
        return []

    def draw_landmarks(self, frame, landmarks):
        """在图像上绘制手部骨架"""
        if landmarks:
            self.mp_drawing.draw_landmarks(
                frame, landmarks, self.mp_hands.HAND_CONNECTIONS
            )

    def draw_all_landmarks(self, frame, all_landmarks):
        """在图像上绘制所有手部骨架"""
        for landmarks in all_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, landmarks, self.mp_hands.HAND_CONNECTIONS
            )

    def close(self):
        """释放资源"""
        self.hands.close()

