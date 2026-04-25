#!/usr/bin//env python3

from PyQt6.QtWidgets import QApplication, QWidget
import ctypes
import sys
import asyncio
import threading
from datetime import datetime, timedelta

from controllers.email_controller.email_main_controller import Email_Main_Controller
from controllers.bluetooth.controller import Device_Controller
from controllers.ressource_controller.controller import Ressource_Controller
from controllers.Sound.vocal_interactions import Vocal_Handler

from utilities.db_calls import (load_keywords, get_logged_events, init_db, load_options)

import config

from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, 
                             QHBoxLayout, QStackedWidget)

from PyQt6.QtCore import QObject, pyqtSignal
from GUI.left_menu import Left_Menu

from GUI.home.main_screen import Home
from GUI.options.options_screen import Options

########################################### INIT ################################################

#************** CONFIG ************************
time_until_next_prompt=None
is_windows_os = sys.platform.startswith("win")

#**********************************************

async def init():
    
    global email_controller, keywords, time_until_next_prompt, resource_controller, vocal_handler, device_controller, OPTIONS


    await init_db()

    now = datetime.now()
    last_prompt = await get_logged_events("'Daily prompt'")
    
    if last_prompt:
     
        last_prompt = datetime.fromisoformat(last_prompt[1])
        next_prompt = last_prompt + timedelta(days=1)
        time_remaining = (next_prompt - now).total_seconds()
     
 
        time_until_next_prompt = 5 if time_remaining < 0 else time_remaining + 5
    
    else: 

        time_until_next_prompt = 5
    


    resource_controller = Ressource_Controller()
    device_controller = Device_Controller()

    keywords = await load_keywords()

    vocal_handler = Vocal_Handler(is_windows_os, device_controller, resource_controller, keywords)
    email_controller = Email_Main_Controller(config.CONFIRMED_PROVIDERS, vocal_handler, keywords)

    config.OPTIONS = await load_options()
    
    

######################################## LOOPS ############################################

async def proximity_loop():
    
    global resource_controller, device_controller, vocal_handler

    if not device_controller.address:
        await device_controller.scan_and_save()
        device_controller.address = device_controller.best_rssi
        
    while True:

        await device_controller.proximity_scan()
        await resource_controller.check_load()
                                                      ## Will anounce in 5 minutes if prompt_active
        if device_controller.user_is_near and not resource_controller.busy and not vocal_handler.prompt_active:
            await vocal_handler.handle_pending_events()

   
        await asyncio.sleep(300)  
       
        



async def prompt_loop():
  
    await asyncio.sleep(time_until_next_prompt)
    while True:
        await vocal_handler.prompt_for_terms()
        await asyncio.sleep(3600 * 24)     


async def GUI_loop():
    app = QApplication([])
    window = QWidget()
    window.show()
    app.exec()


def MTA_thread():
    
    if is_windows_os:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        ctypes.windll.ole32.CoInitializeEx(0, 0x0)

    asyncio.run(proximity_loop())

def agentThread():
    asyncio.run(agentAsync())

async def agentAsync():
    await asyncio.gather(email_controller.get_messages(), prompt_loop())

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



async def GUI_loop():
  
    app = QApplication([])

    window = MainWindow(config.OPTIONS, vocal_handler)
    vocal_handler.window = window
    window.show()
    window.show_screen('home')

    window.screens['home'].prompt_history.history_list.get_events()
    app.exec()


async def main():
  

    await init()
    mta_thread = threading.Thread(target=MTA_thread, daemon=True).start()
    threading.Thread(target=agentThread, daemon=True).start()
    await GUI_loop()
    




asyncio.run(main())


