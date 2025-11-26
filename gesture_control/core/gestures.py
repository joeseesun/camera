"""
手势识别器 - 识别各种静态和动态手势
"""

from enum import Enum, auto
from collections import deque
from ..config import SWIPE_THRESHOLD, SWIPE_FRAMES, CLAP_DISTANCE_THRESHOLD


class GestureType(Enum):
    """手势类型枚举"""
    NONE = auto()           # 无识别手势
    FIST = auto()           # 握拳 ✊
    OPEN_PALM = auto()      # 张开手掌 🖐️
    ONE_FINGER = auto()     # 单指 ☝️
    TWO_FINGER = auto()     # 双指 ✌️
    THREE_FINGER = auto()   # 三指 🤟


class GestureRecognizer:
    """手势识别器"""

    def __init__(self):
        # 用于检测挥手的位置历史
        self.palm_x_history = deque(maxlen=SWIPE_FRAMES)
        self.last_gesture = GestureType.NONE

    def check_both_palms_open(self, all_landmarks):
        """
        检查是否双手都张开（用于激活）

        Args:
            all_landmarks: 所有手部关键点列表

        Returns:
            bool: 是否双手都张开
        """
        if len(all_landmarks) != 2:
            return False

        # 检查两只手是否都张开（4指以上）
        fingers_up_1 = self._count_fingers_up(all_landmarks[0])
        fingers_up_2 = self._count_fingers_up(all_landmarks[1])

        return fingers_up_1 >= 4 and fingers_up_2 >= 4

    def recognize_clap(self, all_landmarks, frame_width, frame_height):
        """
        检测拍手手势（需要双手）

        Args:
            all_landmarks: 所有手部关键点列表
            frame_width: 画面宽度
            frame_height: 画面高度

        Returns:
            GestureType: CLAP 或 NONE
        """
        if len(all_landmarks) != 2:
            return GestureType.NONE

        # 检查两只手是否都张开
        fingers_up_1 = self._count_fingers_up(all_landmarks[0])
        fingers_up_2 = self._count_fingers_up(all_landmarks[1])

        if fingers_up_1 < 4 or fingers_up_2 < 4:
            return GestureType.NONE

        # 计算两只手掌中心的距离
        palm1 = all_landmarks[0].landmark[9]
        palm2 = all_landmarks[1].landmark[9]

        distance = ((palm1.x - palm2.x) ** 2 + (palm1.y - palm2.y) ** 2) ** 0.5

        if distance < CLAP_DISTANCE_THRESHOLD:
            return GestureType.CLAP

        return GestureType.NONE

    def recognize(self, landmarks, frame_width, frame_height):
        """
        识别当前手势
        
        Args:
            landmarks: MediaPipe 手部关键点
            frame_width: 画面宽度
            frame_height: 画面高度
            
        Returns:
            GestureType: 识别的手势类型
            dict: 额外信息（如指尖位置）
        """
        if landmarks is None:
            self.palm_x_history.clear()
            return GestureType.NONE, {}

        # 提取关键点坐标
        points = self._extract_points(landmarks, frame_width, frame_height)

        # 检查静态手势（根据手指数量）
        fingers_up = self._count_fingers_up(landmarks)

        if fingers_up == 0:
            return GestureType.FIST, points
        elif fingers_up >= 4:
            return GestureType.OPEN_PALM, points
        elif fingers_up == 3:
            return GestureType.THREE_FINGER, points
        elif fingers_up == 2:
            return GestureType.TWO_FINGER, points
        elif fingers_up == 1:
            return GestureType.ONE_FINGER, points

        return GestureType.NONE, points

    def _extract_points(self, landmarks, w, h):
        """提取关键坐标点"""
        index_tip = landmarks.landmark[8]
        palm = landmarks.landmark[9]  # 中指根部作为手掌中心参考
        
        return {
            'index_x': int(index_tip.x * w),
            'index_y': int(index_tip.y * h),
            'palm_x': palm.x,
            'palm_y': palm.y,
        }

    def _count_fingers_up(self, landmarks):
        """计算伸出的手指数量"""
        tips = [8, 12, 16, 20]  # 食指、中指、无名指、小指指尖
        pips = [6, 10, 14, 18]  # 对应的第二关节
        
        count = 0
        # 四指：指尖高于第二关节则认为伸出
        for tip, pip in zip(tips, pips):
            if landmarks.landmark[tip].y < landmarks.landmark[pip].y:
                count += 1
        
        # 大拇指：水平方向判断
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        if abs(thumb_tip.x - thumb_ip.x) > 0.05:
            count += 1
            
        return count

    def _is_index_up(self, landmarks):
        """检查是否只有食指伸出"""
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]
        middle_tip = landmarks.landmark[12]
        middle_pip = landmarks.landmark[10]

        index_up = index_tip.y < index_pip.y
        middle_down = middle_tip.y > middle_pip.y

        return index_up and middle_down

    def _check_point_direction(self, landmarks):
        """
        检测食指指向方向

        Returns:
            GestureType: POINT_LEFT, POINT_RIGHT, 或 NONE
        """
        # 首先确认只有食指伸出
        if not self._is_index_up(landmarks):
            return GestureType.NONE

        # 获取食指指尖和手腕的坐标
        index_tip = landmarks.landmark[8]   # 食指指尖
        wrist = landmarks.landmark[0]       # 手腕

        # 计算水平方向差异
        dx = index_tip.x - wrist.x

        # 阈值：食指明显指向一侧
        threshold = 0.1

        if dx < -threshold:
            return GestureType.POINT_LEFT
        elif dx > threshold:
            return GestureType.POINT_RIGHT

        return GestureType.NONE

    def _is_peace_sign(self, landmarks):
        """检查是否 ✌️ 两指手势（食指+中指伸出）"""
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]
        middle_tip = landmarks.landmark[12]
        middle_pip = landmarks.landmark[10]
        ring_tip = landmarks.landmark[16]
        ring_pip = landmarks.landmark[14]

        index_up = index_tip.y < index_pip.y
        middle_up = middle_tip.y < middle_pip.y
        ring_down = ring_tip.y > ring_pip.y

        return index_up and middle_up and ring_down

    def _is_thumb_up(self, landmarks):
        """检查是否竖大拇指（大拇指朝上，其他手指握拳）"""
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        thumb_mcp = landmarks.landmark[2]
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]

        # 大拇指朝上：tip 在 ip 和 mcp 上方
        thumb_up = thumb_tip.y < thumb_ip.y < thumb_mcp.y
        # 食指弯曲
        index_down = index_tip.y > index_pip.y

        return thumb_up and index_down

    def _check_swipe(self, current_x, frame_width):
        """检测挥手动作"""
        self.palm_x_history.append(current_x)
        
        if len(self.palm_x_history) < SWIPE_FRAMES:
            return GestureType.NONE
        
        # 计算移动距离
        start_x = self.palm_x_history[0]
        end_x = self.palm_x_history[-1]
        delta = end_x - start_x
        
        if delta > SWIPE_THRESHOLD:
            self.palm_x_history.clear()
            return GestureType.SWIPE_RIGHT
        elif delta < -SWIPE_THRESHOLD:
            self.palm_x_history.clear()
            return GestureType.SWIPE_LEFT
        
        return GestureType.NONE

