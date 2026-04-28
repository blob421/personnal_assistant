from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QPushButton, 
                             QListWidgetItem, QInputDialog, QMessageBox)
from GUI.styles import styles
from GUI.home.prompt_history import Prompt_label
from PyQt6.QtCore import Qt, QSize

from utilities.db_calls import delete_keyword, add_keyword_gui


class KeywordsMenu(QWidget):
    def __init__(self, vocal_handler):
        super().__init__()
        layout = QVBoxLayout()
        self.vocal_handler = vocal_handler
        self.keywords:set = self.vocal_handler.keywords
        self.setLayout(layout)
        self.setStyleSheet(styles['keywords'])
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)

        self.title = Prompt_label('Keywords')
        self.title.setFixedHeight(65)
     
        self.keywords_list = KeyWordsList(self.keywords, self)

        add_button = AddButton('Add +', self)

       

        layout.addWidget(self.title)
        layout.addWidget(self.keywords_list)
        layout.addWidget(add_button)


    
class KeyWordsList(QListWidget):
    def __init__(self, keywords, menu):
        super().__init__()
        self.menu = menu
        self.setStyleSheet(styles['keywords'])
        for k in keywords:
            item = QListWidgetItem()
           
            widget = ListWidget(k, self.menu, item)
            item.setSizeHint(QSize(0, 90))

            self.addItem(item)
          
            self.setItemWidget(item, widget)

    def add_item(self, name):

        item = QListWidgetItem()
       

        widget = ListWidget(name, self.menu, item)
        item.setSizeHint(QSize(0, 90))

        self.addItem(item)
        
        self.setItemWidget(item, widget)

class ListWidget(QWidget):
    def __init__(self, label_name, menu, widget_item):
        super().__init__()
        self.menu = menu
       
        self.widget_item = widget_item
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setMinimumHeight(90)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('list_item')
     
        label = QLabel(label_name)
        label.setObjectName('keyword_label')

        x_btn = QPushButton('X')
        x_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        x_btn.setObjectName('x_btn_keywords')


        x_btn.setFixedSize(45,45)
        x_btn.clicked.connect(lambda: self.delete_k(label_name))

        layout.addWidget(label)
        layout.addWidget(x_btn)

    def delete_k(self, keyword):
        reply = QMessageBox.question(
        self,
        "Confirm deletion",
        f"Delete keyword '{keyword}'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )

        if reply == QMessageBox.StandardButton.Yes:
            delete_keyword(keyword)
            row = self.menu.keywords_list.row(self.widget_item)
            self.menu.keywords_list.takeItem(row) 
            self.menu.vocal_handler.keywords.remove(keyword)
            self.menu.keywords_list.removeItemWidget(self.widget_item)
        
       

class AddButton(QPushButton):
    def __init__(self, label_name, menu):
        super().__init__()
        self.menu = menu
        self.setText(label_name)
        self.clicked.connect(lambda: self.add_keyword())

        self.setStyleSheet(styles['dialogs'])
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def add_keyword(self):
        text, ok = QInputDialog.getText(
            self,                     # parent → centers on your window
            "Enter keyword",          # title
            "Type the new keyword:"   # label
        )
      
        if text and ok :
            add_keyword_gui(text)
            self.menu.vocal_handler.keywords.add(text)
            self.menu.keywords_list.add_item(text)

