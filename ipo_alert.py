"""
A股主板打新提醒器
每天早上8:00运行，拉取当日申购新股，通过Server酱推送到微信
数据来源: 东方财富 IPO 申购日历接口
"""

import datetime
import requests
from config import SENDKEY, MAINBOARD_PREFIXES


def fetch_today_ipos(date_str):
    """从东方财富拉取近期IPO列表，过滤出今日申购"""
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    params = {
        "reportName": "RPTA_APP_IPOAPPLY",
        "columns": "SECURITY_CODE,SECURITY_NAME_ABBR,APPLY_DATE,ISSUE_PRICE,ONLINE_APPLY_UPPER,TRADE_MARKET,MARKET_TYPE,PREDICT_RAISE_FUNDS",
        "pageSize": "50",
        "sortColumns": "APPLY_DATE",
        "sortTypes": "-1",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://data.eastmoney.com/xg/xg/",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    result = data.get("result") or {}
    items = result.get("data") or []

    today_ipos = []
    for item in items:
        apply_date = (item.get("APPLY_DATE") or "")[:10]
        if apply_date == date_str:
            today_ipos.append(item)
    return today_ipos


def filter_mainboard(ipos):
    """只保留主板股票（沪深主板代码前缀）"""
    result = []
    for item in ipos:
        code = item.get("SECURITY_CODE", "")
        if code.startswith(MAINBOARD_PREFIXES):
            result.append(item)
    return result


def build_message(ipos, date_str):
    """拼装推送正文（Markdown格式，Server酱支持）"""
    lines = [f"## 今日打新提醒 {date_str}\n"]
    lines.append(f"**共 {len(ipos)} 只主板新股今日申购：**\n")
    for item in ipos:
        code = item.get("SECURITY_CODE", "")
        name = item.get("SECURITY_NAME_ABBR", "")
        price = item.get("ISSUE_PRICE")
        upper = item.get("ONLINE_APPLY_UPPER")
        funds = item.get("PREDICT_RAISE_FUNDS")

        price_str = f"¥{price}" if price else "待定"
        upper_str = f"{int(upper)}股" if upper else "1000股"
        funds_str = f"{funds:.2f}亿" if funds else "待定"

        lines.append(f"- **{name}**（{code}）")
        lines.append(f"  发行价：{price_str}　申购上限：{upper_str}　募资：{funds_str}")
        lines.append("")

    lines.append("> 9:30开市后及时申购，每个账户每只最多可申购上限对应股数")
    return "\n".join(lines)


def send_wechat(title, content):
    """通过Server酱发送微信推送"""
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    resp = requests.post(url, data={"title": title, "desp": content}, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    errno = result.get("data", {}).get("errno", -1)
    if errno == 0:
        print("微信推送成功")
    else:
        print(f"推送返回异常: {result}")


def main():
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"[{today}] 检查今日主板打新...")

    try:
        ipos = fetch_today_ipos(today)
    except Exception as e:
        print(f"拉取IPO数据失败: {e}")
        return

    mainboard = filter_mainboard(ipos)
    print(f"今日全市场申购 {len(ipos)} 只，其中主板 {len(mainboard)} 只")

    if not mainboard:
        print("今日无主板新股申购，不推送")
        return

    title = f"【打新提醒】今日 {len(mainboard)} 只主板新股可申购"
    content = build_message(mainboard, today)
    print("消息预览：")
    print(content)
    print()

    try:
        send_wechat(title, content)
    except Exception as e:
        print(f"微信推送失败: {e}")


if __name__ == "__main__":
    main()
