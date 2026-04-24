
from PyQt6.QtWidgets import (QLabel, QListWidget, QWidget, QVBoxLayout)
from PyQt6.QtCore import Qt
from utilities.db_calls import get_logged_events
from GUI.styles import styles


class Prompt_Box(QWidget):
    def __init__(self):
        super().__init__() 
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)

        prompt_box_layout = QVBoxLayout()
        self.setLayout(prompt_box_layout)
        
        prompt_label = Prompt_label('Prompt history')
        self.history_list = Prompt_history()
  
        prompt_box_layout.addWidget(prompt_label)
        prompt_box_layout.addWidget(self.history_list)


class Prompt_history(QListWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(styles['history_list'])
    
    async def get_events(self):
        results = await get_logged_events(limit=20, many=20)
        for result in results:
            self.addItem(f"{result[2]}, {result[1]}")


class Prompt_label(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setStyleSheet("background-color: black; color: white; padding: 10px;")
        self.setFixedHeight(100)
       
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(styles['history_title'])
        