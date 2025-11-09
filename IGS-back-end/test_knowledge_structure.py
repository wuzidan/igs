import requests

# 测试知识结构API
def test_knowledge_structure_api():
    url = "http://localhost:8000/knowledge/structure/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查HTTP响应状态
        
        data = response.json()
        print("知识结构API响应成功!")
        print(f"\n总体掌握情况:")
        print(f"知识点覆盖率: {data.get('coverageRate', 0)}%")
        print(f"已掌握知识点: {data.get('masteredCount', 0)}/{data.get('totalCount', 0)}")
        print(f"平均掌握程度: {data.get('avgMastery', 0)}%")
        
        print(f"\n知识点列表:")
        knowledge_list = data.get('knowledgeList', [])
        for knowledge in knowledge_list:
            print(f"- {knowledge.get('name', '未知')} ({knowledge.get('categoryText', '未知')}): {knowledge.get('mastery', 0)}%")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return False
    except ValueError:
        print("解析JSON失败")
        return False

if __name__ == "__main__":
    test_knowledge_structure_api()