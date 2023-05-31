import time
import ipywidgets as widgets
from IPython.display import display
import json

# ボタンの作成
def ui_test(queue, button):
    queue.put('test')
    # def on_button_clicked(b):

    # button.on_click(on_button_clicked)

    # display(button)
