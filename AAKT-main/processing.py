# 您提供的代码已经是正确的，我们只在其中添加保存映射文件的部分
import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import json

# --- 配置常量 (保持不变) ---
INTERACTIONS_FILE = 'E:/PycharmProjects/AAKT-main/__pycache__/MOOPer/interaction/challenge_interaction.csv'
CHALLENGE_FILE = 'E:/PycharmProjects/AAKT-main/__pycache__/MOOPer/knowledgeGraph/entity/challenge.csv'
OUTPUT_DIR = 'autodl-tmp'
TRAIN_RATIO = 0.8
VALID_RATIO = 0.1
MIN_INTERACTIONS = 3


def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

    # --- 加载数据 (保持不变) ---
    print("Loading data...")
    interaction_df = pd.read_csv(INTERACTIONS_FILE, low_memory=False)
    challenge_df = pd.read_csv(CHALLENGE_FILE, low_memory=False)

    # --- 1. 创建ID映射 ---
    challenge_df['challenge_id'] = pd.to_numeric(challenge_df['challenge_id'], errors='coerce').dropna().astype(int)
    all_possible_challenges = sorted(challenge_df['challenge_id'].unique())
    question_map = {orig_id: new_id for new_id, orig_id in enumerate(all_possible_challenges)}

    # ...

    # --- 2. 【核心修改】保存 question_map.json 时，确保键是整数转换的字符串 ---
    question_map_path = os.path.join(OUTPUT_DIR, "question_map.json")
    with open(question_map_path, 'w', encoding='utf-8') as f:
        # 先将原始ID（键）转为整数，再转为字符串，消除 ".0" 等问题
        question_map_str_keys = {str(int(k)): v for k, v in question_map.items()}
        json.dump(question_map_str_keys, f, indent=4)
    print(f"Saved 'question_map.json' for backend to {question_map_path}")

    # (b) 保存 tag_map.json (知识点名称映射)
    tag_map = {v: f"知识点_{k}" for k, v in question_map.items()}
    tag_map_path = os.path.join(OUTPUT_DIR, "tag_map.json")
    with open(tag_map_path, 'w', encoding='utf-8') as f:
        tag_map_str_keys = {str(k): v for k, v in tag_map.items()}
        json.dump(tag_map_str_keys, f, ensure_ascii=False, indent=4)
    print(f"  - Saved 'tag_map.json'")
    # --- 【新增部分结束】 ---

    # --- 生成训练用标签文件 (保持不变) ---
    print("Generating complete question-to-tag mapping JSON file for training...")
    tags_data = {str(new_id): [new_id] for orig_id, new_id in question_map.items()}
    with open(os.path.join(OUTPUT_DIR, "tags_educoder.json"), 'w') as f:
        json.dump(tags_data, f)

    # --- 处理交互数据 (保持不变) ---
    print("Preprocessing interaction data...")
    interaction_df['challenge_id'] = pd.to_numeric(interaction_df['challenge_id'], errors='coerce')
    interaction_df.dropna(subset=['challenge_id', 'user_id', 'open_time'], inplace=True)
    interaction_df['challenge_id'] = interaction_df['challenge_id'].astype(int)
    interaction_df = interaction_df[interaction_df['challenge_id'].isin(question_map.keys())]
    df = interaction_df[interaction_df['status'].isin([0, 2])].copy()
    df['correctness'] = (df['status'] == 2).astype(int)
    df['timestamp'] = pd.to_datetime(df['open_time'])
    df.sort_values(by=['user_id', 'timestamp'], inplace=True)
    df['open_time_unix'] = df['timestamp'].astype(np.int64) // 10 ** 9
    interaction_counts = df['user_id'].value_counts()
    valid_users = interaction_counts[interaction_counts >= MIN_INTERACTIONS].index
    df = df[df['user_id'].isin(valid_users)]
    print(f"Found {df['user_id'].nunique()} students with valid interactions.")

    # --- 生成训练用交互序列文件 (保持不变) ---
    print("Generating student sequence JSON Lines files for training...")
    df['question_id_mapped'] = df['challenge_id'].map(question_map)
    sequences_df = df.groupby('user_id').agg(
        {'question_id_mapped': list, 'correctness': list, 'open_time_unix': list}).reset_index()
    shuffled_sequences = sequences_df.sample(frac=1, random_state=42)
    train_set = shuffled_sequences.iloc[:int(len(shuffled_sequences) * TRAIN_RATIO)]
    valid_set = shuffled_sequences.iloc[
                int(len(shuffled_sequences) * TRAIN_RATIO):int(len(shuffled_sequences) * (TRAIN_RATIO + VALID_RATIO))]
    test_set = shuffled_sequences.iloc[int(len(shuffled_sequences) * (TRAIN_RATIO + VALID_RATIO)):]

    def save_sequences_to_jsonl(sequences_df, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            for _, row in tqdm(sequences_df.iterrows(), total=len(sequences_df), desc=f"Saving to {output_path}"):
                f.write(json.dumps(
                    [[row['question_id_mapped'][i], row['correctness'][i], row['open_time_unix'][i]] for i in
                     range(len(row['question_id_mapped']))]) + '\n')

    save_sequences_to_jsonl(train_set, os.path.join(OUTPUT_DIR, "educoder.train.json"))
    save_sequences_to_jsonl(valid_set, os.path.join(OUTPUT_DIR, "educoder.valid.json"))
    save_sequences_to_jsonl(test_set, os.path.join(OUTPUT_DIR, "educoder.test.json"))

    print(f"\nPreprocessing finished! All files are in '{OUTPUT_DIR}'.")


if __name__ == '__main__':
    main()