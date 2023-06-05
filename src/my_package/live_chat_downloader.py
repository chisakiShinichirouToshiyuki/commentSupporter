import importlib

if importlib.util.find_spec('yt-dlp') is None:
    !pip install yt-dlp

from yt_dlp import YoutubeDL
import glob

class LiveChatDownloader:
    """Youtubeのライブチャットをダウンロードするクラス."""

    def __init__(self, live_id: str):
        """初期化メソッド.

        Args:
            live_id (str): YouTubeのライブのID.
        """
        self._live_id = live_id

    def get_chat(self):
        """ライブチャットをダウンロードする."""
        self._delete_live_chat_files()
        live_url = f'https://www.youtube.com/watch?v={self._live_id}'
        ydl_video_opts = {
            'outtmpl': '%(id)s'+'_.mp4',
            'format': 'best',
            'writesubtitles': True,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True
        }
        with YoutubeDL(ydl_video_opts) as ydl:
            result = ydl.download([live_url])

    def _delete_live_chat_files(self):
        """同ディレクトリに存在する'.live_chat.json'を名前に含むすべてのファイルを削除します。

        Returns:
            None
        """
        # ディレクトリ内の'.live_chat.json'を名前に含むファイルを検索
        file_list = glob.glob('./*live_chat.json*')

        # 各ファイルを削除
        for file in file_list:
            os.remove(file)
