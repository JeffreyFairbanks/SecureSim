# secure-sim/control_logic/control.py
import time
import threading


class Controller:
    def __init__(self, tank, setpoint=50.0):
        self.tank = tank
        self.setpoint = setpoint
        self.running = True

    def control_loop(self):
        while self.running:
            current_level = self.tank.get_level()
            error = self.setpoint - current_level
            # Simple proportional control
            kp = 0.1
            control_signal = kp * error
            # Adjust inflow based on control signal (limit between 0 and 5)
            new_inflow = max(0, min(5, control_signal + 2.5))
            self.tank.set_inflow(new_inflow)
            # For this example, the outflow is kept constant.
            self.tank.set_outflow(1.0)
            time.sleep(1)

    def start(self):
        thread = threading.Thread(target=self.control_loop)
        thread.daemon = True
        thread.start()
        return thread

    def stop(self):
        self.running = False
