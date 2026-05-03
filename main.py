#!/usr/bin/env python3

import ctypes
import sys
import asyncio
import threading

from controllers.email_controller.email_main_controller import Email_Main_Controller
from controllers.bluetooth.controller import Device_Controller
from controllers.ressource_controller.controller import Ressource_Controller
from controllers.Sound.vocal_interactions import Vocal_Handler
from controllers.main_controller import MainController

from utilities.db.async_calls import (load_keywords, load_options)
from utilities.db.init_tables import init_db

import config as config


from PyQt6.QtWidgets import QApplication
from GUI.set_font_scaling import set_scaling
from GUI.main_window import MainWindow


########################################### INIT ################################################

#************** CONFIG ************************
time_until_next_prompt=None
is_windows_os = sys.platform.startswith("win")

#**********************************************

async def init():
    
    global resource_controller, vocal_handler, device_controller, Async_Worker


    await init_db()
    config.OPTIONS = await load_options()
    set_scaling()
    
    resource_controller = Ressource_Controller()
    device_controller = Device_Controller()

    keywords = await load_keywords()
 
    vocal_handler = Vocal_Handler(is_windows_os, keywords)
    email_controller = Email_Main_Controller(config.CONFIRMED_PROVIDERS)
    Async_Worker = MainController(email_controller, vocal_handler, device_controller, resource_controller)


######################################## LOOPS ############################################

async def proximity_loop():
    
    global resource_controller, device_controller, Async_Worker

    if not device_controller.address:
        await device_controller.scan_and_save()
        device_controller.address = device_controller.best_rssi
      
    while True:

        await device_controller.proximity_scan()
        await resource_controller.check_load()
        Async_Worker.timer.is_operating_hours()
     
        await Async_Worker.handle_pending_events()

   
        await asyncio.sleep(300)  
       
        


async def GUI_loop():
  
    app = QApplication([])

    window = MainWindow(config.OPTIONS, vocal_handler)
    vocal_handler.window = window
    Async_Worker.gui = window
    window.show()
    window.show_screen('watch list')

    window.screens['home'].prompt_history.history_list.get_events()
    app.exec()

#******************* THREADS ******************************************************

def MTA_thread():
    
    if is_windows_os:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        ctypes.windll.ole32.CoInitializeEx(0, 0x0)

    asyncio.run(proximity_loop())

def agentThread():
    asyncio.run(agentAsync())


#****************** MAIN **********************************************************

async def agentAsync():
    await asyncio.sleep(4)
    while True:
        await Async_Worker.process_mail()
        await asyncio.sleep(1800)



async def main():
  

    await init()
    mta_thread = threading.Thread(target=MTA_thread, daemon=True).start()
    threading.Thread(target=agentThread, daemon=True).start()
    await GUI_loop()
    




asyncio.run(main())


