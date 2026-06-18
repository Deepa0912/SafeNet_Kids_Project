import psutil
import time
import threading

class ProcessManager:
    def __init__(self):
        self.target_browsers = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'brave.exe', 'opera.exe']
        self.blocked_processes = []
        self.is_blocking = False
        self.block_thread = None

    def kill_active_browsers(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() in self.target_browsers:
                    p = psutil.Process(proc.info['pid'])
                    p.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def add_blocked_process(self, process_name):
        if process_name.lower() not in self.blocked_processes:
            self.blocked_processes.append(process_name.lower())

    def remove_blocked_process(self, process_name):
        if process_name.lower() in self.blocked_processes:
            self.blocked_processes.remove(process_name.lower())

    def start_process_blocker(self):
        if not self.is_blocking:
            self.is_blocking = True
            self.block_thread = threading.Thread(target=self._block_loop, daemon=True)
            self.block_thread.start()

    def stop_process_blocker(self):
        self.is_blocking = False
        if self.block_thread:
            self.block_thread.join(timeout=2)

    def _block_loop(self):
        while self.is_blocking:
            if self.blocked_processes:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'] and proc.info['name'].lower() in self.blocked_processes:
                            p = psutil.Process(proc.info['pid'])
                            p.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
            time.sleep(2)