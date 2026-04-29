from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout,
                             QTimeEdit,  QScrollArea)

from GUI.styles import styles
from PyQt6.QtCore import QTime, Qt
from .options import SilentMode, OperatingHours, EnableNotif, FontScaling
from .widgets import SaveButton
import config
from utilities.db_calls import save_options
from GUI.titles import Title

class Options(QWidget):
    def __init__(self, options):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.settings = options
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0,0,0,0)
     
        
        self.title_widget = Title('Settings')
    

        ################################################################
        self.option_1 = OperatingHours(self.settings, 'operating_hours_cont', 'Operating Hours')
        self.option2 = SilentMode('options_container', 'Silent mode (pauses vocal prompts)')
        self.o_notif = EnableNotif('options_container', 'Enable system notifications')
        self.o_font_scaling = FontScaling('options_container', 'Font size scaling')
      
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        container.setAutoFillBackground(True)
        container.setObjectName('options_box')
        scroll_layout = QVBoxLayout(container)


       
        empty_block = QWidget()
        # Add widgets to the layout
        scroll_layout.addWidget(self.option_1)
        scroll_layout.addWidget(self.option2)
        scroll_layout.addWidget(self.o_notif)
        scroll_layout.addWidget(self.o_font_scaling)
        scroll_layout.addWidget(empty_block)
     
        


        scroll.setWidget(container)
        ####################################################
    
   
        save_button = SaveButton('Apply settings')
        save_button.clicked.connect(self.get_options_values)
        save_btn_cont = QWidget()

        save_cont_layout = QHBoxLayout()
        save_cont_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        save_btn_cont.setLayout(save_cont_layout)
        save_cont_layout.addWidget(save_button)


        main_layout.addWidget(self.title_widget)
        main_layout.addWidget(scroll)
        main_layout.addWidget(save_btn_cont)

    def get_options_values(self):
        config.OPTIONS['op_h_start'] = self.option_1.time1.time().toString("HH:mm")
        config.OPTIONS['op_h_end'] = self.option_1.time2.time().toString("HH:mm")
        config.OPTIONS['silent_mode'] = self.option2.checkbox.isChecked()
        config.OPTIONS['notifications'] = self.o_notif.checkbox.isChecked()
        config.OPTIONS['font_scaling'] = str(self.o_font_scaling.widget.value() / 100)
        print('Calling save')
        save_options()

   


  




