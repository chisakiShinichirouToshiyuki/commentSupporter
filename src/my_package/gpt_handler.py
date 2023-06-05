from typing import List
from typing import Literal
from typing import TypedDict
import copy
import openai


class message(TypedDict):
    """チャットメッセージ用の型定義クラス。

    Attributes
    ----------
    role : Literal['system','user','assistant']
        メッセージの役割。
    content : str
        メッセージの内容。
    """
    role: Literal['system','user','assistant']
    content:str

class チャットGPTハンドラークラス:
    """チャットGPT-3との対話を管理するクラス。

    Parameters
    ----------
    api_key : str
        OpenAI APIのAPIキー。
    作業依頼 : str
        チャットの初期メッセージ。
    モデル : str, optional
        チャット補完用のモデル。デフォルトは 'gpt-3.5-turbo'。
    温度 : int, optional
        チャット補完の温度設定。デフォルトは 1。
    """
    def __init__(self, api_key:str, 作業依頼:str, モデル:str='gpt-3.5-turbo', 温度:int =1):
        self._api_key:str = api_key
        self._model:str = モデル
        self._temperature:int = 温度
        # 作業依頼のシステムメッセージでチャットを初期化。
        self._messages:List[message] = [
            {
                "role": "system",
                "content": 作業依頼
            }
        ]

    @property
    def api_key(self):
        """APIキーを取得する。

        Returns
        -------
        str
            APIキー。
        """
        return self._api_key

    def ユーザーメッセージの追加(self, メッセージ:str):
        """ユーザーのメッセージを追加する。

        Parameters
        ----------
        メッセージ : str
            追加するメッセージの内容。
        """
        self._messages.append({
            "role": "user",
            "content": メッセージ
        })

    def chatGPT返信の追加(self, 返信:str):
        """ChatGPTの返信を追加する。

        Parameters
        ----------
        返信 : str
            追加する返信の内容。
        """
        self._messages.append({
            "role": "assistant",
            "content": 返信
        })

    def チャットGPTへ問いかけ(self, comments:List[str]):
        """ChatGPTに問いかけて、その結果を返す。

        Parameters
        ----------
        comments : List[str]
            追加するコメントのリスト。

        Returns
        -------
        str
            ChatGPTからの返信。
        """
        openai.api_key = self._api_key
        messages:List[message] = copy.deepcopy(self._messages)
        messages[-1]["content"] = messages[-1]["content"] + "\n" + "\n".join(comments)
        prompt_setting = {
            'model': self._model,
            'messages': messages,
            'temperature': self._temperature, 
        }
        res:str = openai.ChatCompletion.create(**prompt_setting)["choices"][0]["message"]["content"] # type: ignore
        assert isinstance(res, str)
        return res
