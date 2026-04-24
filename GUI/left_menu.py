
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout)

from PyQt6.QtGui import QIcon
from GUI.colors import Color
from PyQt6.QtCore import QSize, Qt
import os 


GUI_DIR = os.path.dirname(__file__)


class Image_button(QPushButton):
    def __init__(self, image):
        super().__init__()    
        image_path = os.path.join(GUI_DIR, 'assets', f'{image}.png')
        self.setIcon(QIcon(image_path))
        self.setIconSize(QSize(100, 100))
        self.setFixedSize(100, 100)
        
        

class Left_Menu(QWidget):
    def __init__(self):
        super().__init__() 

        left_menu = QVBoxLayout()
        left_menu.addWidget(Color("grey"))

        options_button = Image_button('options')
        left_menu.addWidget(options_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setFixedWidth(200)
        self.setLayout(left_menu)