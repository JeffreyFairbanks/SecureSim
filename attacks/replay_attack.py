# secure-sim/attacks/replay_attack.py
import threading


class ReplayAttack:
    """Simulates a replay attack that returns a fixed spoofed value"""
    def __init__(self, tank):
        self.tank = tank
        self.running = False
        self.attack_value = 75.0  # Fixed spoofed value

    def start(self):
        """Start the attack"""
        self.running = True
        return True

    def stop(self):
        """Stop the attack"""
        self.running = False
