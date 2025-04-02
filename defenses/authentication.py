# secure-sim/defenses/authentication.py
import time
import hmac
import hashlib
import logging


class CommandAuthenticator:
    """Simple HMAC-based command authentication system"""
    def __init__(self):
        # Shared secret key (in a real system, this would be securely stored)
        self.shared_secret = "90fcf5e4-e1be-4390-867a-4bf82be7b13f"
        self.time_window = 5  # Time window in seconds for valid commands
        
    def generate_hmac(self, command, timestamp):
        """Generate an HMAC signature for command authentication"""
        # Combine command and timestamp to create a unique message
        message = f"{command}|{timestamp}"
        
        # Create HMAC signature using SHA-256
        signature = hmac.new(
            self.shared_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
        
    def authenticate_command(self, command, timestamp, signature):
        """Verify if a command is authentic based on its signature"""
        # Check if timestamp is within acceptable time window
        current_time = time.time()
        if abs(current_time - timestamp) > self.time_window:
            logging.warning(f"Command rejected: Timestamp outside valid window")
            return False
            
        # Calculate the expected signature
        expected_signature = self.generate_hmac(command, timestamp)
        
        # Use constant-time comparison to prevent timing attacks
        is_authentic = hmac.compare_digest(signature, expected_signature)
        
        if is_authentic:
            logging.info(f"Command authenticated: {command}")
        else:
            logging.warning(f"Command rejected: Invalid signature for {command}")
            
        return is_authentic
        
    def sign_command(self, command):
        """Sign a command for sending to the system"""
        timestamp = time.time()
        signature = self.generate_hmac(command, timestamp)
        return (command, timestamp, signature)


# Singleton instance
command_authenticator = CommandAuthenticator()