from typing import TypedDict
from typing import Literal
import copy
import openai


class message(TypedDict):
    role: Literal['system','user','assistant']
    content:str



class チャットGPTハンドラークラス:
    def __init__(self, api_key:str, 作業依頼:str, モデル:str='gpt-3.5-turbo', 温度:int =1):
        # self.作業依頼:str = 作業依頼
        self._api_key:str = api_key
        self.モデル:str = モデル
        self.温度:int = 温度
        self.messages:list[message] = [
            {
                "role": "system",
                "content": 作業依頼
            }
        ]

    @property
    def api_key(self):
        return self._api_key

    def ユーザーメッセージの追加(self, メッセージ:str):
        self.messages.append({
            "role": "user",
            "content": メッセージ
        })
        
    def chatGPT返信の追加(self, 返信:str):
        self.messages.append({
            "role": "assistant",
            "content": 返信
        })

    def チャットGPTへ問いかけ(self, comments:list[str]):
        openai.api_key = self._api_key
        messages:list[message] = copy.deepcopy(self.messages)
        messages[-1]["content"] = messages[-1]["content"] + "\n" + "\n".join(comments)
        prompt_setting = {
            'model': self.モデル,
            'messages': messages,
            'temperature': self.温度, 
        }
        res = openai.ChatCompletion.create(**prompt_setting)["choices"][0]["message"]["content"]
        assert isinstance(res, str)
        return res