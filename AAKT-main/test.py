import requests
import json
import time

# --- 配置 ---
# 如果您的服务运行在其他机器或端口，请修改这里
API_URL = "http://127.0.0.1:5000/diagnose"


# --- 测试用例 ---

def test_case_1_normal():
    """测试一个正常的、包含有效交互的请求"""
    print("\n--- [Test Case 1: Normal Request] ---")
    payload = {
        "interactions": [
            {"question_id": "81", "correct": 1},
            {"question_id": "80", "correct": 0},
            {"question_id": "82", "correct": 1},
            {"question_id": "90", "correct": 1}
        ]
    }
    send_request(payload)


def test_case_2_invalid_question_id():
    """测试包含模型不认识的题目ID的请求"""
    print("\n--- [Test Case 2: Invalid Question ID] ---")
    payload = {
        "interactions": [
            {"question_id": "99999", "correct": 1},  # 假设这个ID不存在
            {"question_id": "32", "correct": 0}
        ]
    }
    print("Note: This should still succeed, as the backend filters out invalid IDs.")
    send_request(payload)


def test_case_3_empty_interactions():
    """测试交互列表为空的情况"""
    print("\n--- [Test Case 3: Empty Interactions] ---")
    payload = {
        "interactions": []
    }
    send_request(payload)


def test_case_4_bad_format():
    """测试请求体格式错误的情况"""
    print("\n--- [Test Case 4: Bad Format] ---")
    payload = {
        "wrong_key": []  # 缺少 "interactions" 键
    }
    send_request(payload)


def send_request(payload):
    """统一的请求发送和结果打印函数"""
    print("Payload:", json.dumps(payload, indent=2))
    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload)
        end_time = time.time()

        print(f"\nResponse (Status Code: {response.status_code}, Time: {end_time - start_time:.2f}s):")

        # 美化打印JSON响应
        try:
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            print(response.text)

    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Could not connect to the server at {API_URL}.")
        print("Please make sure your 'app.py' server is running.")


# --- 运行所有测试 ---
if __name__ == "__main__":
    test_case_1_normal()
    test_case_2_invalid_question_id()
    test_case_3_empty_interactions()
    test_case_4_bad_format()