# secure-sim/process_sim/water_tank.py
import time
import threading


class WaterTank:
    def __init__(self, capacity=100.0, initial_level=50.0):
        self.capacity = capacity
        self.level = initial_level
        self.inflow = 0.0
        self.outflow = 0.0
        self.lock = threading.Lock()

    def update(self, dt=1.0):
        with self.lock:
            change = self.inflow - self.outflow
            self.level += change * dt
            # Clamp the level between 0 and capacity
            self.level = max(0, min(self.capacity, self.level))
            return self.level

    def set_inflow(self, rate):
        with self.lock:
            self.inflow = rate

    def set_outflow(self, rate):
        with self.lock:
            self.outflow = rate

    def get_level(self):
        with self.lock:
            return self.level


if __name__ == "__main__":
    tank = WaterTank()
    tank.set_inflow(2.0)
    tank.set_outflow(1.0)
    for i in range(10):
        level = tank.update()
        print(f"Time {i}: Level = {level}")
        time.sleep(1)
