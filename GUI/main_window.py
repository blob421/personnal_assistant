
from PyQt6.QtWidgets import (QWidget, QMainWindow, QHBoxLayout, QStackedWidget,QSystemTrayIcon, 
                             QMenu, QApplication)
from GUI.left_menu import Left_Menu
from GUI.home.main_screen import Home
from GUI.options.options_screen import Options
from GUI.styles import styles
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
### Layout => Widgets
### Layout => Layout with widgets
import os 
icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
from PyQt6.QtGui import QIcon, QAction


class Worker(QObject):
    reload_requested = pyqtSignal()
    def __init__(self):
        super().__init__()
        
class MainWindow(QMainWindow):
    def __init__(self, options, vocal_handler):
        super().__init__()

        ########## WINDOW ######################
    
        self.setMinimumSize(1400, 750)
        self.setWindowTitle("Assistant")
        self.setWindowIcon(QIcon(icon_path))
    
   
        main_layout = QHBoxLayout()

        ########## TRAY ##########################
        self.tray = QSystemTrayIcon(QIcon(icon_path), self)
        

        self.tray.setToolTip("Assistant, left click to show menu")
   
        menu = QMenu(self)
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)

        show_action.triggered.connect(self.show_normal)
        quit_action.triggered.connect(self.quit_app)

        menu.addAction(show_action)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        
        ########## SCREENS #####################
      

        
        self.right_screen = QStackedWidget()
        
        self.screens = {'home': Home(self, vocal_handler), 'options': Options(options) }
      
        for _ ,v in self.screens.items():
            self.right_screen.addWidget(v)
        
       
     
        self.left_menu_widget = Left_Menu(self)
        main_layout.addWidget(self.left_menu_widget)
        main_layout.addSpacerItem(QSpacerItem(8, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        main_layout.addWidget(self.right_screen)

        main_layout.setContentsMargins(0, 10, 0, 0)
        widget = QWidget()
        widget.setLayout(main_layout)

        self.setCentralWidget(widget)
        self.worker = Worker()
        self.worker.reload_requested.connect(self.screens['home'].prompt_history.history_list.get_events)
        #self.tray.show()

    def show_screen(self, screen:str):
        self.right_screen.setCurrentWidget(self.screens[screen])

    def closeEvent(self, event):
        event.ignore()
        self.tray.show()
        self.hide()
 

    def show_normal(self):
        self.tray.hide()
        self.show()
        self.raise_()
        self.activateWindow()

       

    def quit_app(self):
        self.tray.hide()
        QApplication.quit()
