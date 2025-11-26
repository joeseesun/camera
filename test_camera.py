#!/usr/bin/env python3
"""测试摄像头权限"""
import cv2

print("尝试打开摄像头...")
cap = cv2.VideoCapture(0)

if cap.isOpened():
    print("✅ 摄像头可用！")
    ret, frame = cap.read()
    if ret:
        print(f"✅ 成功读取帧: {frame.shape}")
        cv2.imshow("Camera Test - Press Q to quit", frame)
        cv2.waitKey(3000)  # 显示3秒
    cap.release()
    cv2.destroyAllWindows()
else:
    print("❌ 无法打开摄像头")
    print("\n请检查:")
    print("1. 系统设置 → 隐私与安全性 → 摄像头 → 勾选'终端'")
    print("2. 如果使用IDE运行,可能需要授权给Python或IDE")
