
from PyQt6.QtCore import QTime, Qt
from .widgets import OptionsContainer, TimeWidget, OptionBox
import config as config
from PyQt6.QtWidgets import QSlider, QLabel

class SilentMode(OptionsContainer):
    def __init__(self, style_class, label_name):
        super().__init__(style_class, label_name)
        
        self.checkbox = OptionBox()
       
        self.checkbox.setChecked(config.OPTIONS['silent_mode'])
        self.layout.addWidget(self.checkbox)                       ### Layout is inherited
        
class EnableNotif(OptionsContainer):
    def __init__(self, style_class, label_name):
        super().__init__(style_class, label_name)

        self.checkbox = OptionBox()
        self.checkbox.setChecked(config.OPTIONS['notifications'])
        self.layout.addWidget(self.checkbox)


class Slider(OptionsContainer):
    def __init__(self, style_class, label_name, minimum_range, option_name):
        super().__init__(style_class, label_name)

        self.slider_value = int(float(config.OPTIONS[option_name]) * 100)

        self.widget = QSlider(Qt.Orientation.Horizontal)
        self.widget.setRange(minimum_range, 100)
        self.widget.setValue(self.slider_value)

        self.widget.valueChanged.connect(self.change_slider)
        self.layout.addWidget(self.widget)

        self.slider_value = QLabel(str(self.slider_value / 100))
        self.widget.setObjectName('slider')
        self.layout.addWidget(self.slider_value)


    def change_slider(self):
        new_value = str(self.widget.value() / 100)
        self.slider_value.setText(new_value)
        


class OperatingHours(OptionsContainer):
    def __init__(self, settings, style_class, label_name):
        super().__init__(style_class, label_name)
        self.settings = settings

      
        self.setObjectName("operating_hours_cont")

        self.time1 = TimeWidget()
        self.time2 = TimeWidget()
  
        self.layout.addWidget(self.time1)
        self.layout.addWidget(self.time2)
       
        self.time1.setTime(QTime.fromString(self.settings['op_h_start']))
        self.time2.setTime(QTime.fromString(self.settings['op_h_end']))