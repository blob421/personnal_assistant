from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout,
                             QTimeEdit,  QScrollArea)

from GUI.styles import styles
from PyQt6.QtCore import QTime, Qt
from .options import SilentMode, OperatingHours
from .widgets import SaveButton

    
class Options(QWidget):
    def __init__(self, options):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.settings = options
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.setObjectName("option_panel")
        self.setStyleSheet(styles['option_panel'])
        
        self.title_widget = QLabel('Settings')
        self.title_widget.setStyleSheet(styles['titles'])
        self.title_widget.setFixedHeight(130)
        self.title_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ################################################################
        self.option_1 = OperatingHours(self.settings, 'operating_hours_cont', 'Operating Hours')
        self.option2 = SilentMode('options_container', 'Silent mode (pauses vocal prompts)')
      
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        scroll_layout = QVBoxLayout(container)


       
        empty_block = QWidget()
        # Add widgets to the layout
        scroll_layout.addWidget(self.option_1)
        scroll_layout.addWidget(self.option2)
        scroll_layout.addWidget(empty_block)
     
        


        scroll.setWidget(container)
        ####################################################
    
   
        save_button = SaveButton('Apply settings')
        
        save_btn_cont = QWidget()
        save_cont_layout = QHBoxLayout()
        save_cont_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        save_btn_cont.setLayout(save_cont_layout)
        save_cont_layout.addWidget(save_button)


        main_layout.addWidget(self.title_widget)
        main_layout.addWidget(scroll)
        main_layout.addWidget(save_btn_cont)
  




