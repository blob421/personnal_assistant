import subprocess
import psutil


class Ressource_Controller():
    def __init__(self):
        self.gpu_vendor = self.detect_gpu_vendor()
        self.busy = False
        

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
        
    async def check_load(self):
        iterations = []
        for i in range(5):
            if self.gpu_vendor == 'nvidia':
                iterations.append(self.get_nvidia_util())

            else :
                iterations.append(self.get_cpu_util())

        mean = sum(iterations) / len(iterations)
        if mean > 40:
            self.busy = True
        else:
            self.busy = False
       
          

    def get_cpu_util(self):
     
        return psutil.cpu_percent(interval=None)

