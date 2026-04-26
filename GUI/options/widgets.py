
from PyQt6.QtWidgets import (QWidget, QPushButton, QLabel, QHBoxLayout,
                             QTimeEdit, QCheckBox)

from GUI.styles import styles
from PyQt6.QtCore import Qt

class OptionBox(QCheckBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(styles['checkboxes'])

class TimeWidget(QTimeEdit):
    def __init__(self):
        super().__init__()
        self.setMaximumWidth(160)
    
   

class OptionsContainer(QWidget):
    def __init__(self, style_class, label_name):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.setSpacing(30)
        self.setLayout(self.layout)
    
     
        if label_name:
            label = QLabel(label_name)
           
            
            self.layout.addWidget(label)
            
        self.setStyleSheet(styles['options'])
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.setMaximumHeight(130)

class SaveButton(QPushButton):
    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.setFixedSize(220, 100)
        self.setStyleSheet("""font-size: 30px;""")
        