import os
import logging

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline

from app.utils.paths import Paths
from app.src.algorithm.utils.download import Downloader, HELSINKI_NLP_MODELS

_FACENET_ROOT = os.path.join(Paths.ALGORITHM, "base", "helsinki_nlp", "checkpoint")

TASK2MODEL = {
    "opus-mt-zh-en": os.path.join(_FACENET_ROOT, "opus-mt-zh-en"),
    "opus-mt-en-zh": os.path.join(_FACENET_ROOT, "opus-mt-en-zh")
}


class HelsinkiModel:
    def __init__(self, param, logger):
        self.task = param["task"]
        assert self.task in TASK2MODEL.keys(), "Please check the task!"
        self.model_path = TASK2MODEL[self.task]
        self.logger = logger
        try:
            self.logger.write_log("interval:0:0:0:0:Model Download")
            self._download()
            self.logger.write_log("interval:0:0:0:0:Model Download End")
        except:
            self.logger.write_log("interval:0:0:0:0:Model Download Error", log_level=logging.ERROR)
            raise ConnectionError("Model Download Error")
        try:
            self.logger.write_log("interval:0:0:0:0:Model Load")
            # 创建tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            # 创建模型
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)

            self.pipeline = pipeline("translation", model=self.model, tokenizer=self.tokenizer)
            self.logger.write_log("interval:0:0:0:0:Model Load End")
        except:
            self.logger.write_log("interval:0:0:0:0:Model Load Error", log_level=logging.ERROR)
            raise RuntimeError("Model Load Error")

    def _download(self):
        model_infos = HELSINKI_NLP_MODELS[self.task]
        downloader = Downloader(self.model_path, model_infos)
        downloader.download()

    def translate(self, text):
        result = self.pipeline(text)
        return result


if __name__ == '__main__':
    param = {
        "task": "opus-mt-zh-en"
    }
    zh2en = HelsinkiModel(param)
    chinese = """
    大家好，欢迎来到今天的直播间！我是你们的主播王小二，非常荣幸能为大家介绍一款近期备受瞩目的产品。这款产品采用了先进的监视技术，不仅具有卓越的性能，而且设计人性化，操作简便，无论是日常使用还是特定场合，都能轻松满足您的需求。
    想象一下，在忙碌的工作日，有了它，您的生活将变得更加便捷高效；在休闲的周末时光，它也能为您增添一份乐趣和舒适。无论您是在家里享受悠闲时光，还是在办公室奋斗，甚至是在外出旅行，它都能成为您不可或缺的得力助手。
    而且，今天下单的朋友们还有特别的优惠哦！数量有限，先到先得，千万不要错过这个难得的机会。如果您对产品有任何疑问或疑虑，都可以在直播间里留言告诉我，我会尽我所能为您解答。
    最后，非常感谢大家的观看和支持！希望你们会喜欢今天推荐的产品，也期待下次直播再与大家相见。别忘了关注我们的直播间，更多好货等你来发现！
    """
    result = zh2en.translate(chinese)

    param = {
        "task": "opus-mt-en-zh"
    }
    en2zh = HelsinkiModel(param)
    english = """
    Hello everyone, welcome to today's live broadcast! I'm your host, XXX, and I'm thrilled to introduce you to a recently highly anticipated product. This product utilizes advanced XXX technology, boasting both superior performance and user-friendly design. Whether it's for daily use or specific occasions, it can easily meet your needs.
    Imagine having it with you on a busy workday, making your life more convenient and efficient. Or on a leisurely weekend, adding a touch of fun and comfort to your time. Whether you're enjoying a relaxing moment at home, hustling in the office, or even traveling, it will become your indispensable helper.
    And for those of you who place an order today, there's a special discount waiting for you! Quantities are limited, so act fast to avoid disappointment. If you have any questions or concerns about the product, feel free to leave a message in the live broadcast, and I'll do my best to address them.
    Lastly, I want to express my heartfelt gratitude to everyone for watching and supporting us! I hope you'll love the product I've recommended today, and I look forward to seeing you again in our next live broadcast. Don't forget to follow our live broadcast room for more great deals waiting for you to discover!
    """
    result = en2zh.translate(english)
    print(result[0]['translation_text'])


