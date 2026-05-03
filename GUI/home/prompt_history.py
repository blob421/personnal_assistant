
from PyQt6.QtWidgets import (QLabel, QListWidget, QWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize
from utilities.db.sync_calls import get_events_gui
from GUI.styles import styles
from datetime import datetime


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
        prompt_label.setObjectName('prompt_top_title')
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
        old = False
 
        if results:
            self.clear()

            now = datetime.now()

            if any(datetime.fromisoformat(result[1]).day == now.day for result in results):
                today_separator = QListWidgetItem()
                self.addItem(today_separator)
                separator1 = DaySeparatorWidget('Today')
                self.setItemWidget(today_separator, separator1)
                today_separator.setSizeHint(QSize(0, separator1.sizeHint().height()))

          
            for result in results:

                item = QListWidgetItem()
                time = datetime.fromisoformat(result[1])

                if not now.day == time.day and not old:
                    old_separator = QListWidgetItem()
                    self.addItem(old_separator)
                    separator2 = DaySeparatorWidget('Old')
                    
                    self.setItemWidget(old_separator, separator2)
                    old_separator.setSizeHint(QSize(0, separator2.sizeHint().height()))
                    old = True

                display_time = time.strftime("%d/%m/%Y, %H:%M")

                widget = Prompt_Unit(result[2], result[3], display_time)
          

                self.addItem(item)
               
                self.setItemWidget(item, widget)
                item.setSizeHint(QSize(0, widget.sizeHint().height() + 85))
                


class DaySeparatorWidget(QLabel):
    def __init__(self, label_name):
        super().__init__()
        self.setText(label_name)
        self.setMinimumHeight(40)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
      
        self.setObjectName('prompts_separator')



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
     
        type.setMinimumWidth(130)
        type.setMaximumWidth(210)

        if not top_row:
            time.setMinimumWidth(150)
            time.setMaximumWidth(230)
         
            type.setObjectName("unit_type_label")
            time.setObjectName("unit_time_label")
            content.setWordWrap(True)
          
            content.setObjectName('unit_content_label')
            content.setMinimumWidth(160)
           

            self.setObjectName('prompt_unit')
            self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self.setAutoFillBackground(True)
        
      
        
        else:
            time.setMinimumWidth(161)
            time.setMaximumWidth(241)
            
            type.setObjectName('top_col_prompts')
            time.setObjectName('top_col_prompts')
            content.setObjectName('top_col_prompts')
        

        layout.addWidget(type, 3)
        layout.addWidget(content)
        layout.addWidget(time)