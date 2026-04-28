from datetime import datetime, timedelta
import config

class Timer():
    def __init__(self):
        self.gui_refresh_due = False
        self.last_gui_refresh = None

    def hour_match(self):
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        end_h, end_m = config.OPTIONS['op_h_end'].split(':')
        start_h, start_m = config.OPTIONS['op_h_start'].split(':')

        
        good = current_hour >= int(start_h) and current_hour <= int(end_h)
        if (current_hour == 0 and current_minute < 6):
            if not self.last_gui_refresh or current_time - self.last_gui_refresh > timedelta(minutes=60):
               self.gui_refresh_due = True

        if current_hour == int(start_h) and current_minute < int(start_m):
            return False

        elif current_hour == int(end_h) and current_minute > int(end_m):
            return False

        else:
            
            return good
    
 