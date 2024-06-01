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

import re
from app.src.algorithm.base.emoti_voice.utils.frontend_cn import g2p_cn, re_digits, tn_chinese
from app.src.algorithm.base.emoti_voice.utils.frontend_en import get_eng_phoneme

# Thanks to GuGCoCo and PatroxGaurab for identifying the issue: 
# the results differ between frontend.py and frontend_en.py. Here's a quick fix.
#re_english_word = re.compile('([a-z\-\.\'\s,;\:\!\?]+|\d+[\d\.]*)', re.I)
re_english_word = re.compile('([^\u4e00-\u9fa5]+|[ \u3002\uff0c\uff1f\uff01\uff1b\uff1a\u201c\u201d\u2018\u2019\u300a\u300b\u3008\u3009\u3010\u3011\u300e\u300f\u2014\u2026\u3001\uff08\uff09\u4e00-\u9fa5]+)', re.I)


def read_lexicon(lex_path):
    lexicon = {}
    with open(lex_path) as f:
        for line in f:
            temp = re.split(r"\s+", line.strip("\n"))
            word = temp[0]
            phones = temp[1:]
            if word.lower() not in lexicon:
                lexicon[word.lower()] = phones
    return lexicon


def g2p_cn_en(text, g2p, lexicon):
    # Our policy dictates that if the text contains Chinese, digits are to be converted into Chinese.
    text=tn_chinese(text)
    parts = re_english_word.split(text)
    parts=list(filter(None, parts))
    tts_text = ["<sos/eos>"]
    chartype = ''
    text_contains_chinese = contains_chinese(text)
    for part in parts:
        if part == ' ' or part == '': continue
        if re_digits.match(part) and (text_contains_chinese or chartype == '') or contains_chinese(part):
            if chartype == 'en':
                tts_text.append('eng_cn_sp')
            phoneme = g2p_cn(part).split()[1:-1]
            chartype = 'cn'
        elif re_english_word.match(part):
            if chartype == 'cn':
                if "sp" in tts_text[-1]:
                    ""
                else:
                    tts_text.append('cn_eng_sp')
            phoneme = get_eng_phoneme(part, g2p, lexicon, False).split()
            if not phoneme :
                # tts_text.pop()
                continue
            else:
                chartype = 'en'
        else:
            continue
        tts_text.extend( phoneme )

    tts_text=" ".join(tts_text).split()
    if "sp" in tts_text[-1]:
        tts_text.pop()
    tts_text.append("<sos/eos>")

    return " ".join(tts_text)


def contains_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    match = re.search(pattern, text)
    return match is not None
