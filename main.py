#!/usr/bin/env python3

import ctypes
import sys
import asyncio
import threading
from datetime import datetime, timedelta

from controllers.email_controller.email_main_controller import Email_Main_Controller
from controllers.bluetooth.controller import Device_Controller
from controllers.ressource_controller.controller import Ressource_Controller
from controllers.Sound.vocal_interactions import Vocal_Handler
from controllers.timer.timer import Timer
from utilities.db_calls import (load_keywords, get_logged_events, init_db, load_options)

import config


from PyQt6.QtWidgets import QApplication
from GUI.set_font_scaling import set_scaling
from GUI.main_window import MainWindow


########################################### INIT ################################################

#************** CONFIG ************************
time_until_next_prompt=None
is_windows_os = sys.platform.startswith("win")

#**********************************************

async def init():
    
    global email_controller, keywords, time_until_next_prompt, resource_controller, vocal_handler, device_controller, OPTIONS


    await init_db()
    config.OPTIONS = await load_options()
    set_scaling()
    
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
    timer = Timer()
    vocal_handler = Vocal_Handler(is_windows_os, device_controller, resource_controller, keywords, timer)
    email_controller = Email_Main_Controller(config.CONFIRMED_PROVIDERS, vocal_handler, keywords)

    
    
    

######################################## LOOPS ############################################

async def proximity_loop():
    
    global resource_controller, device_controller, vocal_handler

    if not device_controller.address:
        await device_controller.scan_and_save()
        device_controller.address = device_controller.best_rssi
    await asyncio.sleep(3)    
    while True:

        await device_controller.proximity_scan()
        await resource_controller.check_load()
        vocal_handler.is_operating_hours()
       
   
                                                      ## Will anounce in 5 minutes if prompt_active
        if device_controller.user_is_near and not resource_controller.busy and not vocal_handler.prompt_active:
            await vocal_handler.last_asked_for_keywords()
            await vocal_handler.handle_pending_events()

   
        await asyncio.sleep(300)  
       
        


async def GUI_loop():
  
    app = QApplication([])

    window = MainWindow(config.OPTIONS, vocal_handler)
    vocal_handler.window = window
    email_controller.window = window
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
    await asyncio.gather(email_controller.get_messages())


async def main():
  

    await init()
    mta_thread = threading.Thread(target=MTA_thread, daemon=True).start()
    threading.Thread(target=agentThread, daemon=True).start()
    await GUI_loop()
    




asyncio.run(main())


