import asyncio
from bleak import BleakScanner, BleakClient
import sqlite3
import os
import contextlib
import traceback
import threading
from config import DB_PATH

class Device_Controller:

    def __init__(self):
        self.best_rssi = None
        self.user_is_near = True
        self.address = self.load_device()
      
    def load_device(self):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                with contextlib.closing(conn.cursor()) as cur:
                  
                    cur.execute('''SELECT * FROM devices''')
                    result = cur.fetchone()
                    if not result:
                        return None
                    return result[0]

        except sqlite3.Error as e:
            print(f'Error getting bluetooth devices: {e}')


    async def proximity_scan(self):
     
        if not self.address:
            print('Error , no device is presently configured or could not fetch it from db')
            return 
        
        
        address_in_proximity = False
        for i in range(2):
            devices = await BleakScanner.discover(return_adv=True)
            for addr, data in devices.items():
                if addr == self.address:
                    _, adv = data
                    address_in_proximity = True
                    rssi = getattr(adv, "rssi", None)
                    if rssi <= -80:
                        self.user_is_near = False

        if not address_in_proximity:
            print('Registered device not found in proximity')
            self.user_is_near = False


        
         
    async def scan_for_closest_device(self):
        print("About to call BleakScanner.discover()")
        traceback.print_stack()
        results = await BleakScanner.discover(return_adv=True)
        print("Scanning...")
        for i in range(2):
            results = await BleakScanner.discover(return_adv=True)
            
        
            for addr, data in results.items():
            
   
                device, adv = data
   
                # Extract address
                address = addr if isinstance(addr, str) else getattr(device, "address", None)

                # Extract RSSI
                rssi = getattr(adv, "rssi", None)

                # Extract name
                name = None
                if device and getattr(device, "name", None):
                    name = device.name
                elif adv and getattr(adv, "local_name", None):
                    name = adv.local_name

                rssi = int(str(rssi).replace('-', ""))

                if not self.best_rssi:
                    self.best_rssi = {'address': address, 'RSSI': rssi, 'name': name}
                if rssi < self.best_rssi['RSSI']:
                    self.best_rssi = {'address': address, 'RSSI': rssi, 'name': name}

                print(f"address: {address}, RSSI: {rssi}, name: {name}")
        

    async def scan_and_save(self):
     
        await self.scan_for_closest_device()
        self.save_device()

    def save_device(self):
        a = self.best_rssi['address']
        r = self.best_rssi["RSSI"]
        n = self.best_rssi['name']
        try:
            with sqlite3.connect(DB_PATH) as conn:
                with contextlib.closing(conn.cursor()) as cur:
                    cur.execute('''CREATE TABLE IF NOT EXISTS devices(address VARCHAR(18) UNIQUE, 
                                                                        RSSI INTEGER, 
                                                                        name VARCHAR(40))''') 
                    
                    cur.execute('''INSERT OR IGNORE INTO devices(address, RSSI, name) 
                                                                    VALUES (?,?,?)''', [a, r ,n])
        except sqlite3.Error as e:
            print(f'Error inserting bluethooth data into devices: {e}')

