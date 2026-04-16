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
                    return {'power': result[4], 'manufacturer': result[3], 'bytes': result[5]}

        except sqlite3.Error as e:
            print(f'Error getting bluetooth devices: {e}')
            return None


    async def proximity_scan(self):
     
        if not self.address:
            print('Error , no device is presently configured or could not fetch it from db')
            return 
        
        
        address_in_proximity = False
        for i in range(2):
            devices = await BleakScanner.discover(return_adv=True)
            for addr, data in devices.items():
      
                _, adv = data
                power = str(adv.tx_power)
                for k, v in adv.manufacturer_data.items():
                    manufacturer = int(k)
                    encoded = str(v)
         
                if (encoded.startswith(self.address['bytes']) 
                    and manufacturer == self.address['manufacturer'] and power == self.address['power']):        
                    address_in_proximity = True
                    rssi = getattr(adv, "rssi", None)
                    if rssi <= -80:
                        self.user_is_near = False

        if not address_in_proximity:
            print('Registered device not found in proximity')
            self.user_is_near = False


        
         
    async def scan_for_closest_device(self):
        print("About to call BleakScanner.discover()")
    
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
                power = adv.tx_power
                for k, v in adv.manufacturer_data.items():
                    manufacturer = int(k)
                    encoded = str(v)[0:6]
            

           
                if not self.best_rssi:
                    self.best_rssi = {'address': address, 'RSSI': rssi, 'name': name, 'power': power, 'manufacturer': manufacturer
                                      , 'bytes': encoded}
                if rssi < self.best_rssi['RSSI']:
                    self.best_rssi = {'address': address, 'RSSI': rssi, 'name': name, 'power': power, 'manufacturer': manufacturer
                                      , 'bytes': encoded}

                print(f"address: {address}, RSSI: {rssi}, name: {name}")
        

    async def scan_and_save(self):
     
        await self.scan_for_closest_device()
        self.save_device()

    def save_device(self):
        a = self.best_rssi['address']
        r = self.best_rssi["RSSI"]
        n = self.best_rssi['name']
        p = self.best_rssi['power']
        m = self.best_rssi['manufacturer']
        b = self.best_rssi['bytes']
        try:
            with sqlite3.connect(DB_PATH) as conn:
                with contextlib.closing(conn.cursor()) as cur:
                    cur.execute('''CREATE TABLE IF NOT EXISTS devices(address VARCHAR(18) UNIQUE, 
                                                                        RSSI INTEGER, 
                                                                        name VARCHAR(40),
                                                                        manufacturer INTEGER,
                                                                        power VARCHAR(40),
                                                                        bytes VARCHAR(40))''') 
                    
                    cur.execute('''INSERT OR IGNORE INTO devices(address, RSSI, name, manufacturer, power, bytes) 
                                                                    VALUES (?,?,?,?,?,?)''', [a, r ,n, m, p, b])
        except sqlite3.Error as e:
            print(f'Error inserting bluethooth data into devices: {e}')

