# ... (上一轮回复中提供的最终版 run.py) ...
# 它应该只包含最简单的前缀名
import os
from argparse import ArgumentParser
import aakt_entry
prefix_dict = {'educoder': ['educoder', 'tags_educoder', 'Educoder-Final']}
arg_dict = {'--max_seq_len': 500, '--n_layer': 4, '--n_embd': 128, '--n_head': 8, '--epochs': 10, '--learning_rate': 1e-3, '--global_batch_size': 64, '--mini_batch_size': 16, '--eval': 1}
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--dataset', type=str, default='educoder')
    args = parser.parse_args()
    model_dataset = args.dataset
    assert model_dataset in prefix_dict.keys()
    model_args = arg_dict
    fp, tp, rp = prefix_dict[model_dataset]
    cmd = f'python "{aakt_entry.__file__}" --file_prefix "{fp}" --tag_prefix "{tp}" --record_prefix "{rp}"'
    for k, v in model_args.items(): cmd += f' {k} {v}'
    print(f"Executing command:\n{cmd}")
    os.system(cmd)