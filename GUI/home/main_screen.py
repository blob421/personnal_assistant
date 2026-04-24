from PyQt6.QtWidgets import (QLabel, QWidget, QVBoxLayout, QHBoxLayout)
from GUI.colors import Color
from GUI.home.prompt_history import Prompt_Box
from PyQt6.QtCore import Qt
from GUI.styles import styles

class Home(QWidget):
    def __init__(self, window):
        super().__init__()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        ############## TITLE #################

        title_layout = QVBoxLayout()

        title_widget = title_label()
        title_widget.setFixedHeight(70)

        title_layout.addWidget(title_widget)

        ############## BELOW ################
      

        below_layout = QHBoxLayout()

        below_layout.addWidget(Color('purple'))
        
        self.prompt_history = Prompt_Box()
        below_layout.addWidget(self.prompt_history)
   
        main_layout.addLayout(title_layout)
        main_layout.addLayout(below_layout)

class title_label(QLabel):
    def __init__(self):
        super().__init__()
        self.setText('Home')
        self.setStyleSheet("background-color: white; color: black; padding: 10px;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(styles['screen_title'])