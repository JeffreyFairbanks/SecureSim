# secure-sim/scada_ui/dashboard.py
from flask import Flask, render_template_string, jsonify
import threading
import time
import re
from datetime import datetime

app = Flask(__name__)


# Global variables to store both reported and actual water levels
water_level = 45.0  # Potentially spoofed/reported level (set to a different initial value)
actual_water_level = 75.0  # Actual water level (set to a different initial value)
current_time = datetime.now().strftime('%H:%M:%S')
timestamps = [current_time] * 5  # Pre-populate with initial timestamps
history = [water_level] * 5  # Pre-populate with some initial data points
actual_history = [actual_water_level] * 5  # Pre-populate with some initial data points
MAX_HISTORY = 60  # Increased history size for more data points
last_active_attack = ""  # Track the last active attack for change detection
attack_change_time = time.time()  # When the attack last changed

# Function to extract timestamp from log line
def get_timestamp_from_log(log_line):
    """
    Extract timestamp from a log line and convert to Unix timestamp
    Example log line: "2025-04-02 11:04:25,864:INFO:Logging initialized."
    """
    try:
        # Extract timestamp using regex
        match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+', log_line)
        if match:
            timestamp_str = match.group(1)
            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return dt.timestamp()
    except Exception:
        pass
    
    # Return current time if parsing fails
    return time.time()


