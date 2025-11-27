"""
配置参数 - Gesture Control Hub
"""

# ===== 摄像头配置 =====
CAMERA_ID = 0
CAMERA_WIDTH = 320   # 小窗口模式：占屏幕角落
CAMERA_HEIGHT = 240  # 从 640x480 缩小到 320x240

# ===== 手势检测配置 =====
MAX_NUM_HANDS = 2              # 支持双手检测（拍手手势需要）
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7
CLAP_DISTANCE_THRESHOLD = 0.2  # 拍手手势：双手距离阈值

# ===== 动作配置 =====
ACTION_COOLDOWN = 1.0          # 动作冷却时间(秒) - 防止连续误触
SWIPE_THRESHOLD = 0.15         # 挥手检测阈值(相对于画面宽度)
SWIPE_FRAMES = 8               # 挥手检测帧数
PALM_HOLD_TIME = 2.0           # 张开手掌切换模式的停留时间
CLAP_HOLD_TIME = 0.3           # 拍手需要保持的时间（防误触）

# ===== 滚动模式配置 =====
SCROLL_AMOUNT = 3              # 每次滚动量
TOP_ZONE_RATIO = 0.25          # 顶部触发区域
BOTTOM_ZONE_RATIO = 0.75       # 底部触发区域
SCROLL_COOLDOWN = 0.3          # 滚动冷却时间

# ===== 视频控制配置 =====
VIDEO_SEEK_SECONDS = 30        # 快进/快退秒数
VIDEO_SEEK_TIMES = 3           # 按键次数（10秒 x 3 = 30秒）

# ===== UI 配置 =====
WINDOW_NAME = "Gesture Control Hub"
FONT_SCALE = 0.7
FONT_THICKNESS = 2

# ===== 颜色定义 (BGR) =====
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_CYAN = (255, 255, 0)

