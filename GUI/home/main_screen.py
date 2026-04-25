from PyQt6.QtWidgets import (QLabel, QWidget, QVBoxLayout, QHBoxLayout)
from GUI.colors import Color
from GUI.home.prompt_history import Prompt_Box
from PyQt6.QtCore import Qt
from GUI.styles import styles
from GUI.home.keywords_menu import KeywordsMenu
from GUI.titles import Title

class Home(QWidget):
    def __init__(self, window, vocal_handler):
        super().__init__()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        ############## TITLE #################

   

        title_widget = Title('Home')

        ############## BELOW ################
      

        below_layout = QHBoxLayout()

       
        
        self.prompt_history = Prompt_Box()
        below_layout.addWidget(self.prompt_history)
        below_layout.addWidget(KeywordsMenu(vocal_handler))
        main_layout.addWidget(title_widget)
        main_layout.addLayout(below_layout)

