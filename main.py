# secure-sim/main.py
import time
import argparse
import random
from process_sim.water_tank import WaterTank
from control_logic.control import Controller
from attacks.replay_attack import ReplayAttack
from attacks.false_data_injection import FalseDataInjectionAttack
from attacks.dos_attack import DoSAttack
from defenses.logging_defense import setup_logging, log_anomaly, setup_console_logging, stop_console_logging
from defenses.anomaly_detection import anomaly_detector
from defenses.authentication import command_authenticator
from scada_ui.dashboard import start_dashboard, update_water_level


def simulation_loop(tank, attacks=None, defenses_enabled=False, demo_mode=False):
    """Simplified main simulation loop"""
    if attacks is None:
        attacks = {}

    # Simplified demo mode sequence
    attack_modes = ['none', 'replay', 'false_data', 'dos', 'none_with_defense', 
                    'replay_with_defense', 'false_data_with_defense', 'dos_with_defense']
    attack_index = 0
    active_attack = attack_modes[attack_index]
    attack_start_time = time.time()
    attack_duration = 15  # seconds per attack mode
    
    # Tracking for defense status
    defense_active = defenses_enabled
    # Flag to track if we've completed a full demo cycle
    demo_complete = False
    
    while True:
        # Demo mode attack cycling
        if demo_mode and time.time() - attack_start_time > attack_duration:
            # Stop current attack if running
            current_attack = active_attack.split('_with_defense')[0]
            if current_attack in attacks and current_attack != 'none':
                attacks[current_attack].stop()
                
            # Move to next attack mode
            attack_index += 1
            
            # Check if we've gone through all attack modes
            if attack_index >= len(attack_modes):
                print("\n" + "="*60)
                print("[DEMO COMPLETE] Demonstration has finished")
                print("[DEMO COMPLETE] All attack and defense scenarios have been shown")
                print("="*60 + "\n")
                log_anomaly("[DEMO] Demonstration complete [TYPE:NORMAL]")
                
                # Stop all attacks to ensure clean exit
                for attack in attacks.values():
                    if hasattr(attack, 'running') and attack.running:
                        attack.stop()
                
                # Exit the simulation loop
                break
                
            active_attack = attack_modes[attack_index]
            attack_start_time = time.time()
            
            # Check if we're entering defense mode
            with_defense = '_with_defense' in active_attack
            if with_defense and not defense_active:
                defense_active = True
                print(f"\n[DEMO] ACTIVATING DEFENSE MECHANISMS")
                log_anomaly(f"[DEFENSE] Security systems activated - Starting defense monitoring")
                # Extra log specifically for dashboard to detect defense mode
                log_anomaly(f"[DEMO] Now demonstrating: Defense Active Mode [TYPE:DEFENSE]")
            
            # Start the new attack if needed
            base_attack = active_attack.split('_with_defense')[0] 
            if base_attack != 'none' and base_attack in attacks:
                attacks[base_attack].start()
                
            # Log current mode for dashboard with explicit attack type
            display_name = active_attack.replace('_', ' ').title()
            
            # Determine the appropriate type tag
            if with_defense:
                # If this is a defense mode, tag it as DEFENSE
                attack_type = "DEFENSE"
            elif base_attack == 'none':
                attack_type = "NORMAL"
            else:
                attack_type = "ATTACK"
                
            # Log with explicit type tag for UI to detect
            log_anomaly(f"[DEMO] Now demonstrating: {display_name} [TYPE:{attack_type}]")
            print(f"[DEMO] Now demonstrating: {display_name} [{attack_type}]")
        
        # Update water tank state
        current_level = tank.update(dt=1)
        reported_level = current_level
        
        # Set tank inflow/outflow for demo mode based on the current phase
        if demo_mode:
            base_attack = active_attack.split('_with_defense')[0]
            current_level_value = tank.get_level()
            
            # Normal operation: maintain level around 30-40
            if base_attack == 'none':
                if current_level_value < 30:
                    tank.set_inflow(3.0)
                    tank.set_outflow(1.0)
                elif current_level_value > 40:
                    tank.set_inflow(1.0)
                    tank.set_outflow(3.0)
                else:
                    tank.set_inflow(2.0)
                    tank.set_outflow(2.0)
            # Simple oscillation for attack scenarios
            else:
                phase_time = time.time() - attack_start_time
                if phase_time % 6 < 3:
                    tank.set_inflow(3.0)
                    tank.set_outflow(1.5)
                else:
                    tank.set_inflow(1.5)
                    tank.set_outflow(3.0)
        
        # Apply attack effects
        with_defense = '_with_defense' in active_attack if demo_mode else defense_active
            
        # Replay attack
        if 'replay' in attacks and attacks['replay'].running:
            reported_level = attacks['replay'].attack_value
            print(f"[Replay Attack] Spoofed sensor reading: {reported_level}")
            log_anomaly(f"[DEMO] Now demonstrating: Replay Attack [TYPE:ATTACK]")
            
            # Defense: anomaly detection may correct the value
            if with_defense and random.random() < 0.7:
                reported_level = current_level * 0.7 + reported_level * 0.3
                print(f"[DEFENSE] Anomaly detection partially corrected level: {reported_level:.2f}")
                log_anomaly(f"[DEFENSE] Anomaly detection identified replay attack")
        
        # False data injection attack
        if 'false_data' in attacks and attacks['false_data'].running:
            reported_level = attacks['false_data'].get_false_reading(reported_level)
            print(f"[False Data Attack] Manipulated sensor reading: {reported_level}")
            log_anomaly(f"[DEMO] Now demonstrating: False Data Attack [TYPE:ATTACK]")
            
            # Defense: anomaly detection has a chance to partially correct
            if with_defense and random.random() < 0.5:
                correction = random.uniform(0.3, 0.8)
                reported_level = current_level * correction + reported_level * (1-correction)
                print(f"[DEFENSE] Partially corrected false data: {reported_level:.2f}")
                log_anomaly(f"[DEFENSE] Anomaly detection identified false data injection")
        
        # DoS attack
        if 'dos' in attacks and attacks['dos'].running:
            reported_level = attacks['dos'].get_delayed_reading(reported_level)
            print(f"[DoS Attack] Delayed sensor reading: {reported_level}")
            log_anomaly(f"[DEMO] Now demonstrating: DoS Attack [TYPE:ATTACK]")
            
            # Defense: authentication allows backup readings
            if with_defense and random.random() < 0.6:
                cmd = "get_backup_reading"
                timestamp = time.time()
                signature = command_authenticator.generate_hmac(cmd, timestamp)
                
                if command_authenticator.authenticate_command(cmd, timestamp, signature):
                    backup_reading = current_level + random.uniform(-1, 1)
                    reported_level = backup_reading
                    print(f"[DEFENSE] Using authenticated backup reading: {reported_level:.2f}")
                    log_anomaly(f"[DEFENSE] Command authentication activated backup system")
        
        # Log water levels
        print(f"Water Tank Level - Reported: {reported_level:.1f}, Actual: {current_level:.1f}")
        
        # Update UI with both values
        update_water_level(reported_level, current_level)
        
        # Basic safety check
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
    console_log_file = setup_console_logging()
    setup_logging()
    
    # Initialize the water tank simulation
    tank = WaterTank(capacity=100.0, initial_level=10.0)
    
    # Start the control logic
    controller = Controller(tank, setpoint=50.0)
    if args.demo:
        controller.set_manual_control(True)
    controller.start()
    
    # Initialize attacks
    attacks = {}
    attacks['replay'] = ReplayAttack(tank)
    attacks['false_data'] = FalseDataInjectionAttack(tank)
    attacks['dos'] = DoSAttack(tank)
    
    # Start attacks if needed (for non-demo mode)
    if not args.demo:
        if args.attack == 'replay' or args.attack == 'all':
            attacks['replay'].start()
        if args.attack == 'false_data' or args.attack == 'all':
            attacks['false_data'].start()
        if args.attack == 'dos' or args.attack == 'all':
            attacks['dos'].start()
    else:
        print("[DEMO MODE] Starting demonstration - will cycle through attacks")
        log_anomaly("[DEMO] Now demonstrating: Normal Operation [TYPE:NORMAL]")
    
    # Start the dashboard UI
    start_dashboard()
    
    # Run the main simulation loop
    try:
        simulation_loop(tank, attacks, args.defense, args.demo)
        if args.demo:
            print("\nDemo completed successfully! All attack and defense scenarios have been demonstrated.")
            print("You can run the demo again with: python main.py --demo")
            print("Or try individual attack modes with: python main.py --attack [replay|false_data|dos|all]")
    except KeyboardInterrupt:
        print("Simulation terminated by user.")
    finally:
        controller.stop()
        for attack in attacks.values():
            attack.stop()
        stop_console_logging(console_log_file)


if __name__ == "__main__":
    main()
