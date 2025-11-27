# 🖐️ Gesture Control Hub

**用手势控制电脑，解放你的双手！**

看视频时手上沾满薯片？做饭时想翻菜谱？躺在床上懒得动？现在，只需对着摄像头比划手势，就能控制视频播放、网页滚动！

基于 Google MediaPipe 官方手势识别模型，识别准确、响应迅速。

---

## ✨ 功能演示

| 手势 | 功能 | 场景 |
|:---:|:---|:---|
| ✊ 握拳 | 暂停 | 来电话了，握拳暂停 |
| 🖐️ 张开手掌 | 播放 | 回来了，张开手继续 |
| ✌️ 剪刀手 | 全屏 | 比个 ✌️ 进入沉浸模式 |
| 👍 点赞 | 快进 20s | 跳过无聊片段 |
| 👎 倒拇指 | 快退 20s | 没听清？倒回去 |
| ☝️ 单指向上 | 向上滚动 | 翻菜谱、看文章 |
| 👇 单指向下 | 向下滚动 | 继续往下看 |

**无需激活，手势直接生效！** 保持手势 0.3 秒即可触发。

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/joeseesun/camera.git
cd camera
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 下载手势模型

```bash
curl -o gesture_recognizer.task https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task
```

### 4. 运行

```bash
python run.py
```

**就这么简单！** 🎉

---

## 🎮 使用技巧

1. **保持手势稳定** - 手势保持 0.3 秒触发，避免误操作
2. **光线充足** - 良好的光线让识别更准确
3. **手掌面向摄像头** - 确保摄像头能看清你的手
4. **窗口置顶** - 按 `p` 键可以让窗口置顶/取消置顶
5. **退出程序** - 按 `q` 键退出

---

## 💡 适用场景

- 🍳 **做饭看菜谱** - 手上有油也能翻页
- 🛋️ **躺着看视频** - 懒得伸手拿鼠标
- 🎮 **吃零食追剧** - 薯片手也能暂停
- 💻 **演示文稿** - 远程翻页控制
- 🏋️ **健身看教程** - 运动中也能暂停

---

## 🛠️ 系统要求

- Python 3.8+
- macOS / Windows / Linux
- 摄像头

---

## 📦 依赖

- `opencv-python` - 视频捕获与显示
- `mediapipe` - Google 手势识别
- `pyautogui` - 模拟键盘操作

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 👨‍💻 作者

**向阳乔木**

- X (Twitter): [@vista8](https://x.com/vista8)
- 公众号: **向阳乔木**

如果这个项目对你有帮助，欢迎 ⭐ Star 支持！

---

## 📄 License

MIT License

