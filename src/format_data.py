import time
from datetime import datetime, timedelta, timezone
from typing import Dict
from typing import List
from typing import Any
from typing import Literal
from typing import Union
from typing import TypedDict
import os
import json
from multiprocessing import Queue
import glob

import copy
from commentSupporter.src.GptHandler import チャットGPTハンドラークラス


class CommentData(TypedDict):
    displayName: str
    date: str
    comment: str
    userId: str


class Thumbnail(TypedDict):
    url: str
    width: float
    height: float


class AccessibilityData(TypedDict):
    label: str


class WebCommandMetadata(TypedDict):
    ignoreNavigation: bool


class CommandMetadata(TypedDict):
    webCommandMetadata: WebCommandMetadata


class LiveChatItemContextMenuEndpoint(TypedDict):
    params: str


class ContextMenuEndpoint(TypedDict):
    clickTrackingParams: str
    commandMetadata: CommandMetadata
    liveChatItemContextMenuEndpoint: LiveChatItemContextMenuEndpoint


class Text(TypedDict):
    text: str


class Message(TypedDict):
    runs: List[Text]


class AuthorName(TypedDict):
    simpleText: str


class AuthorPhoto(TypedDict):
    thumbnails:  List[Thumbnail]


class Renderer(TypedDict):
    message: Message
    authorName: AuthorName
    authorPhoto: AuthorPhoto
    contextMenuEndpoint: ContextMenuEndpoint
    id: str
    timestampUsec: str
    authorExternalChannelId: str
    contextMenuAccessibility: AccessibilityData
    trackingParams: str


class Item(TypedDict):
    liveChatTextMessageRenderer: Renderer


class AddChatItemAction(TypedDict):
    item: Item
    clientId: str


class Action(TypedDict):
    clickTrackingParams: str
    addChatItemAction: AddChatItemAction


class ReplayChatItemAction(TypedDict):
    actions: List[Action]


class CommentRowData(TypedDict):
    replayChatItemAction: ReplayChatItemAction
    videoOffsetTimeMsec: str
    isLive: bool

class chat_transaction(TypedDict):
    user_id: str
    display_name: str
    chat: str
    date: str


def load_json(file_path: str) -> List[chat_transaction]:
    """指定したパスのJSONファイルを読み込みます。ファイルが存在しない場合は新しいリストを返します。

    Args:
        file_path (str): JSONファイルへのパス。

    Returns:
        List[Any]: JSONから読み込んだデータ、または新しいリスト。
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data:List[chat_transaction] = json.load(f)
    else:
        data:List[chat_transaction] = []  # ファイルが存在しない場合は新しいリストを作成

    return data


def update_and_save_json(file_path: str, data: List[chat_transaction]|Dict[str, List[CommentData]]) -> None:
    """リストに要素を追加し、それを同じJSONファイルに書き込みます。

    Args:
        file_path (str): JSONファイルへのパス。
        data (List[Any]): 追加するデータ。

    Returns:
        None
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_json_file(file_path: str, new_chats: List[chat_transaction]) -> None:
    """JSONファイルからデータを読み込み、新たな要素を追加し、それを同じファイルに保存します。

    Args:
        file_path (str): JSONファイルへのパス。
        new_element (Any): 追加する新しい要素。

    Returns:
        None
    """
    # JSONファイルを読み込み。ファイルが存在しない場合は新しいリストを作成。
    data = load_json(file_path)

    # リストに新たな要素を含むlistを末尾に結合。ただしdataはimmutableなので、新しいlistを作成する。
    data = data + new_chats

    # 結果を同じファイルに書き込み
    update_and_save_json(file_path, data)