@app.route('/')
def dashboard():
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>SecureSim Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
          body {
            background-color: #f8f9fa;
          }
          .dashboard-container {
            max-width: 1000px;
            margin: 50px auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
          }
          .tank-container {
            margin: 20px auto;
            width: 200px;
            height: 300px;
            border: 5px solid #343a40;
            border-top: 2px solid #343a40;
            border-radius: 0 0 15px 15px;
            position: relative;
            overflow: hidden;
          }
          .water {
            background: linear-gradient(to bottom, #4dabf7 0%, #3a8bd8 100%);
            width: 100%;
            position: absolute;
            bottom: 0;
            transition: height 0.5s ease-in-out;
          }
          .tank-markers {
            position: absolute;
            width: 100%;
            height: 100%;
          }
          .tank-marker {
            position: absolute;
            width: 10px;
            height: 1px;
            background-color: rgba(0,0,0,0.2);
            left: 0;
          }
          .tank-marker-label {
            position: absolute;
            left: -25px;
            font-size: 12px;
          }
          .card {
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
          }
          .refresh-time {
            font-size: 12px;
            color: #6c757d;
          }
          .alert-security {
            background-color: #ffebeb;
            border-color: #ff9999;
            color: #cc0000;
            font-weight: bold;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
          }
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
          }
          .discrepancy-value {
            font-size: 1.4em;
            padding: 5px 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #dee2e6;
          }
          .discrepancy-high {
            animation: highlight 2s infinite;
          }
          @keyframes highlight {
            0%, 100% { background-color: #fff0f0; }
            50% { background-color: #ffdddd; }
          }
          .chart-container {
            position: relative;
            height: 300px;
          }
          .current-attack {
            padding: 10px;
            text-align: center;
            margin-bottom: 20px;
            border-radius: 5px;
            font-weight: bold;
            animation: fade 3s infinite;
          }
          @keyframes fade {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
          .defense-event-new {
            animation: defense-highlight 2s ease-in-out;
          }
          @keyframes defense-highlight {
            0%, 100% { background-color: transparent; }
            50% { background-color: rgba(25, 135, 84, 0.2); }
          }
          .countdown {
            font-size: 1.2em;
            margin-top: 5px;
            padding: 5px 0;
            border-top: 1px solid rgba(255,255,255,0.3);
          }
        </style>
      </head>
      <body>
        <div class="container dashboard-container">
          <div class="row mb-4">
            <div class="col text-center">
              <h1 class="fw-bold text-primary">Water Tank Control System</h1>
              <p class="text-secondary">Secure SCADA Simulation Dashboard</p>
              <p class="refresh-time">Last updated: <span id="update-time"></span></p>
            </div>
          </div>
          
          <!-- Active attack status display with countdown -->
          <div class="row mb-3">
            <div class="col">
              <div id="current-attack" class="current-attack bg-warning text-dark d-none">
                <div>Currently Demonstrating: <span id="attack-name">Normal Operation</span></div>
                <div class="countdown">
                  Next attack in: <span id="countdown-timer">30</span> seconds
                </div>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6">
              <div class="card">
                <div class="card-header bg-primary text-white">
                  <h5 class="mb-0">Water Tank Level</h5>
                </div>
                <div class="card-body text-center">
                  <div class="tank-container">
                    <div class="tank-markers" id="tank-markers"></div>
                    <div class="water" id="water-level"></div>
                  </div>
                  <h3 class="mt-3"><span id="level-value" class="text-primary">{{ level }}</span> units</h3>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="card">
                <div class="card-header bg-primary text-white d-flex justify-content-between">
                  <h5 class="mb-0">Level History</h5>
                  <small class="text-white">Showing <span id="history-points">0</span> data points</small>
                </div>
                <div class="card-body">
                  <div class="chart-container">
                    <canvas id="chart"></canvas>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="row mt-4">
            <div class="col-md-12">
              <div class="card" style="border: 4px solid red;">
                <div class="card-header bg-danger text-white">
                  <h5 class="mb-0">⚠️ SECURITY DEMONSTRATION: Reported vs Actual Values ⚠️</h5>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6">
                      <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <div class="tank-container" style="height: 200px; width: 150px; margin-right: 20px; flex-shrink: 0;">
                          <div class="tank-markers" id="spoofed-tank-markers"></div>
                          <div class="water" id="spoofed-water-level" style="background: linear-gradient(to bottom, #ff9999 0%, #cc0000 100%);"></div>
                        </div>
                        <div>
                          <h4>Reported (Spoofed) Level</h4>
                          <h5 class="text-danger" id="spoofed-level-value">{{ level }}</h5>
                        </div>
                      </div>
                      <div class="alert alert-warning" style="margin-top: 10px;">
                        <small>This is what the SCADA system "sees" - potentially manipulated by an attacker</small>
                      </div>
                    </div>
                    
                    <div class="col-md-6">
                      <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <div class="tank-container" style="height: 200px; width: 150px; margin-right: 20px; flex-shrink: 0;">
                          <div class="tank-markers" id="actual-tank-markers"></div>
                          <div class="water" id="actual-water-level" style="background: linear-gradient(to bottom, #99ff99 0%, #00cc00 100%);"></div>
                        </div>
                        <div>
                          <h4>Actual Level</h4>
                          <h5 class="text-success" id="actual-level-value">{{ actual_level }}</h5>
                        </div>
                      </div>
                      <div class="alert alert-success" style="margin-top: 10px;">
                        <small>This is the REAL water level in the tank - typically not visible to operators</small>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="card-footer bg-light py-3">
                  <div class="text-center">
                    <span class="text-danger fw-bold">Discrepancy:</span> 
                    <span id="level-discrepancy" class="discrepancy-value">0.000</span> units
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- System Security Status and Defense Events -->
          <div class="row mt-4">
            <div class="col-md-4 text-center">
              <h6>System Security Status:</h6>
              <span id="security-status" class="badge bg-success px-4 py-2" style="font-size: 1.1em;">Secured</span>
            </div>
            <div class="col-md-8">
              <div class="card">
                <div class="card-header bg-primary text-white d-flex justify-content-between">
                  <h6 class="mb-0">Defense Events</h6>
                </div>
                <div class="card-body p-0">
                  <ul id="defense-events" class="list-group list-group-flush">
                    <li class="list-group-item text-muted small">No defense events detected</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <script>
          // Initial water level rendering
          const waterLevel = {{ level }};
          const actualWaterLevel = {{ actual_level }};
          const levelElement = document.getElementById('level-value');
          const waterElement = document.getElementById('water-level');
          const updateTimeElement = document.getElementById('update-time');
          const historyPointsElement = document.getElementById('history-points');
          const currentAttackElement = document.getElementById('current-attack');
          const attackNameElement = document.getElementById('attack-name');
          const securityStatusElement = document.getElementById('security-status');
          const countdownElement = document.getElementById('countdown-timer');
          
          // Countdown timer variables
          let countdownValue = 30;
          let countdownInterval = null;
          
          // Spoofed vs Actual elements
          const spoofedLevelElement = document.getElementById('spoofed-level-value');
          const actualLevelElement = document.getElementById('actual-level-value');
          const spoofedWaterElement = document.getElementById('spoofed-water-level');
          const actualWaterElement = document.getElementById('actual-water-level');
          const discrepancyElement = document.getElementById('level-discrepancy');
          const defenseEventsElement = document.getElementById('defense-events');

          // Create tank markers for main tank
          const tankMarkers = document.getElementById('tank-markers');
          for (let i = 0; i <= 10; i++) {
            const marker = document.createElement('div');
            marker.className = 'tank-marker';
            marker.style.bottom = `${i * 10}%`;

            const label = document.createElement('div');
            label.className = 'tank-marker-label';
            label.style.bottom = `${i * 10}%`;
            label.innerText = (10 - i) * 10;

            tankMarkers.appendChild(marker);
            tankMarkers.appendChild(label);
          }
          
          // Create tank markers for spoofed and actual tanks
          function createTankMarkers(containerId) {
            const markerContainer = document.getElementById(containerId);
            if (markerContainer) {
              for (let i = 0; i <= 5; i++) {
                const marker = document.createElement('div');
                marker.className = 'tank-marker';
                marker.style.bottom = `${i * 20}%`;
                
                const label = document.createElement('div');
                label.className = 'tank-marker-label';
                label.style.bottom = `${i * 20}%`;
                label.innerText = (5 - i) * 20;
                
                markerContainer.appendChild(marker);
                markerContainer.appendChild(label);
              }
            }
          }
          
          createTankMarkers('spoofed-tank-markers');
          createTankMarkers('actual-tank-markers');

          // Initialize empty chart
          const ctx = document.getElementById('chart').getContext('2d');
          const chart = new Chart(ctx, {
            type: 'line',
            data: {
              labels: Array(60).fill(''),
              datasets: [
                {
                  label: 'Reported Water Level',
                  data: Array(60).fill(null),
                  borderColor: '#4dabf7',
                  tension: 0.2,
                  fill: true,
                  backgroundColor: 'rgba(77, 171, 247, 0.1)'
                },
                {
                  label: 'Actual Water Level',
                  data: Array(60).fill(null),
                  borderColor: '#28a745',
                  borderDash: [5, 5],
                  tension: 0.2,
                  fill: false
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  title: {
                    display: true,
                    text: 'Water Level (units)'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Time'
                  },
                  ticks: {
                    maxRotation: 45,
                    minRotation: 45
                  }
                }
              },
              animation: {
                duration: 500
              },
              plugins: {
                tooltip: {
                  callbacks: {
                    title: function(tooltipItems) {
                      return tooltipItems[0].label || 'Unknown time';
                    }
                  }
                }
              }
            }
          });

          // Update function
          function updateDashboard() {
            fetch('/api/water-level')
              .then(response => response.json())
              .then(data => {
                // Update main water level display
                const newLevel = data.level;
                const newActualLevel = data.actual_level;
                const height = Math.min(Math.max(newLevel, 0), 100);
                const actualHeight = Math.min(Math.max(newActualLevel, 0), 100);
                
                // Update main display
                waterElement.style.height = `${height}%`;
                levelElement.innerText = newLevel.toFixed(3);
                
                // Update spoofed vs actual display
                spoofedWaterElement.style.height = `${height}%`;
                actualWaterElement.style.height = `${actualHeight}%`;
                spoofedLevelElement.innerText = newLevel.toFixed(3);
                actualLevelElement.innerText = newActualLevel.toFixed(3);
                
                // Calculate and display discrepancy with more decimal places
                const discrepancy = Math.abs(newLevel - newActualLevel).toFixed(3);
                discrepancyElement.innerText = discrepancy;
                
                // If there's a significant discrepancy, highlight it
                if (discrepancy > 5) {
                  discrepancyElement.className = 'discrepancy-value text-danger fw-bold discrepancy-high';
                  securityStatusElement.className = 'badge bg-danger';
                  securityStatusElement.innerText = 'Potential Attack';
                } else if (discrepancy > 0.5) {
                  discrepancyElement.className = 'discrepancy-value text-warning fw-bold';
                  securityStatusElement.className = 'badge bg-warning text-dark';
                  securityStatusElement.innerText = 'Suspicious';
                } else {
                  discrepancyElement.className = 'discrepancy-value text-dark fw-bold';
                  securityStatusElement.className = 'badge bg-success';
                  securityStatusElement.innerText = 'Secured';
                }

                // Update time
                const currentTime = new Date().toLocaleTimeString();
                updateTimeElement.innerText = currentTime;
                
                // Show the active attack name if provided
                if (data.active_attack) {
                  currentAttackElement.classList.remove('d-none');
                  const currentAttack = data.active_attack;
                  attackNameElement.innerText = currentAttack;
                  
                  // Set appropriate colors based on attack type
                  currentAttackElement.className = 'current-attack';
                  
                  const withDefense = currentAttack.includes('defense') || 
                                     currentAttack.includes('with_defense');
                  
                  // Extract base attack name
                  let baseAttack = currentAttack;
                  if (baseAttack.includes('with_defense')) {
                    baseAttack = baseAttack.split('_with_defense')[0];
                  }
                  
                  if (currentAttack === 'defense_transition') {
                    // Special case for defense transition
                    currentAttackElement.classList.add('bg-primary', 'text-white');
                    attackNameElement.innerText = 'ACTIVATING DEFENSE MECHANISMS';
                  } else if (baseAttack.includes('replay')) {
                    currentAttackElement.classList.add('bg-danger', 'text-white');
                    attackNameElement.innerText = withDefense ? 
                      'Replay Attack (with defenses)' : 'Replay Attack';
                  } else if (baseAttack.includes('false_data')) {
                    currentAttackElement.classList.add('bg-warning', 'text-dark');
                    attackNameElement.innerText = withDefense ? 
                      'False Data Injection (with defenses)' : 'False Data Injection';
                  } else if (baseAttack.includes('dos')) {
                    currentAttackElement.classList.add('bg-info', 'text-dark');
                    attackNameElement.innerText = withDefense ? 
                      'DoS Attack (with defenses)' : 'DoS Attack';
                  } else if (baseAttack.includes('none') || baseAttack.includes('Normal')) {
                    currentAttackElement.classList.add('bg-success', 'text-white');
                    attackNameElement.innerText = withDefense ? 
                      'Normal Operation (with defenses)' : 'Normal Operation';
                  }
                  
                  // Use server-provided time remaining for countdown
                  countdownValue = data.time_remaining;
                  countdownElement.innerText = countdownValue;
                  
                  // Reset the timer if the attack just changed
                  if (data.timestamp_changed) {
                    if (countdownInterval) {
                      clearInterval(countdownInterval);
                    }
                    countdownInterval = setInterval(() => {
                      countdownValue = Math.max(0, countdownValue - 1);
                      countdownElement.innerText = countdownValue;
                    }, 1000);
                  }
                } else {
                  currentAttackElement.classList.add('d-none');
                  if (countdownInterval) {
                    clearInterval(countdownInterval);
                    countdownInterval = null;
                  }
                }

                // Update history counter
                historyPointsElement.innerText = data.history.length;

                // Update chart with both datasets and timestamps
                chart.data.datasets[0].data = data.history;
                chart.data.datasets[1].data = data.actual_history;
                chart.data.labels = data.timestamps;
                chart.update();
                
                // Update defense events display
                if (data.defense_status && data.defense_status.length > 0) {
                  // Clear the list
                  defenseEventsElement.innerHTML = '';
                  
                  // Add each defense event
                  data.defense_status.forEach(event => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item py-1 text-info';
                    
                    // Extract just the relevant part of the message
                    let eventText = event;
                    if (event.includes('[DEFENSE]')) {
                      eventText = event.split('[DEFENSE]')[1].trim();
                    }
                    
                    // Add an appropriate icon
                    if (event.includes('Anomaly detection')) {
                      li.innerHTML = `<i class="bi bi-graph-up"></i> ${eventText}`;
                      li.classList.add('text-warning');
                    } else if (event.includes('authentication')) {
                      li.innerHTML = `<i class="bi bi-shield-check"></i> ${eventText}`;
                      li.classList.add('text-primary');
                    } else {
                      li.innerHTML = `<i class="bi bi-check-circle"></i> ${eventText}`;
                    }
                    
                    defenseEventsElement.appendChild(li);
                  });
                  
                  // If there are no defense events but with_defense is in attack name,
                  // show a "monitoring" message
                  if (data.defense_status.length === 0 && data.active_attack.includes('defense')) {
                    const li = document.createElement('li');
                    li.className = 'list-group-item py-1 text-muted';
                    li.innerHTML = 'Defense systems monitoring...';
                    defenseEventsElement.appendChild(li);
                  }
                } else if (data.active_attack && data.active_attack.includes('defense')) {
                  // If defense mode but no events yet
                  defenseEventsElement.innerHTML = '';
                  const li = document.createElement('li');
                  li.className = 'list-group-item py-1 text-muted';
                  li.innerHTML = 'Defense systems monitoring...';
                  defenseEventsElement.appendChild(li);
                } else {
                  // If no defense mode and no events
                  defenseEventsElement.innerHTML = '';
                  const li = document.createElement('li');
                  li.className = 'list-group-item text-muted small';
                  li.innerHTML = 'No defense events detected';
                  defenseEventsElement.appendChild(li);
                }
              });
          }

          // Initial rendering
          waterElement.style.height = `${Math.min(Math.max(waterLevel, 0), 100)}%`;
          if (spoofedWaterElement) {
            spoofedWaterElement.style.height = `${Math.min(Math.max(waterLevel, 0), 100)}%`;
          }
          if (actualWaterElement) {
            actualWaterElement.style.height = `${Math.min(Math.max(actualWaterLevel, 0), 100)}%`;
          }
          updateTimeElement.innerText = new Date().toLocaleTimeString();

          // Periodic updates
          setInterval(updateDashboard, 2000);
        </script>
      </body>
    </html>
    """
    return render_template_string(html, level=water_level, actual_level=actual_water_level)


@app.route('/api/water-level')
def api_water_level():
    global history, actual_history, timestamps, last_active_attack, attack_change_time
    
    # Get active attack and defense status from the console output
    active_attack = ""
    defense_status = []
    
    with open('data/simulation.log', 'r') as f:
        try:
            lines = f.readlines()
            
            # Look for the most recent attack demo message
            for line in reversed(lines[-50:]):
                if "DEMO" in line and "demonstrating" in line:
                    parts = line.split("demonstrating:")
                    if len(parts) > 1:
                        active_attack = parts[1].strip()
                    break
            
            # Look for any defense activations in the last 100 lines 
            for line in reversed(lines[-100:]):
                if "DEFENSE" in line:
                    # Only collect the last 10 seconds of defense messages
                    if time.time() - get_timestamp_from_log(line) < 10:
                        defense_status.append(line.strip())
        except Exception as e:
            print(f"Error parsing log: {e}")
            pass
    
    # Detect if attack has changed
    timestamp_changed = False
    if active_attack != last_active_attack and active_attack:
        timestamp_changed = True
        last_active_attack = active_attack
        attack_change_time = time.time()
    
    # Calculate time remaining until next attack
    time_elapsed = time.time() - attack_change_time
    time_remaining = max(0, 30 - int(time_elapsed))
    
    return jsonify({
        'level': water_level,
        'actual_level': actual_water_level,
        'history': history,
        'actual_history': actual_history,
        'timestamps': timestamps,
        'active_attack': active_attack,
        'timestamp_changed': timestamp_changed,
        'time_remaining': time_remaining,
        'defense_status': defense_status[-3:] if defense_status else []  # Return last 3 defense messages
    })


def update_water_level(new_level, new_actual_level=None):
    global water_level, actual_water_level, history, actual_history, timestamps
    water_level = new_level
    
    # If actual level is provided, update it (otherwise keep the spoofed value as actual too)
    if new_actual_level is not None:
        actual_water_level = new_actual_level
    else:
        actual_water_level = new_level

    # Add timestamp for this data point
    current_time = datetime.now().strftime('%H:%M:%S')
    timestamps.append(current_time)
    
    # Add to history and maintain maximum size
    history.append(new_level)
    actual_history.append(actual_water_level)
    
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
        actual_history = actual_history[-MAX_HISTORY:]
        timestamps = timestamps[-MAX_HISTORY:]


def run_dashboard():
    app.run(debug=True, use_reloader=False)


def start_dashboard():
    thread = threading.Thread(target=run_dashboard)
    thread.daemon = True
    thread.start()
    return thread