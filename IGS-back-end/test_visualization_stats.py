import requests
import json

# 测试可视化数据API
def test_visualization_api():
    url = 'http://localhost:8000/visualization/display/'
    
    try:
        # 发送GET请求
        response = requests.get(url)
        
        # 检查响应状态码
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            print("可视化数据API测试成功！")
            print("\n=== 答题统计数据 ===")
            print(f"正确率: {data.get('accuracy')}%")
            print(f"总题数: {data.get('totalQuestions')}")
            print("\n=== 完整响应数据 ===")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return True
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试可视化数据API...")
    test_visualization_api()