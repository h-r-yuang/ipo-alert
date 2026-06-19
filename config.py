import os

# Server酱 SendKey，用于微信推送
# 优先读环境变量（GitHub Actions Secret），其次用本地配置
SENDKEY = os.environ.get("SENDKEY") or "SCT366859TUkl2UOFdVxGJ06sDUetSQYj3"

# 主板代码前缀
MAINBOARD_PREFIXES = ("000", "001", "002", "003", "600", "601", "603", "605")
