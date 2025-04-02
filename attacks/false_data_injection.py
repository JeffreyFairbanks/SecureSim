# secure-sim/attacks/false_data_injection.py
import time
import threading
import random


class FalseDataInjectionAttack:
    def __init__(self, tank):
        self.tank = tank
        self.running = False
        self.attack_percent = 0.0  # Gradually increases
        self.max_deviation = 30.0  # Maximum deviation in units
        
    def attack_loop(self):
        while self.running:
            # Gradually increase attack intensity
            if self.attack_percent < 1.0:
                self.attack_percent += 0.1
                self.attack_percent = min(1.0, self.attack_percent)
            
            # Random walk the deviation value to make it look realistic
            time.sleep(2)
            
    def get_false_reading(self, true_value):
        """
        Returns a falsified sensor reading based on the true value.
        As attack progresses, the deviation increases.
        """
        if not self.running:
            return true_value
            
        # Calculate deviation based on attack intensity
        max_current_deviation = self.max_deviation * self.attack_percent
        # Add some randomness to make it look like normal sensor noise
        deviation = random.uniform(-max_current_deviation, max_current_deviation)
        return true_value + deviation
            
    def start(self):
        self.running = True
        self.attack_percent = 0.0  # Reset attack intensity
        thread = threading.Thread(target=self.attack_loop)
        thread.daemon = True
        thread.start()
        return thread
        
    def stop(self):
        self.running = False