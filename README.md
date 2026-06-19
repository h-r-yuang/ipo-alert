# A股主板打新提醒器

每天早上 8:00 自动检查主板新股申购，通过微信推送提醒。

## 文件说明

| 文件 | 说明 |
|------|------|
| `ipo_alert.py` | 主脚本，拉取东财IPO数据并推送 |
| `config.py` | 配置（SendKey、主板代码前缀） |
| `requirements.txt` | Python 依赖 |
| `.github/workflows/ipo-alert.yml` | GitHub Actions 定时任务 |

## 本地运行

```bash
pip install -r requirements.txt
python ipo_alert.py
```

## 微信推送设置

1. 打开 https://sct.ftqq.com 微信扫码登录
2. 复制 SendKey
3. 写入 `config.py` 的 `SENDKEY`
