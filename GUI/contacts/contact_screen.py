
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QScrollArea)
from PyQt6.QtCore import Qt
from GUI.titles import Title
from GUI.components.right_menu import RightMenu
from utilities.db_calls import get_watchlist_messages
from GUI.styles import styles
from datetime import datetime


class ContactScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.setContentsMargins(0,0,0,0)

        title = Title('Watch list')
     
        self.below = ContactMain()
        self.setStyleSheet(styles['watch list'])
        layout.addWidget(title)
        layout.addWidget(self.below)

class ContactMain(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setObjectName('below_screen')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
       
  
        self.left_cont = LeftContainer()
        right_menu = RightMenu('watch list')
        layout.addWidget(self.left_cont)
        layout.addWidget(right_menu)

class LeftContainer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)
        title = QLabel('Messages')
        top_row = MessageItemWidget({'sender': 'Sender', 'subject': 'Subject', 'date': 'Date', 'tags': 'Tags'}, top_row=True)
        top_row.setMaximumHeight(150)
        self.bottom = MessageBox()
        title.setObjectName('title_messages')
        layout.addWidget(title, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(top_row, 1)
        layout.addWidget(self.bottom, 8)

        

class MessageBox(QScrollArea):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(5,10,8,10)
        self.load_messages()
        self.setObjectName('scroll_area')
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_messages(self):
        self.clear_layout()
  
        messages = get_watchlist_messages()
        if messages:
            for m in messages:
                widget = MessageItemWidget(m)
                self.layout.addWidget(widget)
      


class MessageItemWidget(QWidget):
    def __init__(self, message, top_row=False):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout) 
        sender_widget = QLabel(message['sender'])
        subject_widget = QLabel(message['subject'])
        
        if not top_row:
            time_widget = QLabel(datetime.fromisoformat(message['date']).strftime("%d/%m/%Y, %H:%M"))
            self.setObjectName('message_item')
            tags_widget = TagWidget(message['tags'])
            self.setMinimumHeight(150)
            self.setMaximumHeight(225)
            tags_widget.setObjectName('item_row_col')
            time_widget.setObjectName('item_row_col')
            sender_widget.setObjectName('item_row_col')
            subject_widget.setObjectName('item_row_col')
        else: 
            time_widget = QLabel(message['date'])
            
            self.setObjectName('top_row')
            tags_widget = QLabel('Tags')
            tags_widget.setObjectName('top_row_col')
            time_widget.setObjectName('top_row_col')
            sender_widget.setObjectName('top_row_col')
            subject_widget.setObjectName('top_row_col')
            subject_widget.setWordWrap(True)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
     
        
        

        layout.addWidget(sender_widget, 3)
        layout.addWidget(subject_widget, 3)
        layout.addWidget(time_widget, 2)
        layout.addWidget(tags_widget, 2)

class TagWidget(QWidget):
    def __init__(self, tags):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        for t in tags:
            widget = QLabel(t)
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget.setObjectName(t)
            widget.setFixedHeight(30)
            widget.setMaximumWidth(90)
            layout.addWidget(widget, 3)
