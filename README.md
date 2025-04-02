# SecureSim: SCADA Security Simulation Platform

A simplified demonstration platform showcasing industrial control system security concepts through a water tank simulation with interactive attack and defense scenarios.

## 📋 Overview

SecureSim simulates attacks and defenses on an industrial control system (water tank) with a visual web dashboard. It's designed for educational purposes to show both normal operations and the effects of common cyber attacks on critical infrastructure.

### Core Features

- **Physical Process Simulation**: Water tank with inflow/outflow dynamics
- **Attack Simulations**: Replay, False Data Injection, and DoS attacks
- **Defense Mechanisms**: Anomaly detection, command authentication, logging
- **Interactive Dashboard**: Real-time visualization of system state
- **Demo Mode**: Automated demonstration of all attacks and defenses

## 🛠️ Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

```bash
# Clone repository
git clone https://github.com/JeffreyFairbanks/SecureSim.git
cd SecureSim

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

Run the automated demo mode (recommended for first-time users):
```bash
python main.py --demo
```

Then open your browser and go to: `http://127.0.0.1:5000/`

The demo will cycle through:
1. Normal operation
2. Three attacks (Replay, False Data Injection, DoS)
3. Defense mode with all three attacks
4. Complete automatically

### Other Run Options

```bash
# Run specific attacks:
python main.py --attack replay
python main.py --attack false_data
python main.py --attack dos
python main.py --attack all

# Enable defenses:
python main.py --attack all --defense
```

## 🔎 Dashboard Features

![Dashboard Screenshot](https://i.imgur.com/example.png)

The web interface provides:

1. **Status Banner**: Color-coded indicator showing current mode:
   - Green: Normal operation
   - Red: Attack in progress 
   - Yellow: Defense mode active

2. **Defense Event Log**: Real-time log of security events

3. **Water Tank Visualization**: Shows actual vs. reported levels

4. **Level History Chart**: Tracks trends over time

5. **Security Status**: Shows detected discrepancies

## 🔐 Security Concepts Demonstrated

### Attack Types
- **Replay Attack**: Fixed spoofed sensor values
- **False Data Injection**: Gradually manipulated readings
- **Denial of Service (DoS)**: Delayed/stale data

### Defense Mechanisms
- **Anomaly Detection**: Statistical detection of suspicious patterns
- **Command Authentication**: HMAC-based validation
- **Logging**: Security event tracking
- **Backup Systems**: Redundant sensor readings

## 📁 Project Structure

```
SecureSim/
├── attacks/            # Attack implementations
├── control_logic/      # Control system logic
├── data/               # Log files
├── defenses/           # Security mechanisms
├── process_sim/        # Physical process simulation
├── scada_ui/           # Web dashboard
└── tests/              # Unit tests
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.