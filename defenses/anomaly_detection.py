# secure-sim/defenses/anomaly_detection.py
import logging
import time
import numpy as np
from collections import deque


class AnomalyDetector:
    """Simple statistical anomaly detector for water tank level readings"""
    def __init__(self, window_size=20):
        self.window_size = window_size
        self.level_history = deque(maxlen=window_size)
        self.detected_anomalies = []
        
        # Statistical threshold parameters
        self.z_score_threshold = 2.5  # Number of standard deviations for anomaly
        self.min_samples = 5  # Minimum samples needed before detection starts
        
    def add_observation(self, value):
        """Add a new observation and check for anomalies"""
        # Add the value to history
        self.level_history.append(value)
        
        # Run anomaly checks if we have enough data
        if len(self.level_history) >= self.min_samples:
            return self.check_anomalies(value)
        return None
        
    def check_anomalies(self, current_value):
        """Check for anomalies in the data using z-score method"""
        anomalies = []
        
        # Calculate mean and standard deviation of historical values
        history_list = list(self.level_history)[:-1]  # Exclude current value
        level_mean = np.mean(history_list)
        level_std = np.std(history_list)
        
        # Prevent division by zero
        if level_std > 0:
            # Calculate how many standard deviations the current value is from the mean
            z_score = abs(current_value - level_mean) / level_std
            
            # If z-score exceeds threshold, flag as anomaly
            if z_score > self.z_score_threshold:
                anomaly = {
                    'type': 'level_outlier',
                    'value': current_value,
                    'z_score': z_score,
                    'timestamp': time.time()
                }
                anomalies.append(anomaly)
                logging.warning(f"Anomaly detected: Level outlier with z-score {z_score:.2f}")
        
        # Store detected anomalies
        if anomalies:
            self.detected_anomalies.extend(anomalies)
        
        return anomalies if anomalies else None
    
    def get_detected_anomalies(self):
        """Return all detected anomalies"""
        return self.detected_anomalies
    
    def clear_anomalies(self):
        """Clear the list of detected anomalies"""
        self.detected_anomalies = []


# Singleton instance
anomaly_detector = AnomalyDetector()