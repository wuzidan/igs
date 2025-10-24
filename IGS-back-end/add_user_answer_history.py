#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为测试用户添加作答历史和答题行为数据
用于测试模型接口和训练效果
"""

import os
import sys
import random
import json
from datetime import datetime, timedelta
from django.utils import timezone

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ITS_project.settings')
import django
django.setup()

# 导入所需的模型
from student.models import User
from historyRecord.models import HistoryRecord
from question.models import Question, PracticeRecord, QuestionType, DifficultyLevel, PracticeType

def add_user_answer_history():
    """为测试用户添加作答历史和答题行为数据"""
    print("开始添加用户作答历史和答题行为数据...")
    
    try:
        # 获取测试用户
        try:
            test_user = User.objects.get(username='testuser')
            print(f"找到测试用户: {test_user.username} (学号: {test_user.student_id})")
        except User.DoesNotExist:
            print("错误：找不到测试用户'testuser'，请先运行 create_test_data.py")
            return
        
        # 创建用户统计信息（如果不存在）
        UserStatistics = HistoryRecord.UserStatistics
        user_stats, created = UserStatistics.objects.get_or_create(user=test_user)
        if created:
            user_stats.total_attempts = 0
            user_stats.avg_score = 0.00
            user_stats.total_duration_minutes = 0
            user_stats.highest_score = 0
            user_stats.save()
            print("创建了用户统计信息")
        
        # 生成作答历史记录
        total_score = 0
        highest_score = 0
        total_duration = 0
        
        # 生成5次练习记录
        for practice_num in range(5):
            # 随机生成练习日期（过去30天内）
            days_ago = random.randint(1, 30)
            practice_date = timezone.now() - timedelta(days=days_ago)
            
            # 随机练习时长（分钟）
            duration_minutes = random.randint(10, 30)
            total_duration += duration_minutes
            
            # 随机得分
            practice_score = random.randint(60, 95)
            total_score += practice_score
            if practice_score > highest_score:
                highest_score = practice_score
            
            # 随机练习类型
            practice_type = random.choice(list(PracticeType))
            
            # 创建练习记录（PracticeRecord）
            practice_record = PracticeRecord.objects.create(
                student=test_user,
                type=practice_type,
                date=practice_date,
                score=practice_score,
                duration_minutes=duration_minutes
            )
            print(f"创建练习记录 #{practice_num+1}: {practice_type.label}, 得分 {practice_score}分, 时长 {duration_minutes}分钟")
            
            # 同时创建历史记录（HistoryRecord）
            history_record = HistoryRecord.objects.create(
                user=test_user,
                type=practice_type.label,
                date=practice_date,
                score=practice_score,
                duration=f'{duration_minutes}分钟',
                expanded=False
            )
            print(f"  - 创建对应的历史记录: ID {history_record.id}")
            
            # 为这次练习创建5-10道题目记录
            num_questions = random.randint(5, 10)
            for q_num in range(num_questions):
                # 随机题目类型和难度
                q_type = random.choice(list(QuestionType))
                difficulty = random.choice(list(DifficultyLevel))
                
                # 随机是否答对
                is_correct = random.random() > 0.3  # 70%的正确率
                
                # 生成题目内容
                if q_type == QuestionType.SINGLE_CHOICE:
                    content = f"单选题 #{practice_num+1}-{q_num+1}: 以下哪个选项是正确的？"
                    options = json.dumps(["选项A", "选项B", "选项C", "选项D"])
                    correct_answer = json.dumps(["选项B"])
                    user_answer = correct_answer if is_correct else json.dumps([random.choice(["选项A", "选项C", "选项D"])])
                elif q_type == QuestionType.MULTIPLE_CHOICE:
                    content = f"多选题 #{practice_num+1}-{q_num+1}: 以下哪些选项是正确的？"
                    options = json.dumps(["选项A", "选项B", "选项C", "选项D"])
                    correct_answer = json.dumps(["选项A", "选项C"])
                    user_answer = correct_answer if is_correct else json.dumps(random.sample(["选项A", "选项B", "选项C", "选项D"], k=random.randint(1, 3)))
                elif q_type == QuestionType.JUDGMENT:
                    content = f"判断题 #{practice_num+1}-{q_num+1}: 这个陈述是否正确？"
                    options = json.dumps(["正确", "错误"])
                    correct_answer = json.dumps(["正确"])
                    user_answer = correct_answer if is_correct else json.dumps(["错误"])
                else:  # SHORT_ANSWER
                    content = f"简答题 #{practice_num+1}-{q_num+1}: 请简述这个概念的含义。"
                    options = None
                    correct_answer = json.dumps(["这是一个完整的答案解释。"])
                    if is_correct:
                        user_answer = json.dumps(["这是一个接近正确的回答。"])
                    else:
                        user_answer = json.dumps(["这是一个不完整或错误的回答。"])
                
                # 创建题目记录
                question = Question.objects.create(
                    record=practice_record,
                    type=q_type,
                    difficulty=difficulty,
                    content=content,
                    correct=is_correct,
                    user_answer=user_answer,
                    correct_answer=correct_answer,
                    options=options,
                    analysis="这是题目的详细解析说明。"
                )
            
        # 更新用户统计信息
        user_stats.total_attempts = 5  # 5次练习
        user_stats.avg_score = total_score / 5  # 5次练习的平均分
        user_stats.total_duration_minutes = total_duration
        user_stats.highest_score = highest_score
        user_stats.last_highest_date = datetime.now().date()
        
        # 更新题型正确率统计
        type_accuracy = {
            'singleChoice': random.randint(60, 90),
            'multipleChoice': random.randint(50, 85),
            'judgment': random.randint(70, 95),
            'shortAnswer': random.randint(40, 80)
        }
        user_stats.type_accuracy = type_accuracy
        
        # 更新难度正确率统计
        difficulty_accuracy = {
            'easy': random.randint(75, 95),
            'medium': random.randint(60, 85),
            'hard': random.randint(40, 70)
        }
        user_stats.difficulty_accuracy = difficulty_accuracy
        
        user_stats.save()
        
        print("\n===== 作答历史和答题行为数据添加完成 =====")
        print(f"用户: {test_user.username}")
        print(f"总练习次数: {user_stats.total_attempts}")
        print(f"平均得分: {user_stats.avg_score:.1f}")
        print(f"最高得分: {user_stats.highest_score}")
        print(f"总练习时长: {user_stats.total_duration_minutes}分钟")
        print("\n题型正确率统计:")
        for q_type, accuracy in type_accuracy.items():
            print(f"  - {q_type}: {accuracy}%")
        print("\n难度正确率统计:")
        for diff, accuracy in difficulty_accuracy.items():
            print(f"  - {diff}: {accuracy}%")
        print("\n这些数据可以用于测试模型接口和训练效果。")
        print("你可以通过Django管理后台或API接口查看这些数据。")
        
    except Exception as e:
        print(f"错误：添加数据时发生异常 - {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_user_answer_history()