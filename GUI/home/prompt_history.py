
from PyQt6.QtWidgets import (QLabel, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem,
                             QTextBrowser)
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
        self.setMinimumWidth(300)
     
        self.setStyleSheet(styles['history'])
        prompt_box_layout = QVBoxLayout()
        self.setLayout(prompt_box_layout)
        
        prompt_label = Prompt_label('Prompt history')
        self.history_list = Prompt_history()
  

        col_names = Prompt_Unit('Type', 'Message', 'Time', top_row=True)
        col_names.setMinimumHeight(90)

        prompt_box_layout.addWidget(prompt_label)
        prompt_box_layout.addWidget(col_names)
        prompt_box_layout.addWidget(self.history_list)


class Prompt_history(QListWidget):
    def __init__(self):
        super().__init__()
       
    
    def get_events(self):
        results = get_events_gui()
       
        if results:
            self.clear()
            for result in results:
                item = QListWidgetItem()
        
                item.setSizeHint(QSize(0, 90))
                time = datetime.fromisoformat(result[1]).strftime("%d/%m/%Y, %H:%M")
                widget = Prompt_Unit(result[2], result[3], time)
            

                self.addItem(item)
                self.setItemWidget(item, widget)




class Prompt_label(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setStyleSheet("background-color: black; color: white; padding: 10px;")
        self.setFixedHeight(100)
       
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
      
        
class Prompt_Unit(QWidget):
    def __init__(self, type, content, time, top_row=False):
        super().__init__()
        
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setMinimumHeight(90)
    
     

        type = QLabel(type)
        type.setObjectName("unit_type_label")
        type.setMaximumWidth(300)
        if top_row:
            content = QLabel(content)
        else:
            content= QLabel(content)
            content.setWordWrap(True)
        content.setObjectName('unit_content_label')
        

        time = QLabel(time)
        time.setObjectName("unit_time_label")
        time.setMaximumWidth(300)

        layout.addWidget(type)
        layout.addWidget(content)
        layout.addWidget(time)