# Copyright 2023, YOUDAO
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
from app.src.algorithm.base.emoti_voice.config.config import Config
from app.src.algorithm.base.emoti_voice.models.prompt_tts_modified.jets import JETSGenerator
from app.src.algorithm.base.emoti_voice.models.prompt_tts_modified.simbert import StyleEncoder
from transformers import AutoTokenizer
import os, torch
import numpy as np
from app.src.algorithm.base.emoti_voice.models.hifigan.get_vocoder import MAX_WAV_VALUE
import soundfile as sf
from yacs.config import load_cfg
from app.src.algorithm.base.emoti_voice.utils.frontend import read_lexicon, g2p_cn_en
from g2p_en import G2p

from app.src.algorithm.utils.download import Downloader, EMOTIVOICE_MODELS


DEFAULT_SPEAKER = 8051
DEFAULT_PROMPT  = "语速很慢"


def get_style_embedding(prompt, tokenizer, style_encoder):
    prompt = tokenizer([prompt], return_tensors="pt")
    input_ids = prompt["input_ids"]
    token_type_ids = prompt["token_type_ids"]
    attention_mask = prompt["attention_mask"]

    with torch.no_grad():
        output = style_encoder(
            input_ids=input_ids,
            token_type_ids=token_type_ids,
            attention_mask=attention_mask,
        )
    style_embedding = output["pooled_output"].cpu().squeeze().numpy()
    return style_embedding


def gen_text_for_ev(text_path, temp_path, **kwargs):
    speaker = kwargs.get("speaker", DEFAULT_SPEAKER)
    prompt  = kwargs.get("prompt", DEFAULT_PROMPT)
    if prompt == "" or prompt is None:
        prompt = DEFAULT_PROMPT

    text_open = open(text_path, "r+", encoding="utf-8")
    temp_open = open(temp_path, "w+", encoding="utf-8")

    lexicon = read_lexicon(Config.lexicon_path)
    g2p = G2p()

    for content in text_open.readlines():
        content = content.strip()
        phoneme = g2p_cn_en(content, g2p, lexicon)
        temp_line = f"{speaker}|{prompt}|{phoneme}|{content}\n"
        temp_open.write(temp_line)

    temp_open.close()
    text_open.close()


