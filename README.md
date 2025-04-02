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

2. **Recommended for presentation**: Use the interactive demo mode that automatically cycles through attacks:
   ```bash
   # Demo mode - automatically cycles through all attacks (30 seconds each)
   python main.py --demo
   
   # Demo mode with defenses enabled
   python main.py --demo --defense
   ```
   
   The demo mode features:
   - **Complete Attack Lifecycle**: Starts with normal operation, shows all attacks, then demonstrates defense mechanisms
   - **Structured Demonstration Flow**:
     1. Initial normal operation (baseline system behavior)
     2. Three attacks without defenses (Replay, False Data Injection, DoS)
     3. Clear defense activation transition
     4. Same three attacks with defenses active (showing mitigation)
   - **Interactive Visual Elements**:
     - Countdown timer showing seconds until next phase
     - Color-coded attack status banners
     - Defense event log showing all defense actions with timestamps
     - Real-time visualization of attack effects and defense responses

3. Access the dashboard:
   - Open your browser and navigate to `http://127.0.0.1:5000/`
   - The dashboard automatically updates every 2 seconds

4. To stop the simulation:
   - Press `Ctrl+C` in the terminal

5. Run tests:
   ```bash
   python -m unittest discover tests
   ```

## 🔎 Dashboard Features

The web dashboard consists of several components:

1. **Attack Status Banner**: Displays the currently active attack and countdown to next phase
2. **Defense Event Log**: Time-stamped record of all defense actions with categorization:
   - Shows anomaly detection events with timestamps
   - Displays authentication events when backup systems are activated
   - Maintains history throughout the entire simulation
3. **Main Water Tank Display**: Shows the current water level with animated fluid visualization
4. **Level History Chart**: Tracks water level changes over time with timestamps
5. **Security Demonstration Section**: Highlighted with a red border, showing:
   - Left side: Reported/spoofed water level (what the control system "sees")
   - Right side: Actual water level (what's really in the tank)
   - Detailed discrepancy measurement between reported and actual values
6. **System Security Status**: Color-coded indicator showing security state based on discrepancy levels

## 🔐 Security Concepts Demonstrated

1. **Attack Types**:
   - **Replay Attack**: Shows how attackers can feed fixed sensor readings to control systems
   - **False Data Injection**: Demonstrates gradual manipulation of sensor data to avoid detection
   - **Denial of Service**: Illustrates how delayed data can impact system operations

2. **Defense Mechanisms**:
   - **Statistical Anomaly Detection**: Uses statistical models to identify suspicious variations in data
   - **Command Authentication**: Validates control commands using cryptographic signatures
   - **Redundant Systems**: Shows how backup systems can mitigate service disruptions
   
3. **Security Principles**:
   - **Defense in Depth**: Demonstrates using multiple security layers for better protection
   - **Real-time Monitoring**: Shows the importance of continuous security monitoring
   - **Detection vs. Prevention**: Highlights both preventing attacks and detecting ongoing ones

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