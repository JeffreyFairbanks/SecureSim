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


def simulation_loop(tank, attacks=None, defenses_enabled=False):
    """
    Main simulation loop that handles all processes
    """
    if attacks is None:
        attacks = {}

    while True:
        # Get the actual level from the tank
        current_level = tank.update(dt=1)
        
        # Determine reported level based on active attacks
        reported_level = current_level
        
        # Apply each active attack's effects
        if 'replay' in attacks and attacks['replay'].running:
            reported_level = attacks['replay'].attack_value
            print(f"[Replay Attack] Spoofed sensor reading: {reported_level}")
        
        if 'false_data' in attacks and attacks['false_data'].running:
            reported_level = attacks['false_data'].get_false_reading(reported_level)
            print(f"[False Data Attack] Manipulated sensor reading: {reported_level}")
            
        if 'dos' in attacks and attacks['dos'].running:
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
    args = parser.parse_args()
    
    # Initialize logging
    setup_logging()
    
    # Initialize the water tank simulation
    tank = WaterTank(capacity=100.0, initial_level=50.0)
    
    # Start the control logic
    controller = Controller(tank, setpoint=50.0)
    controller.start()
    
    # Initialize attack components
    attacks = {}
    replay_attack = ReplayAttack(tank)
    false_data_attack = FalseDataInjectionAttack(tank)
    dos_attack = DoSAttack(tank)
    
    # Activate requested attack(s)
    if args.attack == 'replay' or args.attack == 'all':
        attacks['replay'] = replay_attack
        replay_attack.start()
        
    if args.attack == 'false_data' or args.attack == 'all':
        attacks['false_data'] = false_data_attack
        false_data_attack.start()
        
    if args.attack == 'dos' or args.attack == 'all':
        attacks['dos'] = dos_attack
        dos_attack.start()
    
    # Start the SCADA dashboard
    start_dashboard()
    
    # Run the main simulation loop
    try:
        simulation_loop(tank, attacks, args.defense)
    except KeyboardInterrupt:
        controller.stop()
        # Stop all active attacks
        for attack in attacks.values():
            attack.stop()
        print("Simulation terminated.")


if __name__ == "__main__":
    main()