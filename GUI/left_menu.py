
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy)

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt

import os 
from GUI.styles import styles

GUI_DIR = os.path.dirname(__file__)


class Image_button(QPushButton):
    def __init__(self, image, main):
        super().__init__()    
        self.main = main
        image_path = os.path.join(GUI_DIR, 'assets', f'{image}.png')
        self.setIcon(QIcon(image_path))
        self.setIconSize(QSize(100, 100))
        self.setFixedSize(100, 100)
        self.clicked.connect(lambda: self.main.show_screen(image))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

       
        
class ButtonContainer(QWidget):
    def __init__(self, image, main):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        button = Image_button(image, main) 
  
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)  

class Left_Menu(QWidget):
    def __init__(self, main_screen):
        super().__init__() 
        self.main = main_screen
        self.setSizePolicy(
        QSizePolicy.Policy.Fixed,
        QSizePolicy.Policy.Expanding
    )
        self.setObjectName('left_menu')
        self.setStyleSheet(styles['left_menu'])
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)


        left_menu = QVBoxLayout()

        home_btn = ButtonContainer('home', self.main)
        left_menu.addWidget(home_btn)

        contacts = ButtonContainer('watch list', self.main)
        left_menu.addWidget(contacts)

        left_menu.addStretch(1)

        options_button = ButtonContainer('options', self.main)
        left_menu.addWidget(options_button)

        self.setFixedWidth(150)
        self.setLayout(left_menu)
 