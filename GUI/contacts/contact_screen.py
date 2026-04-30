
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QScrollArea)
from PyQt6.QtCore import Qt
from GUI.titles import Title
from GUI.components.right_menu import RightMenu
from utilities.db_calls import get_watchlist_messages, load_contacts_ref
from GUI.styles import styles
from datetime import datetime


class ContactScreen(QWidget):
    def __init__(self, vocal_handler):
        super().__init__()
      
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.setContentsMargins(0,0,0,0)

        title = Title('Watch list')
     
        self.below = ContactMain(vocal_handler)
        self.setStyleSheet(styles['watch list'])
        layout.addWidget(title)
        layout.addWidget(self.below)

class ContactMain(QWidget):
    def __init__(self,  vocal_handler):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setObjectName('below_screen')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
       
  
        self.left_cont = LeftContainer()
        right_menu = RightMenu('watch list', vocal_handler, self)
        layout.addWidget(self.left_cont)
        layout.addWidget(right_menu)

class LeftContainer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)
        title = QLabel('Messages')
        title.setMinimumHeight(70)
        title.setObjectName('title_below')
        top_row = MessageItemWidget({'sender': 'Sender', 'subject': 'Subject', 'date': 'Date', 'tags': 'Tags'}, top_row=True)
        top_row.setFixedHeight(70)
      
        self.bottom = MessageBox()
        title.setObjectName('title_messages')
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(top_row)
        layout.addWidget(self.bottom)

        

class MessageBox(QScrollArea):
    def __init__(self):
        super().__init__()
        container = QWidget()
        self.setWidget(container)
        self.setWidgetResizable(True)

        self.contacts = load_contacts_ref()
        self.layout = QVBoxLayout(container)
     
        self.layout.setContentsMargins(0,10,8,10)
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

    def load_messages(self, email=None):
        self.clear_layout()
        
        messages = get_watchlist_messages(email=email)
        if messages:
            for m in messages:
                widget = MessageItemWidget(m, self)
                self.layout.addWidget(widget)
      


class MessageItemWidget(QWidget):
    def __init__(self, message, parent=None, top_row=False):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout) 
        layout.setContentsMargins(0, 0, 12, 0)
       
        subject_widget = QLabel(message['subject'])
        
        if not top_row:
            sender_widget = QLabel(parent.contacts[message['sender']])
            time_widget = QLabel(datetime.fromisoformat(message['date']).strftime("%d/%m/%Y, %H:%M"))
            self.setObjectName('message_item')
            tags_widget = TagWidget(message['tags'])
            self.setMinimumHeight(150)
            self.setMaximumHeight(225)
            tags_widget.setObjectName('item_row_col')
            time_widget.setObjectName('item_row_col')
            sender_widget.setObjectName('item_row_col_sender')
     
            subject_widget.setObjectName('item_row_col')
            subject_widget.setWordWrap(True)
        else: 
            time_widget = QLabel(message['date'])
            sender_widget = QLabel(message['sender'])
            self.setObjectName('top_row')
            tags_widget = QLabel('Tags')
            tags_widget.setObjectName('top_row_col')
            time_widget.setObjectName('top_row_col')
            sender_widget.setObjectName('top_row_col')
            subject_widget.setObjectName('top_row_col')
          
        time_widget.setMaximumWidth(220)
        tags_widget.setMaximumWidth(120)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
     
        
        

        layout.addWidget(sender_widget, 2)
        layout.addWidget(subject_widget, 3)
        layout.addWidget(time_widget, 3)
        layout.addWidget(tags_widget, 2)

class TagWidget(QWidget):
    def __init__(self, tags):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(layout)
        
        for t in tags:
            widget = QLabel(t)
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget.setObjectName(t)
            widget.setFixedHeight(30)
            widget.setFixedWidth(90)
            layout.addWidget(widget)
