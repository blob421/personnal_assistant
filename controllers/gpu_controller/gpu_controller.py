import subprocess
import time 

class GPU_Controller():
    def __init__(self):
        self.gpu_vendor = self.detect_gpu_vendor()
        

    def detect_gpu_vendor(self):
        try:
            output = subprocess.check_output(
                ["powershell", "-Command",
                "(Get-CimInstance Win32_VideoController).Name"],
                text=True
            ).lower()

            if "nvidia" in output:
                return "nvidia"
            if "amd" in output or "radeon" in output:
                return "amd"
            return "unknown"
        except Exception:
            return "unknown"

        
    def get_nvidia_util(self):
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                stderr=subprocess.DEVNULL,
                text=True
            )
            return int(output.strip())
        except Exception:
            return None
        
    def check_gpu_load(self):
        if self.gpu_vendor == 'nvidia':
            return self.get_nvidia_util()


controller = GPU_Controller()
while True:
    print(controller.check_gpu_load())
    time.sleep(10)
