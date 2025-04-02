# SecureSim: Water Tank Control System Simulation

This document explains the core components of SecureSim and how they interact to create a secure SCADA (Supervisory Control and Data Acquisition) simulation.

## System Architecture

The system simulates a water tank control system with cybersecurity features, demonstrating various attack vectors and defense mechanisms in industrial control systems.

```
WaterTank <---> Controller
    ^             ^
    |             |
    v             v
Attack Vectors    Defense Mechanisms
```

## Core Components

### WaterTank Class

The `WaterTank` class simulates a physical water tank process:

- Models a tank with capacity, current level, inflow/outflow rates
- Uses thread-safe operations with locks
- Provides methods to update and query tank state

```python
def update(self, dt=1.0):
    with self.lock:
        change = self.inflow - self.outflow
        self.level += change * dt
        self.level = max(0, min(self.capacity, self.level))
        return self.level
```

### Controller Class

The `Controller` class implements a proportional control algorithm:

- Monitors water tank level and adjusts inflow to maintain setpoint
- Runs in a separate thread for continuous operation
- Supports both automatic and manual control modes

```python
def control_loop(self):
    while self.running:
        if not self.manual_control:
            current_level = self.tank.get_level()
            error = self.setpoint - current_level
            kp = 0.1  # Proportional gain
            control_signal = kp * error
            new_inflow = max(0, min(5, control_signal + 2.5))
            self.tank.set_inflow(new_inflow)
            self.tank.set_outflow(1.0)
        time.sleep(1)
```

## Security Features

### Attack Vectors

1. **Replay Attack**: Returns fixed spoofed sensor values
   ```python
   # Returns a constant value instead of actual tank level
   reported_level = attacks['replay'].attack_value  # Always 75.0
   ```

2. **False Data Injection**: Gradually manipulates sensor readings
   ```python
   # Adds random deviations to sensor data
   deviation = random.uniform(-max_current_deviation, max_current_deviation)
   return true_value + deviation
   ```

3. **Denial of Service (DoS)**: Delays sensor readings to simulate network disruption
   ```python
   # Returns stale data with randomized delays
   update_delay = random.uniform(1.0, self.max_delay)
   # Only updates value if delay time has passed
   ```

### Defense Mechanisms

1. **Anomaly Detection**: Statistical detection of unusual sensor readings
   ```python
   # Z-score based anomaly detection
   z_score = abs(current_value - level_mean) / level_std
   if z_score > self.z_score_threshold:
       # Flag as anomaly
   ```

2. **Command Authentication**: HMAC-based verification of control commands
   ```python
   # Generate and verify command signatures
   signature = hmac.new(
       self.shared_secret.encode(),
       message.encode(),
       hashlib.sha256
   ).hexdigest()
   
   # Use constant-time comparison to prevent timing attacks
   is_authentic = hmac.compare_digest(signature, expected_signature)
   ```

3. **Comprehensive Logging**: Tracks system events and potential security incidents

## Main Simulation Loop

The main function coordinates the entire simulation:

1. Initializes all components (tank, controller, attacks, dashboard)
2. Sets up logging and security features
3. Runs a continuous simulation loop that:
   - Updates water tank state
   - Applies active attacks if enabled
   - Implements defense countermeasures when enabled
   - Updates the UI dashboard
   - Performs safety checks

## Demo Mode

The system includes a demonstration mode that cycles through various attack scenarios with and without defenses enabled, providing an educational view of security vulnerabilities and protections in industrial control systems.

```python
attack_modes = ['none', 'replay', 'false_data', 'dos', 'none_with_defense', 
                'replay_with_defense', 'false_data_with_defense', 'dos_with_defense']
```

This architecture illustrates common cybersecurity concerns in industrial control systems and demonstrates practical defense mechanisms that can be implemented to protect critical infrastructure.