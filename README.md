# SecureSim: SCADA Security Simulation Platform

SecureSim demonstrates industrial control system security concepts.
The platform simulates a water tank control system with a visual dashboard,
allowing users to observe both normal operations and the effects of cyber attacks on SCADA systems.

## 📁 Project Structure

```
secure-sim/
├── attacks/               # Attack simulations
├── control_logic/         # Control algorithms
├── data/                  # Log files
├── defenses/              # Security measures
├── process_sim/           # Physical process simulation
├── scada_ui/              # User interface components
├── main.py                # Main application entry point
├── requirements.txt       # Python dependencies
└── README.md              # This documentation
```

### Key Components

#### `main.py`
The application entry point that initializes and coordinates all components:
- Sets up the water tank simulation
- Launches the control logic
- Starts the attack simulation
- Initializes the web dashboard
- Runs the main simulation loop

#### Process Simulation (`process_sim/`)

**`water_tank.py`**: Simulates a water tank with:
- Variable capacity and initial level
- Controllable inflow and outflow rates
- Thread-safe operations
- Physics-based level calculation

#### Control Logic (`control_logic/`)

**`control.py`**: Implements a feedback controller that:
- Monitors the water tank level
- Adjusts inflow/outflow to maintain a target level (setpoint)
- Runs in a separate thread for real-time control

#### Attack Simulations (`attacks/`)

**`replay_attack.py`**: Simulates a replay attack where:
- The attacker spoofs sensor readings
- The control system receives false data
- The dashboard shows the discrepancy between reported and actual values

#### Defense Mechanisms (`defenses/`)

**`logging_defense.py`**: Basic security monitoring with:
- Setup for logging configuration
- Anomaly detection and logging capabilities

#### User Interface (`scada_ui/`)

**`dashboard.py`**: Flask-based web dashboard featuring:
- Modern Bootstrap user interface
- Animated water tank visualization
- Real-time data updates
- Comparison of reported vs. actual system state
- Historical data trends

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

1. Run the simulation:
   ```bash
   python main.py
   ```

2. Access the dashboard:
   - Open your browser and navigate to `http://127.0.0.1:5000/`
   - The dashboard automatically updates every 2 seconds

3. To stop the simulation:
   - Press `Ctrl+C` in the terminal

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

## 💡 Educational Use Cases

1. **Cybersecurity Training**: Demonstrate SCADA vulnerabilities to security professionals
2. **Engineering Education**: Teach control system principles and security considerations
3. **Security Awareness**: Show non-technical stakeholders the potential impact of cyber attacks

## 📚 Further Development

Potential enhancements:
- Additional attack vectors (DoS, man-in-the-middle)
- More sophisticated defense mechanisms
- Multiple interconnected industrial processes
- User authentication and access control simulation
- Network traffic visualization

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.