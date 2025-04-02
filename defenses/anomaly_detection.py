# secure-sim/defenses/anomaly_detection.py
import logging
import threading
import time
import numpy as np
from collections import deque


class AnomalyDetector:
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.level_history = deque(maxlen=window_size)
        self.rate_of_change_history = deque(maxlen=window_size)
        self.running = False
        self.detected_anomalies = []
        
        # Statistical threshold parameters
        self.z_score_threshold = 3.0  # Number of standard deviations for anomaly
        self.min_samples = 10  # Minimum samples needed before detection starts
        
    def add_observation(self, value):
        """Add a new observation to the history window."""
        # Calculate rate of change if possible
        if len(self.level_history) > 0:
            rate_of_change = value - self.level_history[-1]
            self.rate_of_change_history.append(rate_of_change)
        
        # Add the value to history
        self.level_history.append(value)
        
        # Run anomaly checks if we have enough data
        if len(self.level_history) >= self.min_samples:
            return self.check_anomalies(value)
        return None
        
    def check_anomalies(self, current_value):
        """Check for different types of anomalies in the data."""
        anomalies = []
        
        # 1. Z-score anomaly for water level
        level_mean = np.mean(list(self.level_history)[:-1])  # Exclude current value
        level_std = np.std(list(self.level_history)[:-1])
        
        if level_std > 0:  # Prevent division by zero
            z_score = abs(current_value - level_mean) / level_std
            if z_score > self.z_score_threshold:
                anomaly = {
                    'type': 'level_outlier',
                    'value': current_value,
                    'z_score': z_score,
                    'threshold': self.z_score_threshold,
                    'timestamp': time.time()
                }
                anomalies.append(anomaly)
                logging.warning(f"Anomaly detected: Level outlier with z-score {z_score:.2f}")
        
        # 2. Rate of change anomaly
        if len(self.rate_of_change_history) >= self.min_samples:
            roc_mean = np.mean(list(self.rate_of_change_history)[:-1])
            roc_std = np.std(list(self.rate_of_change_history)[:-1])
            
            if len(self.rate_of_change_history) > 0:
                current_roc = self.rate_of_change_history[-1]
                
                if roc_std > 0:  # Prevent division by zero
                    roc_z_score = abs(current_roc - roc_mean) / roc_std
                    if roc_z_score > self.z_score_threshold:
                        anomaly = {
                            'type': 'rate_of_change_outlier',
                            'value': current_roc,
                            'z_score': roc_z_score,
                            'threshold': self.z_score_threshold,
                            'timestamp': time.time()
                        }
                        anomalies.append(anomaly)
                        logging.warning(f"Anomaly detected: Rate of change outlier with z-score {roc_z_score:.2f}")
        
        # Store detected anomalies
        if anomalies:
            self.detected_anomalies.extend(anomalies)
        
        return anomalies if anomalies else None
    
    def get_detected_anomalies(self):
        """Return all detected anomalies."""
        return self.detected_anomalies
    
    def clear_anomalies(self):
        """Clear the list of detected anomalies."""
        self.detected_anomalies = []


# Singleton instance
anomaly_detector = AnomalyDetector()