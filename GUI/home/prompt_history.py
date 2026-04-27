
from PyQt6.QtWidgets import (QLabel, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem,
                             QTableView)
from PyQt6.QtCore import Qt, QSize, QObject, pyqtSignal
from utilities.db_calls import get_events_gui
from GUI.styles import styles
from datetime import datetime

class worker(QObject):
    def __init__(self):
        super().__init__()
        reload_requested = pyqtSignal()
        self.reload_requested.emit()

class Prompt_Box(QWidget):
    def __init__(self):
        super().__init__() 
        
     
        self.setStyleSheet(styles['history'])
        self.setObjectName('prompt_box')
        prompt_box_layout = QVBoxLayout()
        self.setLayout(prompt_box_layout)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
     
        

        prompt_label = Prompt_label('Prompt history')
        prompt_label.setFixedHeight(65)
        self.history_list = Prompt_history()
  

        col_names = Prompt_Unit('Type', 'Message', 'Time', top_row=True)
        col_names.setMinimumHeight(90)
        col_names.setObjectName('top_col_cont')
        
       
        col_names.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        col_names.setAutoFillBackground(True)
   
        prompt_box_layout.addWidget(prompt_label)
        prompt_box_layout.addWidget(col_names)
        prompt_box_layout.addWidget(self.history_list)


class Prompt_history(QListWidget):
    def __init__(self):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    
    def get_events(self):
        results = get_events_gui()
       
        if results:
            self.clear()
            for result in results:
                item = QListWidgetItem()
             
               
                time = datetime.fromisoformat(result[1]).strftime("%d/%m/%Y, %H:%M")
                widget = Prompt_Unit(result[2], result[3], time)
          

                self.addItem(item)
               
                self.setItemWidget(item, widget)
                item.setSizeHint(QSize(0, widget.sizeHint().height() + 45))
                




class Prompt_label(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
      
        
       
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
      
        
class Prompt_Unit(QWidget):
    def __init__(self, type, content, time, top_row=False):
        super().__init__()
        
        
        layout = QHBoxLayout()
        self.setLayout(layout)
      
       
        type = QLabel(type)
        time = QLabel(time)
        content = QLabel(content)
       
        
       
        type.setFixedWidth(300)

        if not top_row:
            time.setFixedWidth(230)
            type.setObjectName("unit_type_label")
            time.setObjectName("unit_time_label")
            content.setWordWrap(True)
            content.setObjectName('unit_content_label')

            self.setObjectName('prompt_unit')
            self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self.setAutoFillBackground(True)
        
      
        
        else:
            time.setFixedWidth(241)
            type.setObjectName('top_col_prompts')
            time.setObjectName('top_col_prompts')
            content.setObjectName('top_col_prompts')
        

        layout.addWidget(type)
        layout.addWidget(content)
        layout.addWidget(time)