def text_reader(file_path: str) -> str:
    """
        localファイルをtextとして取得する
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def split_text(text: str) -> List[str]:
    """
        textReaderで読み込んだtextを、行ごとに分割して、配列に格納する
    """
    return text.split('\n')


def convert_json_to_dict(comment: CommentRowData) -> CommentData:
    action = comment["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]
    return {
        # 'userId': action["authorExternalChannelId"],
        'userId': action["authorName"]["simpleText"],
        'displayName': action["authorName"]["simpleText"],
        'date': datetime.fromtimestamp(int(action["timestampUsec"]) / 1_000_000).strftime("%H:%M"),
        'comment': action["message"]["runs"][0]["text"]
    }


def translator(comments: List[str]) -> Dict[str, List[CommentData]]:
    user_comments: Dict[str, List[CommentData]] = {}
    for comment in comments:
        try:
            data: CommentRowData = json.loads(comment)
            current_comment = convert_json_to_dict(data)
            user_id = current_comment['userId']
            if user_id not in user_comments:
                user_comments[user_id] = [current_comment]
            else:
                user_comments[user_id].append(current_comment)
        except json.JSONDecodeError:
            # print('----------')
            # print('error')
            # print(comment)
            # print('----------')
            pass
    return user_comments


def update_dictionary(user_comments: Dict[str, List[CommentData]], comments: List[str],live_id: str) -> Dict[str, List[CommentData]]:
    new_chat_transactions: List[chat_transaction] = []
    for comment in comments:
        try:
            data: CommentRowData = json.loads(comment)
            action = data["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]
            # user_id = action["authorExternalChannelId"]
            user_id = action["authorName"]["simpleText"]
            current_comment: CommentData = {
                "displayName": action["authorName"]["simpleText"],
                "date": datetime.fromtimestamp(int(action["timestampUsec"]) / 1_000_000).strftime("%H:%M"),
                "comment": ' '.join([(run['text'] if 'text' in run else ' ') for run in action["message"]["runs"]]),
                "userId": user_id
            }
            if user_id not in user_comments:
                user_comments[user_id] = [current_comment]
            elif not any(d['date'] == current_comment['date'] for d in user_comments[user_id]):
                user_comments[user_id].append(current_comment)
            new_chat_transactions.append({
                "user_id": current_comment['userId'],
                "chat": current_comment['comment'],
                "date": current_comment['date'],
                "display_name": current_comment['userId'],
                # "display_name": current_comment['displayName'],
            })
        # except:
        except Exception as error:
            pass
            # print('----------')
            # print('error')
            # print(error)
            # print(comment)
            # print('----------')
    try :
        update_json_file(f'{live_id}_chat.json', new_chat_transactions)
        update_and_save_json(f'{live_id}_each_chat.json', user_comments)
    # except:
    except Exception as error:
        pass
        # print('----------')
        # print('error')
        # print(error)
        # print(comment)
        # print('----------')
    return user_comments


def convertTime(msec: float):
    """"
        UNIXのミリ秒から、日本の時刻に変換する
    """
    # UNIX時間（秒）をdatetimeオブジェクトに変換（Pythonのdatetimeはマイクロ秒を扱うため1000で割る）
    date = datetime.fromtimestamp(
        msec / 1000, timezone(timedelta(hours=9)))  # JSTに変換
    # 年、月、日、時間、分、秒を取得し、パディングして組み合わせて返す
    return "{}/{}/{} {}:{}".format(date.year,
                                      str(date.month).zfill(2),
                                      str(date.day).zfill(2),
                                      str(date.hour).zfill(2),
                                      str(date.minute).zfill(2),
                                      )


def get_update_date(file_path: str) -> float:
    return os.path.getmtime(file_path)


# def watch_comment(queue:Any, last_modified_date: float, chat_file_path: str, last_row: int, comment_history_dict: Dict[str, List[CommentData]],チャットGPTハンドラー:チャットGPTハンドラークラス,live_id: str):
def watch_comment(last_modified_date: float, chat_file_path: str, last_row: int, comment_history_dict: Dict[str, List[CommentData]],チャットGPTハンドラー:チャットGPTハンドラークラス,live_id: str):
    current_modified_date = get_update_date(chat_file_path)
    comments_modified: list[str] = []
    if current_modified_date > last_modified_date:
        last_modified_date = current_modified_date
        comment_history_str = text_reader(chat_file_path)
        comment_history_list = split_text(comment_history_str)[:-1]
        comment_history_new = comment_history_list[last_row:]
        last_row = len(comment_history_list) - 1
        comment_history_dict = update_dictionary(
            comment_history_dict, comment_history_new,live_id)
        # try:
        #     # comment_history_last_row = json.loads(
        #     #     comment_history_list[last_row])
        #     # comment_history_last = convert_json_to_dict(
        #     #     comment_history_last_row)
        #     # messages = (copy.deepcopy(
        #     #     comment_history_dict[comment_history_last['userId']]))
        #     # messages.reverse()
        #     # comments_modified = [message['comment']
        #     #         for message in messages
        #     # ]
        #     # messages_modified = {
        #     #     '名前': comment_history_last['displayName'],
        #     #     'コメント': comments_modified
        #     # }
        #     # if (チャットGPTハンドラー.api_key != ''):
        #     #     messages_modified['分析'] = チャットGPTハンドラー.チャットGPTへ問いかけ(comments_modified[::-1])

        #     # if queue != '':
        #     #     queue.put('update')
        #     # else:
        #     #     print('update')
        # # except :
        # except Exception as error:
        #     # print('----------')
        #     # print('error')
        #     # print(error)
        #     # print(json.dumps(
        #     #     comment_history_list[last_row], indent=2, ensure_ascii=False))
        #     # print('++++++++++')
        #     pass
    return (last_modified_date, comment_history_dict)

def is_running_on_colab():
    return 'COLAB_GPU' in os.environ

def get_files_with_prefix(directory:str, prefix:str):
    # ディレクトリ内のすべてのファイル名を取得します。
    all_files = os.listdir(directory)
    # 文字列のstartswithメソッドを使用して指定したプレフィックスで始まるファイルのみをフィルタリングします。
    matching_files = [filename for filename in all_files if filename.startswith(prefix)]
    return matching_files

# reverse sort後、先頭のfile名を返す
def get_latest_file_path(chat_file_path:str):
    files = get_files_with_prefix(chat_file_path.split('/')[0], chat_file_path.split('/')[1])
    files.sort(reverse=True)
    assert 'live_chat.json.part-Frag' in files[0] 
    return './' +files[0]


def delete_live_chat_files():
    """同ディレクトリに存在する'.live_chat.json'を名前に含むすべてのファイルを削除します。

    Returns:
        None
    """
    # ディレクトリ内の'.live_chat.json'を名前に含むファイルを検索
    file_list = glob.glob('./*_chat.json')
    print(file_list)

    # 各ファイルを削除
    for file in file_list:
        os.remove(file)

# def replace_watch_comment(queue:Any, live_id: str,チャットGPTハンドラー:チャットGPTハンドラークラス):
def replace_watch_comment(live_id: str,チャットGPTハンドラー:チャットGPTハンドラークラス):
    """"
        watch_comment(last_modified_date)を1秒待機しては、繰り返し実行する.
        再帰ではなくwhileを使う
    """
    # 初期化
    delete_live_chat_files()    
    # queue.put('init')
    comment_history_dict: Dict[str, List[CommentData]] = {}
    last_row = 0
    last_history_modified_date:float =0
    chat_file_path:str
    chat_file_path = f'./{live_id}_.live_chat.json.part'
    # 開始時刻を取得
    start_time = time.time()
    while time.time() - start_time < 60*10:
        try:
            # last_history_modified_date,comment_history_dict = watch_comment(queue, last_history_modified_date, chat_file_path,
            last_history_modified_date,comment_history_dict = watch_comment(last_history_modified_date, chat_file_path,
                        last_row, comment_history_dict, チャットGPTハンドラー, live_id)
        except Exception as error:
            print(error)
            pass
        time.sleep(3)


# replace_watch_comment('', 'Bv6HsO5OuMc')
