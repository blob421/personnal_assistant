from PyQt6.QtWidgets import (QLabel)

from GUI.styles import styles
from PyQt6.QtCore import  Qt




class Title(QLabel):
    def __init__(self, label_name):
        super().__init__()
        self.setText(label_name)
        self.setStyleSheet(styles['titles'])
        self.setFixedHeight(130)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)