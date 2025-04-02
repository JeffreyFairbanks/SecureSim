# secure-sim/scada_ui/dashboard.py
from flask import Flask, render_template_string, jsonify
import threading

app = Flask(__name__)


# Global variables to store both reported and actual water levels
water_level = 45.0  # Potentially spoofed/reported level (set to a different initial value)
actual_water_level = 75.0  # Actual water level (set to a different initial value)
history = [water_level] * 5  # Pre-populate with some initial data points
actual_history = [actual_water_level] * 5  # Pre-populate with some initial data points
MAX_HISTORY = 20


@app.route('/')
def dashboard():
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>SecureSim Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
          body {
            background-color: #f8f9fa;
          }
          .dashboard-container {
            max-width: 900px;
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
                <div class="card-header bg-primary text-white">
                  <h5 class="mb-0">Level History</h5>
                </div>
                <div class="card-body">
                  <canvas id="chart" height="220"></canvas>
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
                <div class="card-footer bg-light">
                  <div class="text-center">
                    <span class="text-danger fw-bold">Discrepancy:</span> 
                    <span id="level-discrepancy" class="text-dark fw-bold">0.0</span> units
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="row mt-4">
            <div class="col-md-12">
              <div class="card">
                <div class="card-header bg-primary text-white">
                  <h5 class="mb-0">System Status</h5>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6">
                      <div class="mb-3">
                        <h6>Flow Rate:</h6>
                        <div class="progress">
                          <div class="progress-bar" role="progressbar" style="width: 75%;">Normal</div>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="mb-3">
                        <h6>System Security:</h6>
                        <span class="badge bg-success">Secured</span>
                      </div>
                    </div>
                  </div>
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
          
          // Spoofed vs Actual elements
          const spoofedLevelElement = document.getElementById('spoofed-level-value');
          const actualLevelElement = document.getElementById('actual-level-value');
          const spoofedWaterElement = document.getElementById('spoofed-water-level');
          const actualWaterElement = document.getElementById('actual-water-level');
          const discrepancyElement = document.getElementById('level-discrepancy');

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
              labels: Array(20).fill(''),
              datasets: [
                {
                  label: 'Reported Water Level',
                  data: Array(20).fill(null),
                  borderColor: '#4dabf7',
                  tension: 0.2,
                  fill: true,
                  backgroundColor: 'rgba(77, 171, 247, 0.1)'
                },
                {
                  label: 'Actual Water Level',
                  data: Array(20).fill(null),
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
                  max: 100
                }
              },
              animation: {
                duration: 500
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
                levelElement.innerText = newLevel.toFixed(1);
                
                // Update spoofed vs actual display
                spoofedWaterElement.style.height = `${height}%`;
                actualWaterElement.style.height = `${actualHeight}%`;
                spoofedLevelElement.innerText = newLevel.toFixed(1);
                actualLevelElement.innerText = newActualLevel.toFixed(1);
                
                // Calculate and display discrepancy
                const discrepancy = Math.abs(newLevel - newActualLevel).toFixed(1);
                discrepancyElement.innerText = discrepancy;
                
                // If there's a significant discrepancy, highlight it
                if (discrepancy > 10) {
                  discrepancyElement.className = 'text-danger fw-bold';
                } else {
                  discrepancyElement.className = 'text-dark fw-bold';
                }

                // Update time
                updateTimeElement.innerText = new Date().toLocaleTimeString();

                // Update chart with both datasets
                chart.data.datasets[0].data = data.history;
                chart.data.datasets[1].data = data.actual_history;
                chart.update();
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
    global history, actual_history
    return jsonify({
        'level': water_level,
        'actual_level': actual_water_level,
        'history': history,
        'actual_history': actual_history
    })


def update_water_level(new_level, new_actual_level=None):
    global water_level, actual_water_level, history, actual_history
    water_level = new_level
    
    # If actual level is provided, update it (otherwise keep the spoofed value as actual too)
    if new_actual_level is not None:
        actual_water_level = new_actual_level
    else:
        actual_water_level = new_level

    # Add to history and maintain maximum size
    history.append(new_level)
    actual_history.append(actual_water_level)
    
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    if len(actual_history) > MAX_HISTORY:
        actual_history = actual_history[-MAX_HISTORY:]


def run_dashboard():
    app.run(debug=True, use_reloader=False)


def start_dashboard():
    thread = threading.Thread(target=run_dashboard)
    thread.daemon = True
    thread.start()
    return thread
