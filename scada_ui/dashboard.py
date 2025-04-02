# secure-sim/scada_ui/dashboard.py
from flask import Flask, render_template_string, jsonify
import threading
import time
import re
from datetime import datetime

app = Flask(__name__)


# Global variables to store both reported and actual water levels
water_level = 10.0  # Potentially spoofed/reported level
actual_water_level = 10.0  # Actual water level
current_time = datetime.now().strftime('%H:%M:%S')
timestamps = [current_time] * 5  # Pre-populate with initial timestamps
history = [water_level] * 5  # Pre-populate with initial water level
actual_history = [actual_water_level] * 5  # Pre-populate with initial water level
MAX_HISTORY = 30  # Set history size to 30 data points
last_active_attack = ""  # Track the last active attack for change detection
attack_change_time = time.time()  # When the attack last changed

# Store all defense events for historical logging
defense_events = []  # List of defense events with timestamps
MAX_DEFENSE_EVENTS = 100  # Maximum number of defense events to retain

# Clear log file at startup to remove old events
def clear_old_log_entries():
    try:
        with open('data/simulation.log', 'w') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},000:INFO:Log file cleared for new session.\n")
    except Exception as e:
        print(f"Error clearing log file: {e}")

# Clear log at startup
clear_old_log_entries()

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
          
          /* Simple banner styles - overrides all others */
          #current-attack {
            padding: 15px;
            text-align: center;
            margin-bottom: 20px;
            border-radius: 6px;
            font-weight: bold;
            border: 4px solid;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
          }
          /* Banner states */
          .normal-state {
            background-color: #198754 !important; /* Green */
            color: white !important;
            border-color: #198754 !important;
          }
          .attack-state {
            background-color: #dc3545 !important; /* Red */
            color: white !important;
            border-color: #dc3545 !important;
            animation: pulse-red 1.5s infinite !important;
          }
          .defense-state {
            background-color: #ffc107 !important; /* Yellow */
            color: #212529 !important;
            border-color: #ffc107 !important;
          }
          
          @keyframes pulse-red {
            0%, 100% { background-color: #dc3545 !important; }
            50% { background-color: #e04050 !important; }
          }
          
          .countdown {
            font-size: 1.2em;
            margin-top: 5px;
            padding: 5px 0;
            border-top: 1px solid rgba(255,255,255,0.3);
          }
          
          .defense-event-new {
            animation: defense-highlight 2s ease-in-out;
          }
          @keyframes defense-highlight {
            0%, 100% { background-color: transparent; }
            50% { background-color: rgba(25, 135, 84, 0.2); }
          }
        </style>
      </head>
      <body>
        <div class="container dashboard-container">
          <div class="row mb-3">
            <div class="col text-center">
              <h1 class="fw-bold text-primary">Water Tank Control System</h1>
              <p class="text-secondary">Secure SCADA Simulation Dashboard</p>
              <p class="refresh-time">Last updated: <span id="update-time"></span></p>
            </div>
          </div>
          
          <!-- Active attack status display with countdown -->
          <div class="row mb-3">
            <div class="col">
              <div id="current-attack" class="normal-state">
                <div style="font-size: 1.2em;"><strong>Currently Demonstrating:</strong> <span id="attack-name">Normal Operation</span></div>
                <div class="countdown">
                  Next attack in: <span id="countdown-timer">15</span> seconds
                </div>
              </div>
            </div>
          </div>
          
          <!-- Defense Events Section - Moved to top -->
          <div class="row mb-4">
            <div class="col">
              <div class="card">
                <div id="defense-header" class="card-header bg-secondary text-white d-flex justify-content-between">
                  <h5 class="mb-0">Defense Event Log <small id="defense-status"><span class="badge bg-light text-dark ms-2">Inactive</span></small></h5>
                  <span class="badge bg-light text-dark" id="event-count">0 events</span>
                </div>
                <div class="card-body p-0" style="max-height: 200px; overflow-y: auto;">
                  <table class="table table-striped table-hover mb-0">
                    <thead>
                      <tr>
                        <th scope="col" style="width: 100px">Time</th>
                        <th scope="col">Event</th>
                        <th scope="col" style="width: 120px">Type</th>
                      </tr>
                    </thead>
                    <tbody id="defense-events">
                      <tr>
                        <td colspan="3" class="text-center text-muted py-3">No defense events logged</td>
                      </tr>
                    </tbody>
                  </table>
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
          
          <!-- System Security Status -->
          <div class="row mt-4">
            <div class="col text-center">
              <h6>System Security Status:</h6>
              <span id="security-status" class="badge bg-success px-4 py-2" style="font-size: 1.1em;">Secured</span>
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
          const eventCountElement = document.getElementById('event-count');
          const defenseHeaderElement = document.getElementById('defense-header');
          const defenseStatusElement = document.getElementById('defense-status');

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
              labels: Array(30).fill(''),
              datasets: [
                {
                  label: 'Reported Water Level',
                  data: Array(30).fill(null),
                  borderColor: '#4dabf7',
                  tension: 0.2,
                  fill: true,
                  backgroundColor: 'rgba(77, 171, 247, 0.1)'
                },
                {
                  label: 'Actual Water Level',
                  data: Array(30).fill(null),
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
                console.log("API Response:", data);
                
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
                
                // SIMPLIFIED ATTACK BANNER HANDLING
                if (data.active_attack && typeof data.active_attack === 'string') {
                  const attackMessage = data.active_attack;
                  
                  // Extract display name and type (remove type tag if present)
                  let displayName = attackMessage;
                  let extractedType = "NORMAL";
                  
                  if (attackMessage.includes("[TYPE:")) {
                    const parts = attackMessage.split("[TYPE:");
                    displayName = parts[0].trim();
                    extractedType = parts[1].split("]")[0]; // Extract the type value
                    console.log("Extracted type:", extractedType);
                  }
                  
                  // Update attack name display
                  attackNameElement.innerText = displayName;
                  
                  // SIMPLIFIED DETECTION
                  // 1. Check message content for attack keywords
                  const hasAttackKeyword = 
                    attackMessage.toLowerCase().includes("replay") || 
                    attackMessage.toLowerCase().includes("false data") || 
                    attackMessage.toLowerCase().includes("dos");
                  
                  // 2. Check for defense keywords or type
                  const hasDefenseKeyword = 
                    attackMessage.toLowerCase().includes("defense") || 
                    attackMessage.toLowerCase().includes("with_defense") ||
                    extractedType === "DEFENSE";
                  
                  // 3. Check for explicit attack type
                  const hasAttackTag = extractedType === "ATTACK";
                  
                  // 4. Check significant discrepancy
                  const hasLargeDiscrepancy = Math.abs(newLevel - newActualLevel) > 5;
                  
                  // Handle UI update in order of priority
                  if (displayName.toLowerCase().includes("demonstration complete")) {
                    // Demo has completed
                    console.log("DEMO COMPLETE - SETTING COMPLETION BANNER");
                    
                    // Set completion message
                    attackNameElement.innerHTML = `🎉 Demonstration Complete!`;
                    countdownElement.innerHTML = "Demo has finished";
                    
                    // Apply blue completion style
                    currentAttackElement.className = 'normal-state';
                    currentAttackElement.style.backgroundColor = '#0d6efd !important';
                    currentAttackElement.style.borderColor = '#0d6efd !important';
                  }
                  else if (hasAttackKeyword || hasAttackTag || hasLargeDiscrepancy) {
                    // IT'S AN ATTACK - FORCE RED
                    console.log("ATTACK DETECTED - SETTING RED BANNER");
                    
                    // Set warning indicators
                    attackNameElement.innerHTML = `⚠️ ${displayName} ⚠️`;
                    
                    // Remove all classes and add attack state
                    currentAttackElement.className = 'attack-state';
                  }
                  else if (hasDefenseKeyword || extractedType === "DEFENSE") {
                    // It's a defense mode - yellow
                    console.log("DEFENSE MODE - SETTING YELLOW BANNER");
                    
                    // Set defense indicator
                    if (!displayName.includes("Defense")) {
                      attackNameElement.innerHTML = `🛡️ ${displayName} (Defense Active)`;
                    } else {
                      attackNameElement.innerHTML = `🛡️ ${displayName}`;
                    }
                    
                    currentAttackElement.className = 'defense-state';
                  } 
                  else {
                    // Normal operation - green
                    console.log("NORMAL MODE - SETTING GREEN BANNER");
                    currentAttackElement.className = 'normal-state';
                  }
                  
                  // Handle countdown
                  countdownValue = data.time_remaining || 15;
                  countdownElement.innerText = countdownValue;
                  
                  // Only setup countdown if not already running
                  if (data.timestamp_changed && !countdownInterval) {
                    countdownInterval = setInterval(() => {
                      countdownValue = Math.max(0, countdownValue - 1);
                      countdownElement.innerText = countdownValue;
                    }, 1000);
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
                // Check for defense mode
                const hasDefenseEvents = data.defense_events && data.defense_events.length > 0;
                const hasDefenseMode = data.active_attack && typeof data.active_attack === 'string' && 
                  (data.active_attack.includes('defense') || 
                   data.active_attack.includes('with_defense') || 
                   data.active_attack.includes('DEFENSE'));
                
                // Set defense header state - ACTIVE when either condition is true
                if (hasDefenseEvents || hasDefenseMode) {
                  // Set defense header to ACTIVE state
                  defenseHeaderElement.className = 'card-header bg-primary text-white d-flex justify-content-between';
                  defenseStatusElement.innerHTML = '<span class="badge bg-success ms-2">Active</span>';
                } else {
                  // Set defense header to INACTIVE state
                  defenseHeaderElement.className = 'card-header bg-secondary text-white d-flex justify-content-between';
                  defenseStatusElement.innerHTML = '<span class="badge bg-light text-dark ms-2">Inactive</span>';
                }
                
                if (hasDefenseEvents) {
                  // Check if there are new events to highlight
                  const hasNewEvents = data.new_events && data.new_events.length > 0;
                  
                  // Update the events count badge
                  eventCountElement.textContent = `${data.defense_events.length} events`;
                  
                  // Clear the table content
                  defenseEventsElement.innerHTML = '';
                  
                  // Add each defense event to the table
                  data.defense_events.forEach(event => {
                    const row = document.createElement('tr');
                    
                    // Check if this is a new event to highlight it
                    if (hasNewEvents && data.new_events.some(e => e.raw === event.raw)) {
                      row.className = 'defense-event-new';
                    }
                    
                    // Add icon based on event type
                    let icon = '<i class="bi bi-check-circle-fill text-primary"></i>';
                    if (event.type === 'Anomaly') {
                      icon = '<i class="bi bi-graph-up-arrow text-warning"></i>';
                    } else if (event.type === 'Authentication') {
                      icon = '<i class="bi bi-shield-check text-info"></i>';
                    }
                    
                    // Create the table cells
                    const timeCell = document.createElement('td');
                    timeCell.textContent = event.timestamp;
                    
                    const messageCell = document.createElement('td');
                    messageCell.innerHTML = event.message;
                    
                    const typeCell = document.createElement('td');
                    typeCell.innerHTML = `${icon} ${event.type}`;
                    
                    // Add cells to the row
                    row.appendChild(timeCell);
                    row.appendChild(messageCell);
                    row.appendChild(typeCell);
                    
                    // Add the row to the table
                    defenseEventsElement.appendChild(row);
                  });
                } else if (hasDefenseMode) {
                  // If in defense mode but no events yet
                  defenseEventsElement.innerHTML = '';
                  const row = document.createElement('tr');
                  const cell = document.createElement('td');
                  cell.colSpan = 3;
                  cell.className = 'text-center text-primary py-3';
                  cell.innerHTML = '<i class="bi bi-shield-check"></i> Defense systems active and monitoring...';
                  row.appendChild(cell);
                  defenseEventsElement.appendChild(row);
                  
                  eventCountElement.textContent = '0 events';
                } else {
                  // If no defense mode and no events
                  defenseEventsElement.innerHTML = '';
                  const row = document.createElement('tr');
                  const cell = document.createElement('td');
                  cell.colSpan = 3;
                  cell.className = 'text-center text-muted py-3';
                  cell.innerHTML = 'No defense events logged';
                  row.appendChild(cell);
                  defenseEventsElement.appendChild(row);
                  
                  eventCountElement.textContent = '0 events';
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
          setInterval(updateDashboard, 1000);  // Faster updates
        </script>
      </body>
    </html>
    """
    return render_template_string(html, level=water_level, actual_level=actual_water_level)


@app.route('/api/water-level')
def api_water_level():
    global history, actual_history, timestamps, last_active_attack, attack_change_time, defense_events
    
    # Get active attack and defense status from the console output
    active_attack = ""
    new_defense_events = []
    
    with open('data/simulation.log', 'r') as f:
        try:
            lines = f.readlines()
            
            # Look for the most recent attack demo message
            for line in reversed(lines[-50:]):
                if "DEMO" in line and "demonstrating" in line:
                    parts = line.split("demonstrating:")
                    if len(parts) > 1:
                        full_message = parts[1].strip()
                        
                        # Extract the attack type if present
                        attack_type = "NORMAL"  # Default type
                        if "[TYPE:" in full_message:
                            type_parts = full_message.split("[TYPE:")
                            attack_type = type_parts[1].split("]")[0]
                            # Remove the type tag from the display message
                            display_message = type_parts[0].strip()
                        elif "[ATTACK]" in full_message:
                            # Alternative attack tag format
                            attack_type = "ATTACK"
                            display_message = full_message.replace("[ATTACK]", "").strip()
                        else:
                            display_message = full_message
                            
                        # Detect attack names in the display message as a backup
                        if ("Replay" in display_message or 
                            "replay" in display_message or 
                            "False Data" in display_message or 
                            "false_data" in display_message or 
                            "DoS" in display_message or 
                            "dos" in display_message or
                            "Dos" in display_message):
                            print(f"Found attack name in display message: {display_message}")
                            attack_type = "ATTACK"
                        
                        # For debugging - print what we found
                        print(f"API found message: {display_message} with type: {attack_type}")
                        
                        # Only update if the attack is different or the current active_attack is empty
                        if display_message != last_active_attack or not active_attack:
                            # Format the attack string with consistent TYPE tag
                            active_attack = f"{display_message} [TYPE:{attack_type}]"
                            print(f"API returning active_attack: {active_attack}")
                    break
            
            # Look for any defense activations in all available lines
            for line in lines:
                # Only process actual defense events, not demo announcements
                if "[DEFENSE]" in line and "DEMO" not in line:
                    log_time = datetime.fromtimestamp(get_timestamp_from_log(line))
                    timestamp = log_time.strftime('%H:%M:%S')
                    
                    # Extract message and categorize it
                    event_text = line.strip()
                    if "[DEFENSE]" in event_text:
                        message = event_text.split("[DEFENSE]")[1].strip()
                    else:
                        message = event_text
                        
                    # Determine event type
                    event_type = "General"
                    if "Anomaly" in message:
                        event_type = "Anomaly"
                    elif "authentication" in message or "authentic" in message:
                        event_type = "Authentication"
                    
                    # Add to events if not already present
                    event = {
                        'timestamp': timestamp,
                        'message': message,
                        'type': event_type,
                        'raw': event_text
                    }
                    
                    # Check if this event is already in our list
                    if event_text not in [e['raw'] for e in defense_events]:
                        new_defense_events.append(event)
                        
        except Exception as e:
            print(f"Error parsing log: {e}")
    
    # Add new events to our global list
    defense_events.extend(new_defense_events)
    
    # Keep only the most recent MAX_DEFENSE_EVENTS
    if len(defense_events) > MAX_DEFENSE_EVENTS:
        defense_events = defense_events[-MAX_DEFENSE_EVENTS:]
    
    # Detect if attack has changed
    timestamp_changed = False
    if active_attack != last_active_attack and active_attack:
        timestamp_changed = True
        last_active_attack = active_attack
        attack_change_time = time.time()
    
    # Calculate time remaining until next attack
    time_elapsed = time.time() - attack_change_time
    time_remaining = max(0, 15 - int(time_elapsed))
    
    return jsonify({
        'level': water_level,
        'actual_level': actual_water_level,
        'history': history,
        'actual_history': actual_history,
        'timestamps': timestamps,
        'active_attack': active_attack,
        'timestamp_changed': timestamp_changed,
        'time_remaining': time_remaining,
        'defense_events': defense_events,
        'new_events': new_defense_events
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