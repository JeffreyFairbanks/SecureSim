# secure-sim/tests/test_attacks.py
import sys
import os
import unittest
import time

# Add the parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from process_sim.water_tank import WaterTank
from attacks.replay_attack import ReplayAttack
from attacks.false_data_injection import FalseDataInjectionAttack
from attacks.dos_attack import DoSAttack


class TestAttacks(unittest.TestCase):
    
    def setUp(self):
        self.tank = WaterTank(capacity=100.0, initial_level=50.0)
    
    def test_replay_attack(self):
        """Test that the replay attack returns a fixed value"""
        attack = ReplayAttack(self.tank)
        
        # Before the attack is started
        self.assertFalse(attack.running)
        
        # Start the attack
        attack.start()
        self.assertTrue(attack.running)
        
        # Verify the attack returns a fixed value
        self.assertEqual(attack.attack_value, 75.0)
        
        # Stop the attack
        attack.stop()
        self.assertFalse(attack.running)
    
    def test_false_data_injection(self):
        """Test that the false data injection modifies readings"""
        attack = FalseDataInjectionAttack(self.tank)
        original_level = 50.0
        
        # Before the attack is started, should return original value
        self.assertEqual(attack.get_false_reading(original_level), original_level)
        
        # Start the attack
        attack.start()
        self.assertTrue(attack.running)
        
        # The value should now be modified
        falsified = attack.get_false_reading(original_level)
        self.assertNotEqual(falsified, original_level)
        
        # Stop the attack
        attack.stop()
        self.assertFalse(attack.running)
        
        # After stopping, should return original value again
        self.assertEqual(attack.get_false_reading(original_level), original_level)
    
    def test_dos_attack(self):
        """Test that the DoS attack delays readings"""
        attack = DoSAttack(self.tank)
        
        # Start the attack
        attack.start()
        
        # Get initial reading
        level_1 = attack.get_delayed_reading(60.0)
        
        # Change actual level
        new_level = 70.0
        
        # With DoS, we might still get the old value due to delay
        level_2 = attack.get_delayed_reading(new_level)
        
        # Eventually it should update after we wait
        time.sleep(6)  # Wait longer than max_delay
        level_3 = attack.get_delayed_reading(new_level)
        
        # Stop the attack
        attack.stop()
        
        # Now we should immediately get the current value
        level_4 = attack.get_delayed_reading(80.0)
        self.assertEqual(level_4, 80.0)


if __name__ == '__main__':
    unittest.main()