import argparse
import json
import os

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from tqdm import tqdm
from transformers import TrainingArguments, Trainer

# 确保这些导入路径是正确的
from dataset.AlternateDataset import KTDataset
from dataset.QuestionTags import QuestionTags
from models.AAKT import AAKT


def collate_fn(batch_of_data):
    # 这个函数将 __getitem__ 返回的张量列表，聚合成一个批次
    return {
        "input_ids": torch.cat([data[0] for data in batch_of_data], dim=0).long(),
        "input_times": torch.cat([data[1] for data in batch_of_data], dim=0).float(),
        "labels_kts": torch.cat([data[2] for data in batch_of_data], dim=0).long(),
        "labels_tags": torch.cat([data[3] for data in batch_of_data], dim=0).float(),
    }


def preprocess_logits_for_metrics(predictions, labels):
    """
    这个函数在训练和评估时接收到的 predictions 元组长度不同。
    训练时: (total_loss, loss_kts, loss_tags, preds_kts) -> 长度为4
    评估时: (loss_kts, loss_tags, preds_kts) -> 长度为3
    我们需要处理这两种情况。
    """
    if len(predictions) == 4:
        # 训练时的情况，忽略第一个总损失
        _total_loss, loss_kts, loss_tags, preds_kts = predictions
    else:
        # 评估时的情况
        loss_kts, loss_tags, preds_kts = predictions

    # 后续逻辑保持不变
    probs_kts = 1 / (torch.exp(preds_kts[:, :, 0] - preds_kts[:, :, 1]) + 1)
    return loss_kts, loss_tags, probs_kts