class EmotiVoice:
    def __init__(self, param, logger):
        self.param = param
        self.device = self.param["device"]
        if not torch.cuda.is_available():
            self.device = "cpu"

        style_encoder_ckpt_path = self.param["style_encoder_ckpt_path"]
        generator_ckpt_path     = self.param["generator_ckpt_path"]
        bert_path               = self.param["bert_path"]

        self.speaker = self.param["speaker"]

        self.config = Config()
        with open(self.config.model_config_path, 'r') as f:
            self.yaml_conf = load_cfg(f)

        self.yaml_conf.n_vocab = self.config.n_symbols
        self.yaml_conf.n_speaker = self.config.speaker_n_labels

        self.style_encoder_ckpt_path = os.path.join(self.config.checkpoint, "style_encoder", style_encoder_ckpt_path)
        self.generator_ckpt_path     = os.path.join(self.config.checkpoint, "generator", generator_ckpt_path)
        self.bert_path               = os.path.join(self.config.checkpoint, bert_path)

        self.logger = logger
        try:
            self.logger.write_log("interval:0:0:0:0:Model Download")
            self._download()
            self.logger.write_log("interval:0:0:0:0:Model Download End")
        except:
            self.logger.write_log("interval:0:0:0:0:Model Download Error", log_level=logging.ERROR)
            raise ConnectionError("Model Download Error")

    def _download(self):
        model_infos = EMOTIVOICE_MODELS[self.param["model-type"]]
        downloader = Downloader(self.config.checkpoint, model_infos)
        downloader.download()

    def infer(self, input_data, output_data):
        text_path = input_data["text_path"]
        temp_path = input_data["temp_path"]
        prompt    = input_data.get("prompt", None)

        audio_path = output_data["audio_path"]
        gen_text_for_ev(text_path, temp_path, speaker=self.speaker, prompt=prompt)

        setattr(self.config, "bert_path", self.bert_path)

        # style_encoder Model
        style_encoder = StyleEncoder(self.config)
        load_model = torch.load(self.style_encoder_ckpt_path, map_location="cpu")
        model_ckpt = {}
        for key, value in load_model['model'].items():
            new_key = key[7:]
            model_ckpt[new_key] = value
        style_encoder.load_state_dict(model_ckpt, strict=False)

        # generator Model
        generator = JETSGenerator(self.yaml_conf).to(self.device)
        load_model = torch.load(self.generator_ckpt_path, map_location=self.device)
        generator.load_state_dict(load_model['generator'])
        generator.eval()

        with open(self.config.token_list_path, 'r') as f:
            token2id = {t.strip(): idx for idx, t, in enumerate(f.readlines())}

        with open(self.config.speaker2id_path, encoding='utf-8') as f:
            speaker2id = {t.strip(): idx for idx, t in enumerate(f.readlines())}

        # bert Model
        tokenizer = AutoTokenizer.from_pretrained(self.bert_path)

        texts = []
        prompts = []
        speakers = []
        contents = []
        with open(temp_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().split("|")
                speakers.append(line[0])
                prompts.append(line[1])
                texts.append(line[2].split())
                contents.append(line[3])

        # audios' X name
        text_name = os.path.basename(text_path).split('.')[0]
        audio_xname = f"{text_name}_s_{self.speaker}" + "_{order}.wav"

        output_paths = list()

        for i, (speaker, prompt, text, content) in enumerate(zip(speakers, prompts, texts, contents)):

            style_embedding = get_style_embedding(prompt, tokenizer, style_encoder)
            content_embedding = get_style_embedding(content, tokenizer, style_encoder)

            if speaker not in speaker2id:
                continue
            speaker = speaker2id[speaker]

            text_int = [token2id[ph] for ph in text]

            sequence = torch.from_numpy(np.array(text_int)).to(self.device).long().unsqueeze(0)
            sequence_len = torch.from_numpy(np.array([len(text_int)])).to(self.device)
            style_embedding = torch.from_numpy(style_embedding).to(self.device).unsqueeze(0)
            content_embedding = torch.from_numpy(content_embedding).to(self.device).unsqueeze(0)
            speaker = torch.from_numpy(np.array([speaker])).to(self.device)
            with torch.no_grad():

                infer_output = generator(
                    inputs_ling=sequence,
                    inputs_style_embedding=style_embedding,
                    input_lengths=sequence_len,
                    inputs_content_embedding=content_embedding,
                    inputs_speaker=speaker,
                    alpha=1.0
                )
                audio = infer_output["wav_predictions"].squeeze() * MAX_WAV_VALUE
                audio = audio.cpu().numpy().astype('int16')
                output_path = os.path.join(audio_path, audio_xname.format(order=i))
                sf.write(file=output_path,
                         data=audio,
                         samplerate=self.config.sampling_rate)  # h.sampling_rate
                output_paths.append(output_path)
        os.remove(temp_path)
        return output_paths


if __name__ == '__main__':
    print("run!")

    # -d
    # prompt_tts_open_source_joint
    # -c
    # config / joint
    # --checkpoint
    # g_00140000
    # -t
    # test / my_test_for_tts.txt
    input_datas = {
        "config": {
            "device": "cuda",
            "model-type": "emotivoice_v1",
            "generator_ckpt_path": "g_00140000",
            "style_encoder_ckpt_path": "checkpoint_163431",
            "bert_path": "simbert-base-chinese",
            "speaker": 9000,
            "prompt": "亢奋"
        },
        "input": {
            "text_path": r"F:\demo\audio\emoti\long.txt",
            "temp_path": r"F:\demo\audio\emoti\temp.txt"
        },
        "output": {
            "audio_path": r"F:\demo\audio\emoti",
        }

    }

