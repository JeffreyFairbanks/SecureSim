# secure-sim/main.py
import time
from process_sim.water_tank import WaterTank
from control_logic.control import Controller
from attacks.replay_attack import ReplayAttack
from defenses.logging_defense import setup_logging, log_anomaly
from scada_ui.dashboard import start_dashboard, update_water_level


def simulation_loop(tank, replay_attack=None):
    while True:
        # Get the actual level from the tank
        current_level = tank.update(dt=1)
        print(f"Water Tank Level: {current_level}")

        # If we're under attack, use the spoofed value for the reported level
        # and keep the actual level separate
        if replay_attack and replay_attack.running:
            spoofed_level = replay_attack.attack_value
            print(f"[Attack] Spoofed sensor reading: {spoofed_level}")
            # Update UI with both values (spoofed and actual)
            update_water_level(spoofed_level, current_level)
        else:
            # No attack, update with just the real value
            update_water_level(current_level)

        # Basic anomaly detection: log if the tank level is out of expected
        # bounds
        if current_level <= 0 or current_level >= tank.capacity:
            log_anomaly(f"Tank level out of bounds: {current_level}")

        time.sleep(1)


def main():
    # Initialize logging
    setup_logging()

    # Initialize the water tank simulation
    tank = WaterTank(capacity=100.0, initial_level=50.0)

    # Start the control logic
    controller = Controller(tank, setpoint=50.0)
    controller.start()

    # Start the attack simulation
    replay_attack = ReplayAttack(tank)
    replay_attack.start()

    # Start the SCADA dashboard (optional)
    start_dashboard()

    # Run the main simulation loop
    try:
        simulation_loop(tank, replay_attack)
    except KeyboardInterrupt:
        controller.stop()
        replay_attack.stop()
        print("Simulation terminated.")


if __name__ == "__main__":
    main()
