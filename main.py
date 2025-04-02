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
    active_attack = None
    attack_names = ['none', 'replay', 'false_data', 'dos']
    attack_index = 0
    attack_start_time = time.time()
    attack_duration = 30  # seconds per attack in demo mode
    
    while True:
        # In demo mode, cycle through attacks
        if demo_mode:
            current_time = time.time()
            # Time to switch to next attack?
            if current_time - attack_start_time > attack_duration:
                # Stop current attack if any
                if active_attack and active_attack in attacks:
                    print(f"\n[DEMO] Stopping {active_attack} attack")
                    attacks[active_attack].stop()
                
                # Move to next attack
                attack_index = (attack_index + 1) % len(attack_names)
                active_attack = attack_names[attack_index]
                attack_start_time = current_time
                
                # Print demo status with more visible logging
                attack_name = active_attack if active_attack != 'none' else 'normal operation'
                print(f"\n{'='*60}")
                print(f"[DEMO] Now demonstrating: {attack_name}")
                print(f"{'='*60}\n")
                # Log to simulation.log for dashboard to pick up
                log_anomaly(f"[DEMO] Now demonstrating: {attack_name}")
                
                # Start the new attack
                if active_attack != 'none' and active_attack in attacks:
                    attacks[active_attack].start()
        
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
            # In demo mode, only apply the currently active attack
            if active_attack == 'replay' and attacks['replay'].running:
                reported_level = attacks['replay'].attack_value
                print(f"[Replay Attack] Spoofed sensor reading: {reported_level}")
            
            elif active_attack == 'false_data' and attacks['false_data'].running:
                reported_level = attacks['false_data'].get_false_reading(reported_level)
                print(f"[False Data Attack] Manipulated sensor reading: {reported_level}")
                
            elif active_attack == 'dos' and attacks['dos'].running:
                reported_level = attacks['dos'].get_delayed_reading(reported_level)
                print(f"[DoS Attack] Delayed sensor reading: {reported_level}")
            
        print(f"Water Tank Level - Reported: {reported_level:.1f}, Actual: {current_level:.1f}")
        
        # Apply defenses if enabled
        if defenses_enabled:
            # Anomaly detection
            anomalies = anomaly_detector.add_observation(reported_level)
            if anomalies:
                for anomaly in anomalies:
                    log_anomaly(f"Anomaly detected: {anomaly['type']} with z-score {anomaly['z_score']:.2f}")
            
            # Command authentication example
            if 'command' in locals():
                cmd, timestamp, signature = command_authenticator.sign_command('adjust_setpoint')
                is_authentic = command_authenticator.authenticate_command(cmd, timestamp, signature)
                if not is_authentic:
                    log_anomaly("Unauthenticated command detected!")
        
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