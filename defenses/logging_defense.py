# secure-sim/defenses/logging_defense.py
import logging


def setup_logging():
    logging.basicConfig(filename='data/simulation.log', level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    logging.info("Logging initialized.")


def log_anomaly(message):
    logging.warning(f"Anomaly detected: {message}")
