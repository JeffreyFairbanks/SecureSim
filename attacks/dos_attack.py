# secure-sim/attacks/dos_attack.py
import time
import threading
import random


class DoSAttack:
    def __init__(self, tank):
        self.tank = tank
        self.running = False
        self.last_update_time = time.time()
        self.update_delay = 0  # Normal operation
        self.max_delay = 5.0  # Maximum delay in seconds
        
    def attack_loop(self):
        while self.running:
            # Randomly vary the delay to simulate intermittent connectivity issues
            self.update_delay = random.uniform(1.0, self.max_delay)
            time.sleep(1)
            
    def get_delayed_reading(self, true_value):
        """
        Simulates communication delays by returning stale data
        """
        if not self.running:
            self.last_update_time = time.time()
            return true_value
            
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_delay:
            # Update the stored value after delay has passed
            self.delayed_value = true_value
            self.last_update_time = current_time
            
        # The returned value might be stale
        return getattr(self, 'delayed_value', true_value)
            
    def start(self):
        self.running = True
        self.delayed_value = self.tank.get_level()  # Initialize with current value
        self.last_update_time = time.time()
        thread = threading.Thread(target=self.attack_loop)
        thread.daemon = True
        thread.start()
        return thread
        
    def stop(self):
        self.running = False