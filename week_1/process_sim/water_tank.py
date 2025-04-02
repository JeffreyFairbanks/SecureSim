# secure-sim/process_sim/water_tank.py
import threading


class WaterTank:
    """Simple water tank simulation with inflow and outflow rates"""
    def __init__(self, capacity=100.0, initial_level=10.0):
        self.capacity = capacity
        self.level = initial_level
        self.inflow = 0.0
        self.outflow = 0.0
        self.lock = threading.Lock()

    def update(self, dt=1.0):
        """Update water level based on inflow and outflow rates"""
        with self.lock:
            # Calculate level change
            change = self.inflow - self.outflow
            self.level += change * dt
            
            # Ensure level stays within bounds
            self.level = max(0, min(self.capacity, self.level))
            return self.level

    def set_inflow(self, rate):
        """Set the inflow rate in units per second"""
        with self.lock:
            self.inflow = rate

    def set_outflow(self, rate):
        """Set the outflow rate in units per second"""
        with self.lock:
            self.outflow = rate

    def get_level(self):
        """Get the current water level"""
        with self.lock:
            return self.level
