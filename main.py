# secure-sim/main.py
import time
import argparse
from process_sim.water_tank import WaterTank
from control_logic.control import Controller
from attacks.replay_attack import ReplayAttack
from attacks.false_data_injection import FalseDataInjectionAttack
from attacks.dos_attack import DoSAttack
from defenses.logging_defense import setup_logging, log_anomaly
from defenses.anomaly_detection import anomaly_detector
from defenses.authentication import command_authenticator
from scada_ui.dashboard import start_dashboard, update_water_level


def simulation_loop(tank, attacks=None, defenses_enabled=False, demo_mode=False):
    """
    Main simulation loop that handles all processes
    """
    if attacks is None:
        attacks = {}

    # For demo mode cycling
    # First half shows attacks without defense, second half with defense
    attack_names = ['none', 'replay', 'false_data', 'dos', 'defense_transition', 'none_with_defense', 'replay_with_defense', 'false_data_with_defense', 'dos_with_defense']
    attack_index = 0
    active_attack = attack_names[attack_index]  # Initialize with first attack name
    attack_start_time = time.time()
    attack_duration = 30  # seconds per attack in demo mode
    
    # Tracking defense activation
    defense_active = False
    anomaly_triggered = False
    auth_triggered = False
    
    while True:
        # In demo mode, cycle through attacks
        if demo_mode:
            current_time = time.time()
            # Time to switch to next attack?
            if current_time - attack_start_time > attack_duration:
                # Stop current attack if any
                current_base_attack = active_attack.split('_with_defense')[0] if active_attack and '_with_defense' in active_attack else active_attack
                if current_base_attack and current_base_attack != 'none' and current_base_attack in attacks:
                    print(f"\n[DEMO] Stopping {current_base_attack} attack")
                    attacks[current_base_attack].stop()
                
                # Move to next attack
                attack_index = (attack_index + 1) % len(attack_names)
                active_attack = attack_names[attack_index]
                attack_start_time = current_time
                
                # Handle special case for defense transition
                if active_attack == 'defense_transition':
                    defense_active = True
                    print(f"\n{'='*60}")
                    print(f"[DEMO] ACTIVATING DEFENSE MECHANISMS")
                    print(f"[DEMO] The following attacks will now be mitigated")
                    print(f"{'='*60}\n")
                    log_anomaly(f"[DEMO] ACTIVATING DEFENSE MECHANISMS")
                    # Skip to next attack right away
                    attack_index = (attack_index + 1) % len(attack_names)
                    active_attack = attack_names[attack_index]
                
                # Extract base attack name (without the "_with_defense" suffix)
                base_attack = active_attack.split('_with_defense')[0] if '_with_defense' in active_attack else active_attack
                
                # Print demo status with more visible logging
                display_name = base_attack if base_attack != 'none' else 'normal operation'
                if '_with_defense' in active_attack:
                    display_name += " (with defenses active)"
                
                print(f"\n{'='*60}")
                print(f"[DEMO] Now demonstrating: {display_name}")
                print(f"{'='*60}\n")
                # Log to simulation.log for dashboard to pick up
                log_anomaly(f"[DEMO] Now demonstrating: {display_name}")
                
                # Start the new attack
                if base_attack != 'none' and base_attack in attacks:
                    attacks[base_attack].start()
                    
                # Reset defense triggers for the new attack phase
                anomaly_triggered = False
                auth_triggered = False
        
        # Get the actual level from the tank
        current_level = tank.update(dt=1)
        
        # Determine reported level based on active attacks
        reported_level = current_level
        
        # Apply each active attack's effects
        if not demo_mode:
            # In normal mode, apply all active attacks
            if 'replay' in attacks and attacks['replay'].running:
                reported_level = attacks['replay'].attack_value
                print(f"[Replay Attack] Spoofed sensor reading: {reported_level}")
            
            if 'false_data' in attacks and attacks['false_data'].running:
                reported_level = attacks['false_data'].get_false_reading(reported_level)
                print(f"[False Data Attack] Manipulated sensor reading: {reported_level}")
                
            if 'dos' in attacks and attacks['dos'].running:
                reported_level = attacks['dos'].get_delayed_reading(reported_level)
                print(f"[DoS Attack] Delayed sensor reading: {reported_level}")
        else:
            # Extract base attack name without defense suffix
            current_base_attack = active_attack.split('_with_defense')[0] if '_with_defense' in active_attack else active_attack
            with_defense = '_with_defense' in active_attack
            
            # Apply the attack effects but mitigate if defense is active
            if current_base_attack == 'replay' and attacks['replay'].running:
                # Replay attack - sending a fixed spoofed value
                reported_level = attacks['replay'].attack_value
                print(f"[Replay Attack] Spoofed sensor reading: {reported_level}")
                
                # Apply anomaly detection with 50% chance to detect in first 10 seconds,
                # then guaranteed detection after
                if with_defense:
                    anomaly_time = current_time - attack_start_time
                    if anomaly_time > 10 or (anomaly_time > 5 and random.random() > 0.5):
                        if not anomaly_triggered:
                            anomaly_triggered = True
                            print(f"[DEFENSE] Anomaly detection identified replay attack")
                            log_anomaly(f"[DEFENSE] Anomaly detection identified replay attack")
                        # When detected, use actual level 70% of the time
                        if random.random() < 0.7:
                            reported_level = current_level
                            print(f"[DEFENSE] Using actual level: {reported_level}")
            
            elif current_base_attack == 'false_data' and attacks['false_data'].running:
                # False data injection - gradually manipulating sensor readings
                original_level = reported_level
                reported_level = attacks['false_data'].get_false_reading(reported_level)
                print(f"[False Data Attack] Manipulated sensor reading: {reported_level}")
                
                # Apply anomaly detection - harder to detect at first
                if with_defense:
                    anomaly_time = current_time - attack_start_time
                    detection_chance = min(0.9, anomaly_time / 30)  # Probability increases over time
                    if random.random() < detection_chance:
                        if not anomaly_triggered:
                            anomaly_triggered = True
                            print(f"[DEFENSE] Anomaly detection identified false data attack")
                            log_anomaly(f"[DEFENSE] Anomaly detection identified false data injection")
                        # When detected, partially correct the reading (blend actual and reported)
                        correction_factor = random.uniform(0.5, 0.9)  # How much to correct
                        reported_level = reported_level * (1 - correction_factor) + current_level * correction_factor
                        print(f"[DEFENSE] Partially corrected level: {reported_level:.2f}")
                
            elif current_base_attack == 'dos' and attacks['dos'].running:
                # DoS attack - delaying sensor updates
                original_level = reported_level
                reported_level = attacks['dos'].get_delayed_reading(reported_level)
                print(f"[DoS Attack] Delayed sensor reading: {reported_level}")
                
                # Apply command authentication for DoS defense - using backup readings
                if with_defense:
                    cmd = "get_sensor_reading"
                    # Simulate an authorized backup sensor system
                    if not auth_triggered and random.random() < 0.4:
                        auth_triggered = True
                        print(f"[DEFENSE] Command authentication activated backup system")
                        log_anomaly(f"[DEFENSE] Command authentication activated backup system")
                        
                    if auth_triggered:
                        # Simulate getting command from authenticated source
                        timestamp = time.time()
                        signature = command_authenticator.generate_hmac(cmd, timestamp)
                        is_authentic = command_authenticator.authenticate_command(cmd, timestamp, signature)
                        
                        if is_authentic:
                            # If authenticated, use a value closer to the actual level
                            backup_reading = current_level + random.uniform(-2, 2)  # Small noise
                            reported_level = backup_reading
                            print(f"[DEFENSE] Using authenticated backup reading: {reported_level:.2f}")
            
        print(f"Water Tank Level - Reported: {reported_level:.1f}, Actual: {current_level:.1f}")
        
        # Apply defenses if enabled in regular mode (not demo)
        if defenses_enabled and not demo_mode:
            # Anomaly detection
            anomalies = anomaly_detector.add_observation(reported_level)
            if anomalies:
                for anomaly in anomalies:
                    log_anomaly(f"Anomaly detected: {anomaly['type']} with z-score {anomaly['z_score']:.2f}")
                    
                # Make a real adjustment to the reported level based on anomaly detection
                anomaly_correction = 0.6  # How much to correct towards actual value
                original_reported = reported_level
                reported_level = reported_level * (1 - anomaly_correction) + current_level * anomaly_correction
                print(f"[DEFENSE] Anomaly correction applied: {original_reported:.2f} → {reported_level:.2f}")
            
            # Command authentication for control adjustments
            # Every 15 seconds, simulate authentication check on a control command
            if int(time.time()) % 15 == 0:
                # 75% of commands are authentic, 25% are tampered
                is_tampered = random.random() < 0.25
                
                if is_tampered:
                    # Simulate a tampered command
                    cmd = "set_valve_position"
                    timestamp = time.time()
                    # Generate invalid signature
                    signature = "invalid_signature_" + str(timestamp)
                    # This will fail authentication
                    is_authentic = command_authenticator.authenticate_command(cmd, timestamp, signature)
                    if not is_authentic:
                        log_anomaly(f"[DEFENSE] Unauthenticated command rejected: {cmd}")
                else:
                    # Simulate a valid command
                    cmd = "set_valve_position"
                    # Properly sign the command
                    cmd, timestamp, signature = command_authenticator.sign_command(cmd)
                    # This will pass authentication
                    is_authentic = command_authenticator.authenticate_command(cmd, timestamp, signature)
                    if is_authentic:
                        print(f"[DEFENSE] Authenticated command accepted: {cmd}")
        
        # Update UI with both values (reported and actual)
        update_water_level(reported_level, current_level)
        
        # Basic anomaly detection: log if the tank level is out of expected bounds
        if current_level <= 0 or current_level >= tank.capacity:
            log_anomaly(f"Tank level out of bounds: {current_level}")
        
        time.sleep(1)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Secure SCADA Simulation')
    parser.add_argument('--attack', choices=['replay', 'false_data', 'dos', 'all', 'none'], 
                        default='none', help='Attack type to simulate')
    parser.add_argument('--defense', action='store_true', 
                        help='Enable defense mechanisms')
    parser.add_argument('--demo', action='store_true',
                        help='Enable demonstration mode that cycles through attacks')
    args = parser.parse_args()
    
    # Initialize logging
    setup_logging()
    
    # Initialize the water tank simulation
    tank = WaterTank(capacity=100.0, initial_level=50.0)
    
    # Start the control logic
    controller = Controller(tank, setpoint=75.0)  # Increased setpoint to allow higher water levels
    controller.start()
    
    # Initialize attack components
    attacks = {}
    replay_attack = ReplayAttack(tank)
    false_data_attack = FalseDataInjectionAttack(tank)
    dos_attack = DoSAttack(tank)
    
    # Initialize all attacks but don't start them yet
    attacks['replay'] = replay_attack
    attacks['false_data'] = false_data_attack
    attacks['dos'] = dos_attack
    
    # If in demo mode, don't start any attacks yet - they'll be cycled through
    if not args.demo:
        # Activate requested attack(s)
        if args.attack == 'replay' or args.attack == 'all':
            replay_attack.start()
            
        if args.attack == 'false_data' or args.attack == 'all':
            false_data_attack.start()
            
        if args.attack == 'dos' or args.attack == 'all':
            dos_attack.start()
    else:
        print("\n" + "="*60)
        print("[DEMO MODE] Starting demonstration - will cycle through each attack")
        print("="*60 + "\n")
    
    # Start the SCADA dashboard
    start_dashboard()
    
    # Run the main simulation loop
    try:
        simulation_loop(tank, attacks, args.defense, args.demo)
    except KeyboardInterrupt:
        controller.stop()
        # Stop all active attacks
        for attack in attacks.values():
            attack.stop()
        print("Simulation terminated.")


if __name__ == "__main__":
    main()