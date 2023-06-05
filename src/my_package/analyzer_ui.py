from IPython.display import display
import ipywidgets as widgets
from typing import TypedDict, List, Dict, Union
from typing import TYPE_CHECKING
import json
import os

from .gpt_handler import チャットGPTハンドラークラス

class chat_transaction(TypedDict):
    user_id: str
    display_name: str
    chat: str
    date: str

class CommentData(TypedDict):
    displayName: str
    date: str
    comment: str
    userId: str

class AnalyzerUi:
    def __init__(self,チャットGPTハンドラー:チャットGPTハンドラークラス, live_id:str):
        self._list_1:list[chat_transaction] = []
        self._list_2: list[CommentData] = []
        self._select_1:widgets.SelectMultiple
        self._select_2:widgets.SelectMultiple
        self._title_2:widgets.Label
        self._footer_2:widgets.Label
        self._live_id = live_id
        self._gpt_handler:チャットGPTハンドラークラス = チャットGPTハンドラー
        self._set_ui()

    def _set_ui(self):
        """
        チャットの分析とUIのセットアップを行います。

        Parameters
        ----------
        チャットGPTハンドラー_local : チャットGPTハンドラークラス
            チャット分析を管理するためのハンドラー。
        local_live_id : str
            ライブIDを指定します。このIDはチャットの取得元を識別します。

        """
        
        self._list_1 = ['ロード中です：ロード中です']
        self._list_2 = []

        scroll_end_message = [f"1{i}" for i in range(5)] if 30< len(self._list_2) else [] 
        list_1_all = scroll_end_message + self._list_1 + scroll_end_message[::-1]
        list_2_all = scroll_end_message + self._list_2 + scroll_end_message[::-1]

        self._select_1 = widgets.SelectMultiple(
            options=list_1_all,
            description='',
            layout=widgets.Layout(width='auto', height='532px', overflow_y='auto')
        )

        self._select_2 = widgets.SelectMultiple(
            options=list_2_all,
            layout=widgets.Layout(width='auto', height='500px', overflow_y='auto')
        )

        self._select_1.observe(self._analyze, 'value')

        self._title_2 = widgets.Label(
            value="コメント主：", 
            layout=widgets.Layout(width='auto')
        )

        self._footer_2 = widgets.Label(
            value="chatGPT：", 
            layout=widgets.Layout(width='auto')
        )

        right_column = widgets.VBox([self._title_2, self._select_2, self._footer_2], layout=widgets.Layout(width='50%', overflow='auto'))

        update_button = widgets.Button(description="Update",
                                            button_style='',
                                            style=widgets.ButtonStyle(button_color='hsl(210, 50%, 90%)'))
        update_button.on_click(self._update) 

        footer_1 = widgets.HBox([widgets.Label(value=''), update_button], layout=widgets.Layout(width='auto'))

        left_column = widgets.VBox([self._select_1, footer_1], layout=widgets.Layout(width='50%', overflow='auto'))

        two_columns = widgets.HBox([left_column, right_column], layout=widgets.Layout(width='100%', overflow='auto'))

        display(two_columns)

    def _load_chat(self) -> list[chat_transaction]:
        """指定したパスのJSONファイルを読み込みます。ファイルが存在しない場合は新しいリストを返します。

        Args:
            file_path (str): JSONファイルへのパス。

        Returns:
            List[Any]: JSONから読み込んだデータ、または新しいリスト。
        """
        if os.path.exists(f"{self._live_id}_chat.json"):
            with open(f"{self._live_id}_chat.json", 'r', encoding='utf-8') as f:
                data:list[chat_transaction] = json.load(f)
        else:
            data:list[chat_transaction] = []  # ファイルが存在しない場合は新しいリストを作成
        return data

    def _load_each_chat(self) -> Dict[str, List[CommentData]]:
        """指定したパスのJSONファイルを読み込みます。ファイルが存在しない場合は新しいリストを返します。

        Args:
            file_path (str): JSONファイルへのパス。

        Returns:
            List[Any]: JSONから読み込んだデータ、または新しいリスト。
        """
        if os.path.exists(f"{self._live_id}_each_chat.json"):
            with open(f"{self._live_id}_each_chat.json", 'r', encoding='utf-8') as f:
                data:Dict[str, List[CommentData]] = json.load(f)
        else:
            data:Dict[str, List[CommentData]] = {}  # ファイルが存在しない場合は新しいリストを作成
        return data

    def _update(self, button:widgets.Button):
        """
        クリックイベントのハンドラーです。このメソッドは、ユーザーが更新ボタンをクリックしたときに呼び出されます。

        Parameters
        ----------
        button : widgets.Button
            クリックされたボタンのインスタンス。

        """
        try:
            # load_chatの詳細が不明なため、一時的に空リストを返すようにしています。
            # 適切なコードに置き換えてください。
            self._list_1= self._load_chat()[-150:]
            scroll_end_message = [f"もうすぐスクロール端です：{i}" for i in range(5)] if 30<len(self._list_1) else []
            list_all = scroll_end_message + [f"{el['display_name']}：{el['chat']}" for el in self._list_1] + scroll_end_message[::-1]
            self._select_1.options = list_all
        except Exception as error:
            print('----------')
            print('error')
            print(error)

    def _analyze(self, change):
        """
        ユーザーの選択に基づいてチャットを分析し、UIを更新します。

        Parameters
        ----------
        change : dict
            observeメソッドによって生成される変更の辞書。

        """
        if change['new']:
            name:str =change['new'][0].split('：')[0]
            assert isinstance(name, str)
            
            # load_each_chatの詳細が不明なため、一時的に空の辞書を返すようにしています。
            # 適切なコードに置き換えてください。
            if name in self._load_each_chat():
                # "addList"を10回list_1に追加
                self._footer_2.value= "chatGPT：分析中..."
                self._list_2= self._load_each_chat()[name]
                scroll_end_message = [f"もうすぐスクロール端です：{i}" for i in range(5)] if 30<len(self._list_2) else []
                list_all = scroll_end_message + [f"{el['date']}：{el['comment']}" for el in self._list_2] + scroll_end_message[::-1]
                # select_1のoptionsを更新
                self._select_2.options = list_all
                self._title_2.value =  "コメント主："+name
                self._footer_2.value= "chatGPT：" + self._gpt_handler.チャットGPTへ問いかけ([f"{el['comment']}" for el in self._list_2][::-1])
