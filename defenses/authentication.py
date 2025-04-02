# secure-sim/defenses/authentication.py
import time
import hmac
import hashlib
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
import random


class CommandAuthenticator:
    def __init__(self):
        # For a real system, this would be securely stored and regularly rotated
        self.shared_secret = "90fcf5e4-e1be-4390-867a-4bf82be7b13f"
        self.window_size = 5  # Time window in seconds for valid commands
        self.verified_commands = []
        self.rejected_commands = []
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def generate_hmac(self, command, timestamp):
        """Generate HMAC for command authentication."""
        # Combine command and timestamp to ensure uniqueness
        message = f"{command}|{timestamp}"
        # Create HMAC using SHA-256
        signature = hmac.new(
            self.shared_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
        
    def authenticate_command(self, command, timestamp, signature):
        """
        Authenticate a command with its signature.
        Returns True if command is authentic, False otherwise.
        """
        # Verify timestamp is within acceptable window
        current_time = time.time()
        if abs(current_time - timestamp) > self.window_size:
            logging.warning(f"Command rejected: Timestamp outside valid window")
            self.rejected_commands.append({
                'command': command,
                'timestamp': timestamp,
                'reason': 'timestamp_expired'
            })
            return False
            
        # Recalculate HMAC to verify
        expected_signature = self.generate_hmac(command, timestamp)
        
        # Use constant-time comparison to prevent timing attacks
        is_authentic = hmac.compare_digest(signature, expected_signature)
        
        if is_authentic:
            logging.info(f"Command authenticated: {command}")
            self.verified_commands.append({
                'command': command,
                'timestamp': timestamp,
                'time_verified': current_time
            })
        else:
            logging.warning(f"Command rejected: Invalid signature for {command}")
            self.rejected_commands.append({
                'command': command,
                'timestamp': timestamp,
                'reason': 'invalid_signature'
            })
            
        return is_authentic
        
    def sign_command(self, command):
        """
        Sign a command for sending to the system.
        Returns (command, timestamp, signature) tuple.
        """
        timestamp = time.time()
        signature = self.generate_hmac(command, timestamp)
        return (command, timestamp, signature)
        
    def get_stats(self):
        """Get authentication statistics."""
        return {
            'verified_count': len(self.verified_commands),
            'rejected_count': len(self.rejected_commands),
            'recent_verified': self.verified_commands[-5:] if self.verified_commands else [],
            'recent_rejected': self.rejected_commands[-5:] if self.rejected_commands else []
        }


# Singleton instance
command_authenticator = CommandAuthenticator()