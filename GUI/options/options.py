
from PyQt6.QtCore import QTime
from .widgets import OptionsContainer, TimeWidget, OptionBox


class SilentMode(OptionsContainer):
    def __init__(self, style_class, label_name):
        super().__init__(style_class, label_name)

        self.checkbox = OptionBox()
        self.layout.addWidget(self.checkbox)
        



class OperatingHours(OptionsContainer):
    def __init__(self, settings, style_class, label_name):
        super().__init__(style_class, label_name)
        self.settings = settings

      
        self.setObjectName("operating_hours_cont")

        self.time1 = TimeWidget()
        self.time2 = TimeWidget()
  
        self.layout.addWidget(self.time1)
        self.layout.addWidget(self.time2)
       
        self.time1.setTime(QTime.fromString(self.settings['op_h_start']['value']))
        self.time2.setTime(QTime.fromString(self.settings['op_h_end']['value']))