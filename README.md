# SecureSim: SCADA Security Simulation Platform

SecureSim demonstrates industrial control system security concepts by simulating a water tank control system with a visual dashboard. This platform showcases both normal operations and the effects of cyber attacks on industrial control systems.

## 📋 Project Overview

This project simulates an industrial control system (water tank), implements various cyber-attacks against it, and demonstrates security defenses. The simulation is built as a 3-week project with the following components:

### Week 1: System Modeling & Control Logic
- Water tank simulation with physics-based level calculation
- Feedback controller for maintaining setpoint
- Thread-safe operations for real-time simulation
- Web dashboard for monitoring

### Week 2: Attack Implementation
- **Replay Attack**: Spoofs sensor readings with static values
- **False Data Injection**: Gradually manipulates sensor readings
- **Denial of Service (DoS)**: Simulates communication delays

### Week 3: Defense Mechanisms
- **Logging and Auditing**: Records system events and anomalies
- **Anomaly Detection**: Statistical analysis to detect suspicious behavior
- **Command Authentication**: HMAC-based verification of control commands

## 📁 Project Structure

```
secure-sim/
├── attacks/               # Attack simulations
│   ├── replay_attack.py         # Simple sensor value spoofing
│   ├── false_data_injection.py  # Gradual sensor manipulation
│   └── dos_attack.py            # Communication delay simulation
├── control_logic/         # Control algorithms
│   └── control.py              # Proportional controller
├── data/                  # Log files
│   └── simulation.log          # Event and anomaly records
├── defenses/              # Security measures
│   ├── logging_defense.py      # Basic logging configuration
│   ├── anomaly_detection.py    # Statistical anomaly detection
│   └── authentication.py       # Command authentication
├── process_sim/           # Physical process simulation
│   └── water_tank.py           # Water tank physics model
├── scada_ui/              # User interface components
│   └── dashboard.py            # Flask web dashboard
├── tests/                 # Test cases
│   ├── test_water_tank.py      # Tests for tank simulation
│   └── test_attacks.py         # Tests for attack modules
├── main.py                # Main application entry point
├── requirements.txt       # Python dependencies
└── README.md              # This documentation
```

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/secure-sim.git
   cd secure-sim
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🖥️ Usage

1. Run the simulation with selected attacks and defenses:
   ```bash
   # Run with no attacks (normal operation)
   python main.py

   # Run with replay attack
   python main.py --attack replay

   # Run with false data injection
   python main.py --attack false_data
   
   # Run with DoS attack
   python main.py --attack dos
   
   # Run with all attacks
   python main.py --attack all
   
   # Enable defense mechanisms
   python main.py --attack all --defense
   ```

2. Access the dashboard:
   - Open your browser and navigate to `http://127.0.0.1:5000/`
   - The dashboard automatically updates every 2 seconds

3. To stop the simulation:
   - Press `Ctrl+C` in the terminal

4. Run tests:
   ```bash
   python -m unittest discover tests
   ```

## 🔎 Dashboard Features

The web dashboard consists of several components:

1. **Main Water Tank Display**: Shows the current water level with animated fluid visualization
2. **Level History Chart**: Tracks water level changes over time
3. **System Status Panel**: Displays flow rate and security status
4. **Security Demonstration Section**: Highlighted with a red border, showing:
   - Left side: Reported/spoofed water level (what the control system "sees")
   - Right side: Actual water level (what's really in the tank)
   - Discrepancy calculation between reported and actual values

## 🔐 Security Concepts Demonstrated

1. **Sensor Data Integrity**: Visualizes how attackers can manipulate sensor data
2. **Attack Detection**: Shows how comparing expected vs. actual behavior can reveal attacks
3. **System Monitoring**: Demonstrates the importance of logging and anomaly detection
4. **Authentication**: Shows how to verify the authenticity of control commands

## 💡 Educational Use Cases

1. **Cybersecurity Training**: Demonstrate SCADA vulnerabilities to security professionals
2. **Engineering Education**: Teach control system principles and security considerations
3. **Security Awareness**: Show non-technical stakeholders the potential impact of cyber attacks

## 📚 Further Development

Potential enhancements:
- Additional attack vectors (man-in-the-middle)
- More sophisticated defense mechanisms
- Multiple interconnected industrial processes
- User authentication and access control simulation
- Network traffic visualization

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.