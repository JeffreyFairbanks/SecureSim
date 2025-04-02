# secure-sim/attacks/dos_attack.py
import time
import random


class DoSAttack:
    """Simulates a Denial of Service attack by returning delayed/stale sensor readings"""
    def __init__(self, tank):
        self.tank = tank
        self.running = False
        self.last_update_time = time.time()
        self.delayed_value = 0.0
        self.max_delay = 3.0  # Maximum delay in seconds
        
    def get_delayed_reading(self, true_value):
        """Simulates communication delays by returning stale data"""
        if not self.running:
            return true_value
        
        # Randomly vary the delay to simulate intermittent connectivity
        update_delay = random.uniform(1.0, self.max_delay)
        
        # Get current time
        current_time = time.time()
        
        # Check if it's time for an update based on delay
        if current_time - self.last_update_time >= update_delay:
            # Update the stored value after delay has passed
            self.delayed_value = true_value
            self.last_update_time = current_time
        
        # Return the delayed value (which might be stale)
        return self.delayed_value
            
    def start(self):
        """Start the attack"""
        self.running = True
        self.delayed_value = self.tank.get_level()  # Initialize with current value
        self.last_update_time = time.time()
        return True
        
    def stop(self):
        """Stop the attack"""
        self.running = False