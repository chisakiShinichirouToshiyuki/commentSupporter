import json
import os
import time
import glob
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Dict
from typing import List
from typing import TypedDict
from typing import Tuple

from my_package.gpt_handler import チャットGPTハンドラークラス


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


class DataFormatter:
    def __init__(self, live_id: str, チャットGPTハンドラー: チャットGPTハンドラークラス):
        """
        データフォーマッタークラスの初期化.

        Parameters
        ----------
        live_id : str
            ライブID.
        チャットGPTハンドラー : チャットGPTハンドラークラス
            チャットGPTハンドラーのインスタンス.
        """
        self._live_id = live_id
        self._gpt_handler = チャットGPTハンドラー
        self._comment_history_dict: Dict[str, List[CommentData]] = {}
        self._last_row = 0
        self._last_history_modified_date: float = 0
        self._chat_file_path: str = f'./{live_id}_.live_chat.json.part'

    def replace_watch_comment(self):
        """
        watch_comment()を3秒待機しては、繰り返し実行する.
        """
        # 初期化
        self._delete_live_chat_files()   
        self._comment_history_dict = {}
        self._last_row = 0
        self._last_history_modified_date = 0
        # 開始時刻を取得
        start_time = time.time()
        while time.time() - start_time < 60*10:
            try:
                self._last_history_modified_date = self._watch_comment()
            except Exception as error:
                print(error)
            time.sleep(3)


    def _convert_json_to_dict(self, comment: CommentRowData) -> CommentData:
        """
        JSON形式のコメントを辞書型データに変換する.

        Parameters
        ----------
        comment : CommentRowData
            JSON形式のコメントデータ.

        Returns
        -------
        CommentData
            辞書型のコメントデータ.
        """
        # コメントの各部分を抽出
        action = comment["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]
        
        # コメントの部分を辞書として戻す
        return {
            'userId': action["authorName"]["simpleText"],
            'displayName': action["authorName"]["simpleText"],
            'date': datetime.fromtimestamp(int(action["timestampUsec"]) / 1_000_000).strftime("%H:%M"),
            'comment': action["message"]["runs"][0]["text"]
        }
    
    def _convert_time(self, msec: float) -> str:
        """
        UNIXのミリ秒を日本の時刻に変換する.

        Parameters
        ----------
        msec : float
            UNIXのミリ秒時間.

        Returns
        -------
        str
            日本の時刻を表す文字列.
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

    def _delete_live_chat_files(self) -> None:
        """
        同ディレクトリに存在する'.live_chat.json'を名前に含むすべてのファイルを削除する.

        Returns
        -------
        None
        """
        # ディレクトリ内の'.live_chat.json'を名前に含むファイルを検索
        file_list = glob.glob('./*_chat.json')
        print(file_list)

        # 各ファイルを削除
        for file in file_list:
            os.remove(file)

    def _get_files_with_prefix(self, directory: str, prefix: str) -> List[str]:
        """
        指定したディレクトリ内の指定したプレフィックスで始まるファイル名のリストを取得する.

        Parameters
        ----------
        directory : str
            ディレクトリのパス.
        prefix : str
            ファイル名のプレフィックス.

        Returns
        -------
        List[str]
            ファイル名のリスト.
        """
        # ディレクトリ内のすべてのファイル名を取得します。
        all_files = os.listdir(directory)
        # 文字列のstartswithメソッドを使用して指定したプレフィックスで始まるファイルのみをフィルタリングします。
        matching_files = [filename for filename in all_files if filename.startswith(prefix)]
        return matching_files


    def _get_update_date(self, file_path: str) -> float:
        """
        指定したファイルの更新日時を取得する.

        Parameters
        ----------
        file_path : str
            ファイルのパス.

        Returns
        -------
        float
            ファイルの更新日時（UNIX時間）.
        """
        return os.path.getmtime(file_path)

    def _load_json(self, file_path: str) -> List[chat_transaction]:
        """
        指定したパスのJSONファイルを読み込みます。ファイルが存在しない場合は新しいリストを返します。

        Parameters
        ----------
        file_path : str
            JSONファイルへのパス.

        Returns
        -------
        List[Any]
            JSONから読み込んだデータ、または新しいリスト.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data: List[chat_transaction] = json.load(f)
        else:
            data: List[chat_transaction] = []  # ファイルが存在しない場合は新しいリストを作成

        return data

    def _split_text(self, text: str) -> List[str]:
        """
        テキストを行ごとに分割してリストに格納する.

        Parameters
        ----------
        text : str
            分割するテキスト.

        Returns
        -------
        List[str]
            分割された行のリスト.
        """
        return text.split('\n')

    def _text_reader(self, file_path: str) -> str:
        """
        ローカルファイルをテキストとして取得します。

        Args:
            file_path (str): ファイルパス。

        Returns:
            str: テキストデータ。
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _update_and_save_json(self, file_path: str, data: List[chat_transaction]|Dict[str, List[CommentData]]) -> None:
        """
        リストに要素を追加し、それを同じJSONファイルに書き込みます。

        Args:
            file_path (str): JSONファイルへのパス。
            data (List[Any]): 追加するデータ。

        Returns:
            None
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _update_dictionary(self, user_comments: Dict[str, List[CommentData]], comments: List[str],live_id: str) -> Dict[str, List[CommentData]]:
        """
        辞書にコメントを追加します。

        Args:
            user_comments (Dict[str, List[CommentData]]): ユーザーごとのコメント履歴の辞書。
            comments (List[str]): 追加するコメントのリスト。
            live_id (str): ライブID。

        Returns:
            Dict[str, List[CommentData]]: 更新後のコメント履歴の辞書。
        """
        new_chat_transactions: List[chat_transaction] = []
        for comment in comments:
            try:
                data: CommentRowData = json.loads(comment)
                action = data["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]
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
                })
            except Exception as error:
                pass
        try :
            self._update_json_file(f'{live_id}_chat.json', new_chat_transactions)
            self._update_and_save_json(f'{live_id}_each_chat.json', user_comments)
        except Exception as error:
            pass
        return user_comments

    def _watch_comment(self) -> float:
        """
        コメントを監視し、更新があった場合にコメント履歴を更新します。

        Args:
            last_modified_date (float): 最終更新日時。
            chat_file_path (str): チャットファイルのパス。
            last_row (int): 最終行のインデックス。
            comment_history_dict (Dict[str, List[CommentData]]): コメント履歴の辞書。
            live_id (str): ライブID。

        Returns:
            Tuple[float, Dict[str, List[CommentData]]]: 更新後の最終更新日時とコメント履歴の辞書。
        """
        current_modified_date = self._get_update_date(self._chat_file_path)
        if current_modified_date > self._last_history_modified_date:
            self._last_history_modified_date = current_modified_date
            comment_history_str = self._text_reader(self._chat_file_path)
            comment_history_list = self._split_text(comment_history_str)[:-1]
            comment_history_new = comment_history_list[self._last_row:]
            self._last_row = len(comment_history_list)
            self._comment_history_dict = self._update_dictionary(self._comment_history_dict, comment_history_new, self._live_id)
        return self._last_history_modified_date


    def _update_json_file(self, file_path: str, new_chats: List[chat_transaction]) -> None:
        """JSONファイルからデータを読み込み、新たな要素を追加し、それを同じファイルに保存します。

        Args:
            file_path (str): JSONファイルへのパス。
            new_element (Any): 追加する新しい要素。

        Returns:
            None
        """
        # JSONファイルを読み込み。ファイルが存在しない場合は新しいリストを作成。
        data = self._load_json(file_path)

        # リストに新たな要素を含むlistを末尾に結合。ただしdataはimmutableなので、新しいlistを作成する。
        data = data + new_chats

        # 結果を同じファイルに書き込み
        self._update_and_save_json(file_path, data)