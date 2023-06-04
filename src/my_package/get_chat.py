from yt_dlp import YoutubeDL
import os
import glob

def delete_live_chat_files():
    """同ディレクトリに存在する'.live_chat.json'を名前に含むすべてのファイルを削除します。

    Returns:
        None
    """
    # ディレクトリ内の'.live_chat.json'を名前に含むファイルを検索
    file_list = glob.glob('./*live_chat.json*')
    print(file_list)

    # 各ファイルを削除
    for file in file_list:
        os.remove(file)


def get_chat(live_id: str):
    delete_live_chat_files()    
    live_url = f'https://www.youtube.com/watch?v={live_id}'
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

# get_chat('olJxvZne88k')
