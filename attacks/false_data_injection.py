# secure-sim/attacks/false_data_injection.py
import random


class FalseDataInjectionAttack:
    """Simulates a false data injection attack by adding random deviations to readings"""
    def __init__(self, tank):
        self.tank = tank
        self.running = False
        self.attack_percent = 0.0  # Controls intensity (0.0 to 1.0)
        self.max_deviation = 30.0  # Maximum deviation in units
        
    def get_false_reading(self, true_value):
        """Returns a falsified sensor reading based on the true value"""
        if not self.running:
            return true_value
            
        # Calculate deviation based on attack intensity
        # Gradually increase attack intensity with each call
        if self.attack_percent < 1.0:
            self.attack_percent += 0.02
            self.attack_percent = min(1.0, self.attack_percent)
            
        # Calculate maximum current deviation
        max_current_deviation = self.max_deviation * self.attack_percent
        
        # Add random deviation to make it look realistic
        deviation = random.uniform(-max_current_deviation, max_current_deviation)
        return true_value + deviation
            
    def start(self):
        """Start the attack"""
        self.running = True
        self.attack_percent = 0.0  # Reset attack intensity
        return True
        
    def stop(self):
        """Stop the attack"""
        self.running = False