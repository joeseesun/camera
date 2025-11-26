#!/usr/bin/env python3
"""
Touch-Free Recipe Scroller
使用手势控制屏幕滚动 - 做饭时不用脏手碰屏幕
"""

import cv2
import mediapipe as mp
import pyautogui
import time

# ===== 配置参数 =====
COOLDOWN = 0.3           # 滚动冷却时间(秒) - 防止过快滚动
SCROLL_AMOUNT = 3        # 每次滚动量(行数)
TOP_ZONE_RATIO = 0.25    # 顶部触发区域(屏幕高度的25%)
BOTTOM_ZONE_RATIO = 0.75 # 底部触发区域(屏幕高度的75%)

# ===== 初始化 =====
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,           # 只检测一只手 - 简单有效
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("错误: 无法打开摄像头")
    exit(1)

# 状态变量 - 就这两个,没有复杂的类
last_scroll_time = 0

print("Touch-Free Recipe Scroller 已启动")
print("- 食指放在屏幕顶部 → 向上滚动")
print("- 食指放在屏幕底部 → 向下滚动")
print("- 按 'q' 退出\n")

# ===== 主循环 =====
while True:
    ret, frame = cap.read()
    if not ret:
        print("错误: 无法读取摄像头帧")
        break

    # 翻转图像(镜像效果更自然)
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # 转换颜色空间供MediaPipe处理
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # 绘制触发区域线条
    top_line_y = int(h * TOP_ZONE_RATIO)
    bottom_line_y = int(h * BOTTOM_ZONE_RATIO)
    cv2.line(frame, (0, top_line_y), (w, top_line_y), (0, 255, 0), 2)
    cv2.line(frame, (0, bottom_line_y), (w, bottom_line_y), (0, 0, 255), 2)

    # 添加文字说明
    cv2.putText(frame, "UP ZONE", (10, top_line_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, "DOWN ZONE", (10, bottom_line_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # 处理手部检测结果
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]  # 只取第一只手

        # 绘制手部骨架
        mp_drawing.draw_landmarks(
            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # 获取食指尖坐标 (landmark 8)
        index_tip = hand_landmarks.landmark[8]
        finger_x = int(index_tip.x * w)
        finger_y = int(index_tip.y * h)

        # 绘制食指位置指示器
        cv2.circle(frame, (finger_x, finger_y), 15, (255, 0, 255), -1)

        # 时间门控 - 防止过快滚动
        current_time = time.time()
        if current_time - last_scroll_time >= COOLDOWN:

            # 判断是否在触发区域
            if finger_y < top_line_y:
                # 向上滚动
                pyautogui.scroll(SCROLL_AMOUNT)
                last_scroll_time = current_time
                cv2.putText(frame, "SCROLLING UP", (w//2 - 100, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            elif finger_y > bottom_line_y:
                # 向下滚动
                pyautogui.scroll(-SCROLL_AMOUNT)
                last_scroll_time = current_time
                cv2.putText(frame, "SCROLLING DOWN", (w//2 - 120, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # 显示冷却状态
    time_since_last = time.time() - last_scroll_time
    if time_since_last < COOLDOWN:
        cooldown_text = f"Cooldown: {COOLDOWN - time_since_last:.1f}s"
        cv2.putText(frame, cooldown_text, (10, h - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    # 显示窗口
    cv2.imshow('Touch-Free Recipe Scroller', frame)

    # 按'q'退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ===== 清理资源 =====
cap.release()
cv2.destroyAllWindows()
hands.close()
print("\n已退出")
