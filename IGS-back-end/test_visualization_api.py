import requests

try:
    # 发送GET请求到可视化数据API
    response = requests.get('http://localhost:8000/visualization/display/')
    
    # 检查状态码
    if response.status_code == 200:
        # 获取JSON响应
        data = response.json()
        print("可视化数据API响应成功!")
        print("\n学习进度数据:")
        print(f"整体进度: {data.get('overallProgress')}%")
        print(f"已完成课程: {data.get('completedCourses')}")
        print(f"总课程数: {data.get('totalCourses')}")
        print(f"平均得分: {data.get('avgScore')}分")
        
        print("\n答题统计:")
        print(f"正确率: {data.get('accuracy')}%")
        print(f"总题数: {data.get('totalQuestions')}")
        
        print("\n知识掌握度:")
        for item in data.get('knowledgeMastery', []):
            print(f"  {item['name']}: {item['value']}%")
        
        print("\n学习时长:")
        for item in data.get('studyTime', []):
            print(f"  {item['month']}: {item['hours']}小时")
    else:
        print(f"API请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
except Exception as e:
    print(f"请求出错: {e}")