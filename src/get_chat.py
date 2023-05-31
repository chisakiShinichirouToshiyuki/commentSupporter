from yt_dlp import YoutubeDL

def get_chat(live_id: str):
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
