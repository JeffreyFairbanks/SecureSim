# secure-sim/attacks/replay_attack.py
import time
import threading


class ReplayAttack:
    def __init__(self, tank):
        self.tank = tank
        self.running = False
        self.attack_value = 75.0  # Spoofed water level for demonstration

    def attack_loop(self):
        while self.running:
            # In a real attack, the attacker might replay old sensor data
            # or inject false data.
            # We're no longer printing here since main.py handles the printing
            # This avoids duplicate console output
            time.sleep(5)

    def start(self):
        self.running = True
        thread = threading.Thread(target=self.attack_loop)
        thread.daemon = True
        thread.start()
        return thread

    def stop(self):
        self.running = False
