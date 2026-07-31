import requests
import json

# 这是你刚才在 Django 里写好的接口地址
# 注意：如果在你的 urls.py 里有前缀（比如 /api/），请对应修改。这里假设是直接访问。
url = "http://127.0.0.1:8000/api/recommend-path"

# 模拟前端 Vue 传给你的 JSON 数据
payload = {"student_id": "stu_001", "target": "一元二次方程"}

print(f"🚀 正在向 {url} 发送 POST 请求...")

try:
    # 发送 POST 请求
    response = requests.post(url, json=payload)

    # 打印返回的状态码（200代表通了，404代表地址写错了，500代表代码报错了）
    print(f"📦 收到状态码: {response.status_code}")

    # 打印后端传回来的最终 JSON 数据
    print("\n========== 🎉 接口返回的数据 ==========")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except Exception as e:
    print(f"❌ 请求失败，请检查 Django 服务是否启动，报错: {e}")
