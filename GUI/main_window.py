
from PyQt6.QtWidgets import (QWidget, QMainWindow, QHBoxLayout, QStackedWidget)
from GUI.left_menu import Left_Menu
from GUI.home.main_screen import Home
from GUI.options.options_screen import Options

from PyQt6.QtCore import QObject, pyqtSignal

### Layout => Widgets
### Layout => Layout with widgets

class Worker(QObject):
    reload_requested = pyqtSignal()
    def __init__(self):
        super().__init__()
        
class MainWindow(QMainWindow):
    def __init__(self, options, vocal_handler):
        super().__init__()

        ########## WINDOW ######################
        self.setMinimumSize(1500, 800)
        self.setWindowTitle("Assistant")

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        
        ########## SCREENS #####################
      

        
        self.right_screen = QStackedWidget()
        
        self.screens = {'home': Home(self, vocal_handler), 'options': Options(options) }
      
        for _ ,v in self.screens.items():
            self.right_screen.addWidget(v)
        
      # layout1.setContentsMargins(300,0,0,0)
     
        self.left_menu_widget = Left_Menu(self)
        main_layout.addWidget(self.left_menu_widget)
        main_layout.addWidget(self.right_screen)


        widget = QWidget()
        widget.setLayout(main_layout)

        self.setCentralWidget(widget)
        self.worker = Worker()
        self.worker.reload_requested.connect(self.screens['home'].prompt_history.history_list.get_events)

    def show_screen(self, screen:str):
        self.right_screen.setCurrentWidget(self.screens[screen])