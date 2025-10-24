import json


class QuestionTags:
    def __init__(self, tag_prefix: str, path=None):
        # 遵循原始代码的路径逻辑
        if path is None:
            path = f"autodl-tmp/{tag_prefix}.json"

        with open(path, "r") as f:
            # self.tags 的键是字符串 '0', '1', ...
            self.tags = json.load(f)

        # num_questions 应该是标签文件中定义的问题总数
        self.num_questions = len(self.tags)

        # 计算 num_tags
        max_tag = 0
        for tag_list in self.tags.values():
            if tag_list:
                max_tag = max(max_tag, max(tag_list))
        self.num_tags = max_tag + 1

        print(f"Tags loaded: num_questions = {self.num_questions}, num_tags = {self.num_tags}")

    def __getitem__(self, question):
        # 【核心Bug修复】
        # question 是一个整数，我们必须将它转换为字符串来查询JSON加载的字典
        # 同时使用 .get() 方法来避免当某个question不存在于tags文件时直接崩溃
        return self.tags.get(str(question), [])

    def __len__(self):
        return len(self.tags)