import ipywidgets as widgets
from IPython.display import display
from typing import TypedDict
from typing import List
from typing import Dict
import os
import json

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

list_1: list[chat_transaction]
select_1: widgets.SelectMultiple
list_2:  list[CommentData]
select_2: widgets.SelectMultiple
title_2  : widgets.Label


def load_chat(live_id: str) -> list[chat_transaction]:
    """指定したパスのJSONファイルを読み込みます。ファイルが存在しない場合は新しいリストを返します。

    Args:
        file_path (str): JSONファイルへのパス。

    Returns:
        List[Any]: JSONから読み込んだデータ、または新しいリスト。
    """
    if os.path.exists(f"{live_id}_chat.json"):
        with open(f"{live_id}_chat.json", 'r', encoding='utf-8') as f:
            data:list[chat_transaction] = json.load(f)
    else:
        data:list[chat_transaction] = []  # ファイルが存在しない場合は新しいリストを作成
    return data

def load_each_chat(live_id: str) -> Dict[str, List[CommentData]]:
    """指定したパスのJSONファイルを読み込みます。ファイルが存在しない場合は新しいリストを返します。

    Args:
        file_path (str): JSONファイルへのパス。

    Returns:
        List[Any]: JSONから読み込んだデータ、または新しいリスト。
    """
    if os.path.exists(f"{live_id}_each_chat.json"):
        with open(f"{live_id}_each_chat.json", 'r', encoding='utf-8') as f:
            data:Dict[str, List[CommentData]] = json.load(f)
    else:
        data:Dict[str, List[CommentData]] = {}  # ファイルが存在しない場合は新しいリストを作成
    return data

# クリックイベントのハンドラー
def update_list(live_id:str):
    global list_1
    global select_1 
    # "addList"を10回list_1に追加
    list_1= load_chat(live_id)[:-150]
    scroll_end_message = [f"もうすぐスクロール端です：{i}" for i in range(5)] if 30<len(list_1) else []
    list_all = scroll_end_message + [f"{el['display_name']}：{el['chat']}" for el in list_1] + scroll_end_message[::-1]
    # select_1のoptionsを更新
    select_1.options = list_all

def analyze(change):
    global list_1
    global list_2 
    global select_1 
    global select_2 
    global title_2 
    global チャットGPTハンドラー
    print('aaa')
    title_2.value = str('aaa')
    # if change['new'] and load_each_chat(live_id) in change['new'].split('：')[0]:
    #     # "addList"を10回list_1に追加
    #     list_2= load_each_chat(live_id)[change['new'].split('：')[0]]
    #     scroll_end_message = [f"もうすぐスクロール端です：{i}" for i in range(5)] if 30<len(list_2) else []
    #     list_all = scroll_end_message + [f"{el['date']}：{el['comment']}" for el in list_2] + scroll_end_message[::-1]
    #     # select_1のoptionsを更新
    #     select_2.options = list_all
    #     # print('Selected item:', change['new'])
    select_1.value = ()

def set_ui():
    # リストの内容
    global list_1
    global list_2 
    global select_1 
    global select_2 
    global title_2 
    list_1 = ['aaaaaaaaa：あああ']
    list_2 = []

    # スクロール端メッセージの追加
    scroll_end_message = [f"1{i}" for i in range(5)] if 30< len(list_2) else [] 
    list_1_all = scroll_end_message + list_1 + scroll_end_message[::-1]
    list_2_all = scroll_end_message + list_2 + scroll_end_message[::-1]

    # SelectMultiple widgetsの作成
    select_1 = widgets.SelectMultiple(
        options=list_1_all,
        description='',  # リストタイトルを非表示
        layout=widgets.Layout(width='auto', height='580px', overflow_y='auto')  # スクロールを追加
    )

    select_2 = widgets.SelectMultiple(
        options=list_2_all,
        layout=widgets.Layout(width='auto', height='500px', overflow_y='auto')  # スクロールを追加
    )


    # イベントハンドラーの追加
    select_1.observe(analyze, 'value')

    # タイトルウィジェットの作成
    title_2 = widgets.Label(
        value='List 2', 
        layout=widgets.Layout(width='auto')
    )

    # フッターウィジェットの作成
    footer_2 = widgets.Label(
        value='Info: This is a footer', 
        layout=widgets.Layout(width='auto')
    )

    # 右側のカラムを作成（タイトル、リスト、フッターを含む）
    right_column = widgets.VBox([title_2, select_2, footer_2], layout=widgets.Layout(width='50%', overflow='auto'))

    # 左側のカラムを作成（リストのみ）
    left_column = widgets.VBox([select_1], layout=widgets.Layout(width='50%', overflow='auto'))

    # 2カラムのレイアウトを作成
    two_columns = widgets.HBox([left_column, right_column], layout=widgets.Layout(width='100%', overflow='auto'))

    display(two_columns)

# set_ui()