def compute_metrics(eval_preds):
    loss_kts_np, loss_tags_np, probs_kts = eval_preds.predictions
    labels_kts = eval_preds.label_ids

    # 【核心修改】对 NumPy 数组使用 .mean() 方法
    loss_kts = loss_kts_np.mean()
    loss_tags = loss_tags_np.mean()

    labels_kts = labels_kts.reshape(-1)
    probs_kts = probs_kts.reshape(-1)

    non_pad_indices = np.nonzero(labels_kts != -100)
    labels_kts = labels_kts[non_pad_indices]
    probs_kts = probs_kts[non_pad_indices]

    if len(labels_kts) == 0:
        return {"loss_kts": loss_kts, "loss_tags": loss_tags, "ACC": 0, "AUC": 0, "RMSE": 0, "num_kts": 0}

    assert labels_kts.shape[0] == probs_kts.shape[0], f'{labels_kts.shape}, {probs_kts.shape}'

    acc = ((probs_kts > 0.5) == labels_kts).mean()

    # 为 roc_auc_score 增加一个检查，确保标签不单一
    if len(np.unique(labels_kts)) < 2:
        auc = 0.5  # 如果所有标签都一样，AUC没有意义，设为0.5
    else:
        auc = roc_auc_score(labels_kts, probs_kts)

    rmse = np.sqrt(((labels_kts - probs_kts) ** 2).mean())

    result = {"loss_kts": loss_kts,
              "loss_tags": loss_tags,
              "ACC": acc,
              "AUC": auc,
              "RMSE": rmse,
              "num_kts": len(labels_kts)}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='parse args for modeling and training')

    parser.add_argument('--without_tags', type=bool, default=False)
    parser.add_argument('--without_times', type=bool, default=False)
    parser.add_argument('--eval', type=int, default=1)  # 默认设为1

    parser.add_argument('--max_seq_len', type=int, default=128)  # 减少默认值以加快调试
    parser.add_argument('--n_layer', type=int, default=4)
    parser.add_argument('--n_embd', type=int, default=128)
    parser.add_argument('--n_head', type=int, default=8)

    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--learning_rate', type=float, default=1e-3)
    parser.add_argument('--n_devices', type=int, default=1)
    parser.add_argument('--global_batch_size', type=int, default=64)
    parser.add_argument('--mini_batch_size', type=int, default=16)

    parser.add_argument('--file_prefix', type=str, required=True)
    parser.add_argument('--tag_prefix', type=str, required=True)
    parser.add_argument('--record_prefix', type=str, required=True)

    args = parser.parse_args()
    print(f"args: {json.dumps(vars(args), ensure_ascii=False, indent=4)}")

    eval = args.eval == 1

    file_prefix = args.file_prefix
    tag_prefix = args.tag_prefix
    record_prefix = args.record_prefix

    max_seq_len = args.max_seq_len
    n_layer = args.n_layer
    n_embd = args.n_embd
    n_head = args.n_head
    rotary_dim = n_embd // n_head // 2

    output_dir = f"output-{record_prefix}"
    print(f"output_dir: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    question_tags = QuestionTags(tag_prefix=tag_prefix)
    usage2dataset = {
        usage: KTDataset(question_tags, max_seq_len, usage=usage, file_prefix=file_prefix)
        for usage in ["train", "valid", "test"]
    }

    # --- 【核心修改】---
    # 由于我们重构了 KTDataset，它不再有 total_num_kts 属性。
    # 这段代码仅用于打印日志，对训练无影响，我们将其简化。
    usage2nums = {"names": ['samples']}
    print(f"Dataset stats (number of samples):")
    for usage, dataset in usage2dataset.items():
        print(f"  {usage}: {len(dataset)}")
        usage2nums[usage] = [len(dataset)]
    # --- 【修改结束】---

    learning_rate = args.learning_rate
    n_devices = args.n_devices
    global_batch_size = args.global_batch_size
    mini_batch_size = args.mini_batch_size
    gradient_accumulation_steps = global_batch_size // (n_devices * mini_batch_size) if n_devices > 0 else 1

    epochs = args.epochs
    # 确保 len(usage2dataset["train"]) > 0
    if len(usage2dataset["train"]) > 0:
        total_training_steps = np.math.ceil(len(usage2dataset["train"]) / global_batch_size) * epochs
        logging_steps = max(1, int(total_training_steps / epochs / 10))
    else:
        total_training_steps = 1
        logging_steps = 1

    print(f"training epochs = {epochs:.2f}")

    model = AAKT(
        num_questions=question_tags.num_questions,
        num_tags=question_tags.num_tags,
        max_seq_len=max_seq_len,
        with_tags=not args.without_tags,
        with_times=not args.without_times,
        n_layer=n_layer,
        n_embd=n_embd,
        n_head=n_head,
        rotary_dim=rotary_dim
    )
    print(f"Model created.")

    # 检查是否有可用的GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model.to(device)

    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        num_train_epochs=epochs,
        learning_rate=learning_rate,
        lr_scheduler_type='cosine',
        per_device_train_batch_size=mini_batch_size,
        per_device_eval_batch_size=mini_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        # eval_accumulation_steps=1, # 较新版本的transformers可能不支持
        fp16=torch.cuda.is_available(),  # 仅在有GPU时启用fp16
        warmup_ratio=0.1,
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="AUC",
        greater_is_better=True,
        log_level='info',
        logging_steps=logging_steps,
        dataloader_num_workers=0,  # 在Windows上设为0通常更稳定
        label_names=["labels_kts"],
        report_to="none"  # 避免连接wandb等
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=usage2dataset["train"],
        eval_dataset=usage2dataset["valid"],
        compute_metrics=compute_metrics,
        data_collator=collate_fn,
        preprocess_logits_for_metrics=preprocess_logits_for_metrics,
    )

    print("Starting training...")
    train_output = trainer.train()

    print("Starting final evaluation...")
    test_result = trainer.evaluate(usage2dataset["test"], metric_key_prefix="test")
    print("Final test results:", test_result)

    # 保存模型和记录
    best_model_path = trainer.state.best_model_checkpoint
    if best_model_path:
        print(f"Best model saved at: {best_model_path}")
        state_dict_path = os.path.join(best_model_path, "pytorch_model.bin")
        if os.path.exists(state_dict_path):
            state_dict = torch.load(state_dict_path)
            if 'model.wte.weight' in state_dict:
                emb_weight = state_dict['model.wte.weight'].detach().cpu().numpy()
                os.makedirs('emb_weight', exist_ok=True)
                np.save(f'emb_weight/{record_prefix}.npy', emb_weight)
                print("Embedding weights saved.")

    results = {}
    results.update(train_output._asdict())
    results.update(test_result)
    record = {
        output_dir: {
            "args": vars(args),
            "usage2nums": usage2nums,
            "results": results,
            "best_model_checkpoint": trainer.state.best_model_checkpoint,
        }
    }

    os.makedirs('records', exist_ok=True)
    record_file = f'records/{record_prefix}.json'
    records = {}
    if os.path.exists(record_file):
        with open(record_file, "r") as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                pass  # 文件为空或格式错误
    records.update(record)
    with open(record_file, "w") as f:
        f.write(json.dumps(records, ensure_ascii=False, indent=4) + "\n")

    print("Script finished successfully.")