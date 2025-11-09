import json
import os
import numpy as np
import torch
from torch.utils.data import Dataset
from tqdm import tqdm


class KTDataset(Dataset):
    def __init__(self, question_tags, max_seq_len, usage="train", path=None, file_prefix=None, **kwargs):
        self.question_tags = question_tags
        self.max_seq_len = max_seq_len
        self.usage = usage
        self.pad_token_id = question_tags.num_questions + 3

        if path is None: path = f"autodl-tmp/{file_prefix}.{usage}.json"

        print(f"Loading data from: {path}")
        self.kts = []
        with open(path, "r") as f:
            for line in f:
                try:
                    # 每个kt是一个学生的交互序列: [[q, r, t], [q, r, t], ...]
                    self.kts.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode a line in {path}")
                    pass

        print(f"Loaded {len(self.kts)} student sequences for '{usage}'.")

        # --- 【核心架构变更】只计算切片，不进行预处理 ---
        self.calculate_slices()

    def calculate_slices(self):
        """
        这个函数取代了旧的 expand() 和 preprocess() 的部分功能。
        它只计算每个样本应该从哪个学生的哪个位置切片，不加载任何数据到内存。
        """
        self.splits = []
        # 注意：这里的长度是原始交互长度 * 2，与原始代码的逻辑保持一致
        item_lengths = [len(kt) * 2 for kt in self.kts]

        # 定义切片窗口的步长
        # 在训练时，窗口重叠较多以增加数据量；在评估时，步长更大以加快速度
        step_size = self.max_seq_len // 2 if self.usage == "train" else self.max_seq_len

        for item_index, length in enumerate(item_lengths):
            if length <= self.max_seq_len:
                self.splits.append((item_index, 0, length // 2))  # item_index, start_pos, end_pos
            else:
                # 对于长序列，进行滑动窗口切片
                for i in range(0, length, step_size):
                    start_index_doubled = i
                    end_index_doubled = i + self.max_seq_len

                    if end_index_doubled > length:
                        # 保证最后一个切片不会超出范围，并包含末尾
                        end_index_doubled = length
                        start_index_doubled = max(0, end_index_doubled - self.max_seq_len)

                    start_pos = start_index_doubled // 2
                    end_pos = end_index_doubled // 2

                    if start_pos < end_pos:
                        self.splits.append((item_index, start_pos, end_pos))

                    if end_index_doubled == length:
                        break  # 已到达序列末尾
        print(f"Created {len(self.splits)} samples (slices) from {len(self.kts)} students.")

    def __len__(self):
        return len(self.splits)

    def __getitem__(self, index):
        """
        【核心架构变更】只在需要时为单个切片创建张量，从根本上解决内存问题。
        """
        # 1. 获取切片信息
        student_index, start_pos, end_pos = self.splits[index]

        # 2. 获取原始数据切片
        kt_slice = self.kts[student_index][start_pos:end_pos]

        # 3. 动态地为这个小切片创建张量 (这部分逻辑来自原始的process函数)
        seq_len = len(kt_slice)
        num_questions = self.question_tags.num_questions
        num_tags = self.question_tags.num_tags

        # 创建小尺寸的张量，不会导致内存溢出
        input_ids = torch.full((1, self.max_seq_len), fill_value=self.pad_token_id, dtype=torch.long)
        input_times = torch.full((1, self.max_seq_len), fill_value=-1, dtype=torch.float)
        labels_kts = torch.full((1, self.max_seq_len), fill_value=-100, dtype=torch.long)
        labels_tags = torch.full((1, self.max_seq_len, num_tags), fill_value=-100, dtype=torch.long)

        # 填充张量
        for i, (question, result, time) in enumerate(kt_slice):
            # 原始代码将一个交互拆分为两个时间步
            idx1 = i * 2
            idx2 = i * 2 + 1

            if idx2 >= self.max_seq_len: continue  # 避免超出预设的max_seq_len

            input_ids[0, idx1] = question
            input_ids[0, idx2] = result + num_questions  # 0+num_q 或 1+num_q

            # 原始代码只在第二个时间步记录时间
            input_times[0, idx1] = -1  # 或者可以设置为0
            input_times[0, idx2] = float(time) / 60000.0  # 与原始代码的times_factor一致

            # 原始代码只在第一个时间步设置标签
            labels_kts[0, idx1] = result

            tag_vector = torch.zeros(num_tags, dtype=torch.long)
            tags = self.question_tags[question]
            if tags:
                tag_vector[tags] = 1
            labels_tags[0, idx1, :] = tag_vector

        return input_ids, input_times, labels_kts, labels_tags