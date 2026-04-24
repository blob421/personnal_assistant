from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout, 
                             QHBoxLayout, QLabel,  QStackedWidget)
from PyQt6.QtCore import Qt

from GUI.left_menu import Left_Menu
from GUI.colors import Color
from GUI.home.prompt_history import Prompt_Box
from GUI.home.main_screen import Home
from GUI.options.options_screen import Options
import asyncio
from utilities.db_calls import load_options

### Layout => Widgets
### Layout => Layout with widgets

class MainWindow(QMainWindow):
    def __init__(self, options):
        super().__init__()

        ########## WINDOW ######################
        self.setMinimumSize(1300, 800)
        self.setWindowTitle("Assistant")

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        
        ########## SCREENS #####################
    

        self.left_menu_widget = Left_Menu()
        self.right_screen = QStackedWidget()
        self.screens = {'home': Home(self), 'options': Options(options) }
      
        for _ ,v in self.screens.items():
            self.right_screen.addWidget(v)
        
      # layout1.setContentsMargins(300,0,0,0)
     

        main_layout.addWidget(self.left_menu_widget)
        main_layout.addWidget(self.right_screen)


        widget = QWidget()
        widget.setLayout(main_layout)

        self.setCentralWidget(widget)

    def show_screen(self, screen:str):
        self.right_screen.setCurrentWidget(self.screens[screen])



async def GUI_loop():
    app = QApplication([])
    options = await load_options()
    window = MainWindow(options)
  
    window.show()
    window.show_screen('options')

    await window.screens['home'].prompt_history.history_list.get_events()
    app.exec()


async def main():
    await asyncio.gather(GUI_loop())


asyncio.run(main())