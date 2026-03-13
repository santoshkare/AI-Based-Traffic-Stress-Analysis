/* Professional Drowsiness Detection Dashboard JavaScript */

// Backend API base URL
const baseURL = 'http://localhost:5000';

// ===== GLOBAL STATE =====
const state = {
    updateInterval: 500,
    statsUpdateInterval: null,
    sessionStartTime: Date.now(),
    alertQueue: [],
    maxAlerts: 10,
    thresholds: {
        drowsiness: 0.5,
        yawn: 0.5,
        blink: 100
    },
    settings: {
        enableAlerts: true,
        soundNotifications: true,
        videoQuality: 'medium'
    }
};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');

    setupTabNavigation();
    setupEventListeners();
    loadSettings();
    startStatsUpdate();
    setupVideoFeedListener();
    updateCameraStatus();

    console.log('Dashboard initialized successfully');
});

// ===== TAB NAVIGATION =====
function setupTabNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    // Set active nav item
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Load history when switching to history tab
    if (tabName === 'history') {
        loadHistory();
    }
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    // Camera control button
    document.getElementById('camera-btn').addEventListener('click', toggleCamera);

    // Reset button
    document.getElementById('reset-btn').addEventListener('click', resetSession);

    // Threshold sliders
    setupThresholdSliders();

    // Settings toggles
    setupSettingsToggles();

    // Update interval slider
    document.getElementById('update-interval').addEventListener('input', function() {
        state.updateInterval = parseInt(this.value);
        document.getElementById('update-interval-value').textContent = this.value;
        restartStatsUpdate();
    });
}

function setupThresholdSliders() {
    // Drowsiness threshold
    const drowsinessSlider = document.getElementById('drowsiness-threshold');
    drowsinessSlider.addEventListener('input', function() {
        state.thresholds.drowsiness = parseFloat(this.value);
        document.getElementById('drowsiness-threshold-value').textContent = this.value;
        updateThresholds();
    });

    // Yawn threshold
    const yawnSlider = document.getElementById('yawn-threshold');
    yawnSlider.addEventListener('input', function() {
        state.thresholds.yawn = parseFloat(this.value);
        document.getElementById('yawn-threshold-value').textContent = this.value;
        updateThresholds();
    });

    // Blink threshold
    const blinkSlider = document.getElementById('blink-threshold');
    blinkSlider.addEventListener('input', function() {
        state.thresholds.blink = parseInt(this.value);
        document.getElementById('blink-threshold-value').textContent = this.value;
        updateThresholds();
    });
}

function setupSettingsToggles() {
    document.getElementById('enable-alerts').addEventListener('change', function() {
        state.settings.enableAlerts = this.checked;
        saveSettings();
    });

    document.getElementById('sound-notifications').addEventListener('change', function() {
        state.settings.soundNotifications = this.checked;
        saveSettings();
    });

    document.getElementById('video-quality').addEventListener('change', function() {
        state.settings.videoQuality = this.value;
        saveSettings();
    });
}

// ===== THRESHOLD MANAGEMENT =====
function updateThresholds() {
    const data = {
        eye_threshold: state.thresholds.drowsiness,
        yawn_threshold: state.thresholds.yawn,
        consecutive_frames: state.thresholds.blink
    };

    fetch(`${baseURL}/api/config`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Thresholds updated:', data);
        addAlert('Settings updated', 'Thresholds have been applied successfully', 'info');
    })
    .catch(error => {
        console.error('Error updating thresholds:', error);
        addAlert('Error', 'Failed to update thresholds', 'warning');
    });
}

// ===== SETTINGS MANAGEMENT =====
function saveSettings() {
    const settings = {
        enable_alerts: state.settings.enableAlerts,
        sound_notifications: state.settings.soundNotifications,
        video_quality: state.settings.videoQuality,
        update_interval: state.updateInterval
    };

    localStorage.setItem('drowsiness_settings', JSON.stringify(settings));
}

function loadSettings() {
    const saved = localStorage.getItem('drowsiness_settings');
    if (saved) {
        try {
            const settings = JSON.parse(saved);
            state.settings = { ...state.settings, ...settings };

            // Update UI
            document.getElementById('enable-alerts').checked = state.settings.enableAlerts;
            document.getElementById('sound-notifications').checked = state.settings.soundNotifications;
            document.getElementById('video-quality').value = state.settings.videoQuality;
            document.getElementById('update-interval').value = state.updateInterval;
            document.getElementById('update-interval-value').textContent = state.updateInterval;
        } catch (e) {
            console.error('Error loading settings:', e);
        }
    }
}

// ===== STATS UPDATE =====
function startStatsUpdate() {
    // Update immediately
    updateStats();

    // Set interval
    state.statsUpdateInterval = setInterval(updateStats, state.updateInterval);
}

function restartStatsUpdate() {
    if (state.statsUpdateInterval) {
        clearInterval(state.statsUpdateInterval);
    }
    startStatsUpdate();
}

function updateStats() {
    fetch(`${baseURL}/api/stats`)
        .then(response => {
            if (!response.ok) throw new Error('API error');
            return response.json();
        })
        .then(data => {
            updateDashboardStats(data);
            updateStatusIndicator(data);
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
            updateStatusIndicator(null);
        });
}

function updateDashboardStats(data) {
    // Drowsiness level
    const drowsinessLevel = data.drowsiness_level || 0;
    const drowsinessPercent = Math.min(100, Math.round(drowsinessLevel * 100));
    document.getElementById('drowsiness-level').textContent = drowsinessPercent + '%';
    document.getElementById('drowsiness-bar').style.width = drowsinessPercent + '%';

    // Drowsiness status
    const drowsinessStatus = document.getElementById('drowsiness-status');
    if (drowsinessPercent < 30) {
        drowsinessStatus.textContent = 'Alert';
        drowsinessStatus.className = 'stat-status';
    } else if (drowsinessPercent < 70) {
        drowsinessStatus.textContent = 'Cautious';
        drowsinessStatus.className = 'stat-status warning';
    } else {
        drowsinessStatus.textContent = 'Drowsy';
        drowsinessStatus.className = 'stat-status danger';
    }

    // Yawn count
    document.getElementById('yawn-count').textContent = data.yawn_count || 0;

    // Blink rate
    document.getElementById('blink-rate').textContent = data.blink_rate || 0;

    // Eye closure duration
    const closureDuration = (data.max_closure_duration || 0).toFixed(1);
    document.getElementById('closure-duration').textContent = closureDuration + 's';

    // Accuracy
    const accuracy = Math.round((data.confidence || 0) * 100);
    document.getElementById('accuracy').textContent = accuracy + '%';

    // Session duration
    const sessionDuration = Math.floor((Date.now() - state.sessionStartTime) / 1000);
    document.getElementById('session-duration').textContent = formatTime(sessionDuration);

    // Head pose status
    const headPose = data.current?.head_pose || { pitch: 0, yaw: 0, roll: 0 };
    const lookingAway = data.current?.looking_away || false;
    const headPoseStatus = document.getElementById('head-pose-status');
    const headPoseDetails = document.getElementById('head-pose-details');
    const headPoseBar = document.getElementById('head-pose-bar');

    headPoseDetails.textContent = `Y:${headPose.yaw}° P:${headPose.pitch}° R:${headPose.roll}°`;

    if (lookingAway) {
        headPoseStatus.textContent = 'Looking Away';
        headPoseStatus.className = 'stat-status danger';
        headPoseBar.style.width = '100%';
        headPoseBar.className = 'stat-bar-fill head-pose danger';
    } else {
        const poseDeviation = (Math.abs(headPose.yaw) + Math.abs(headPose.pitch) + Math.abs(headPose.roll)) / 3;
        const posePercent = Math.min(100, (poseDeviation / 45) * 100);
        headPoseStatus.textContent = 'Centered';
        headPoseStatus.className = 'stat-status';
        headPoseBar.style.width = posePercent + '%';
        headPoseBar.className = 'stat-bar-fill head-pose';
    }

    // Risk score
    const riskScore = data.current?.risk_score || 0;
    const riskLevel = data.current?.risk_level || 'low';
    document.getElementById('risk-score').textContent = riskScore.toFixed(1);
    document.getElementById('risk-score-bar').style.width = Math.min(100, riskScore) + '%';

    const riskLevelElement = document.getElementById('risk-level');
    riskLevelElement.textContent = riskLevel.toUpperCase();

    // Update risk level styling
    const riskBar = document.getElementById('risk-score-bar');
    riskBar.className = 'stat-bar-fill risk-score';
    if (riskLevel === 'critical') {
        riskBar.classList.add('critical');
        riskLevelElement.className = 'stat-status critical';
    } else if (riskLevel === 'high') {
        riskBar.classList.add('danger');
        riskLevelElement.className = 'stat-status danger';
    } else if (riskLevel === 'medium') {
        riskBar.classList.add('warning');
        riskLevelElement.className = 'stat-status warning';
    } else {
        riskLevelElement.className = 'stat-status';
    }

    // Check for drowsiness alert
    if (drowsinessPercent > 70 && state.settings.enableAlerts) {
        if (data.drowsy_detected && !data.alert_shown) {
            triggerDrowsinessAlert();
        }
    }
}

function updateStatusIndicator(data) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.getElementById('status-text');
    const videoStatus = document.getElementById('video-status');

    if (!data) {
        statusDot.classList.remove('active');
        statusText.textContent = 'Disconnected';
        videoStatus.textContent = 'No Signal';
        return;
    }

    statusDot.classList.add('active');

    if (data.drowsy_detected) {
        statusText.textContent = 'Drowsiness Detected';
    } else if (data.yawn_detected) {
        statusText.textContent = 'Yawning Detected';
    } else {
        statusText.textContent = 'System Active';
    }

    videoStatus.textContent = 'Connected';
}

// ===== ALERT MANAGEMENT =====
function addAlert(title, message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');

    const alertItem = document.createElement('div');
    alertItem.className = `alert-item alert-${type}`;

    const iconMap = {
        'info': 'ℹ️',
        'warning': '⚠️',
        'danger': '🚨'
    };

    const timestamp = new Date().toLocaleTimeString();

    alertItem.innerHTML = `
        <div class="alert-icon">${iconMap[type] || '•'}</div>
        <div class="alert-content">
            <p class="alert-title">${title}</p>
            <p class="alert-message">${message}</p>
        </div>
        <span class="alert-time">${timestamp}</span>
    `;

    // Add to beginning
    alertsContainer.insertBefore(alertItem, alertsContainer.firstChild);

    // Remove oldest alert if exceeds max
    const alerts = alertsContainer.querySelectorAll('.alert-item');
    if (alerts.length > state.maxAlerts) {
        alerts[alerts.length - 1].remove();
    }

    // Auto-remove after 30 seconds
    setTimeout(() => {
        alertItem.style.opacity = '0';
        alertItem.style.transform = 'translateX(-20px)';
        setTimeout(() => alertItem.remove(), 300);
    }, 30000);
}

function triggerDrowsinessAlert() {
    if (state.settings.enableAlerts) {
        addAlert('Drowsiness Alert', 'High drowsiness detected. Please stay alert!', 'danger');

        if (state.settings.soundNotifications) {
            playAlertSound();
        }
    }
}

function playAlertSound() {
    // Create a simple beep using Web Audio API
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 1000;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (e) {
        console.log('Could not play alert sound:', e);
    }
}

// ===== VIDEO FEED HANDLING =====
function setupVideoFeedListener() {
    const videoFeed = document.getElementById('video-feed');

    videoFeed.addEventListener('load', function() {
        console.log('Video feed loaded');
        document.getElementById('video-status').textContent = 'Connected';
    });

    videoFeed.addEventListener('error', function() {
        console.error('Video feed error');
        document.getElementById('video-status').textContent = 'Error';
    });
}

// ===== CAMERA CONTROL =====
function toggleCamera() {
    const cameraBtn = document.getElementById('camera-btn');
    const isCurrentlyOn = cameraBtn.textContent.includes('Off');

    const action = isCurrentlyOn ? 'stop' : 'start';
    const newText = isCurrentlyOn ? 'Turn Camera On' : 'Turn Camera Off';
    const newClass = isCurrentlyOn ? 'btn-success' : 'btn-primary';

    // Update button immediately for responsive UI
    cameraBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
            <circle cx="12" cy="13" r="4"></circle>
        </svg>
        ${newText}
    `;
    cameraBtn.className = `btn ${newClass}`;

    fetch(`${baseURL}/api/camera`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            addAlert('Camera Control', data.message, 'success');
            updateCameraStatus();
        } else {
            // Revert button on error
            cameraBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                    <circle cx="12" cy="13" r="4"></circle>
                </svg>
                Turn Camera ${isCurrentlyOn ? 'Off' : 'On'}
            `;
            cameraBtn.className = `btn ${isCurrentlyOn ? 'btn-primary' : 'btn-success'}`;
            addAlert('Error', data.message, 'warning');
        }
    })
    .catch(error => {
        console.error('Error controlling camera:', error);
        // Revert button on error
        cameraBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                <circle cx="12" cy="13" r="4"></circle>
            </svg>
            Turn Camera ${isCurrentlyOn ? 'Off' : 'On'}
        `;
        cameraBtn.className = `btn ${isCurrentlyOn ? 'btn-primary' : 'btn-success'}`;
        addAlert('Error', 'Failed to control camera', 'warning');
    });
}

function updateCameraStatus() {
    fetch(`${baseURL}/api/camera`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'status' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const cameraBtn = document.getElementById('camera-btn');
            const isRunning = data.camera_running;
            const newText = isRunning ? 'Turn Camera Off' : 'Turn Camera On';
            const newClass = isRunning ? 'btn-primary' : 'btn-success';

            cameraBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                    <circle cx="12" cy="13" r="4"></circle>
                </svg>
                ${newText}
            `;
            cameraBtn.className = `btn ${newClass}`;
        }
    })
    .catch(error => {
        console.error('Error getting camera status:', error);
    });
}

// ===== SESSION CONTROL =====
function resetSession() {
    if (confirm('Are you sure you want to reset the session? This will clear all current session statistics.')) {
        fetch(`${baseURL}/api/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            state.sessionStartTime = Date.now();
            addAlert('Session Reset', 'Session statistics have been cleared', 'info');
            updateStats();
        })
        .catch(error => {
            console.error('Error resetting session:', error);
            addAlert('Error', 'Failed to reset session', 'warning');
        });
    }
}

// ===== HISTORY MANAGEMENT =====
function loadHistory() {
    // History not implemented in separated backend
    const data = { sessions: [] };
    renderHistory(data);
    updateHistoryStats(data);
}

function renderHistory(data) {
    const tbody = document.getElementById('history-tbody');

    if (!data.sessions || data.sessions.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="6">No sessions recorded yet</td></tr>';
        return;
    }

    tbody.innerHTML = '';

    data.sessions.forEach(session => {
        const summary = session.summary;
        const createdAt = new Date(session.created_at).toLocaleString();
        const duration = formatTime(Math.floor(summary.session_duration_seconds));
        const avgDrowsiness = Math.round((summary.avg_drowsiness_level || 0) * 100);
        const peakLevel = Math.round((summary.peak_drowsiness_level || 0) * 100);

        // Determine status
        let status = 'Good';
        let statusClass = '';
        if (avgDrowsiness > 70) {
            status = 'Alert';
            statusClass = 'danger';
        } else if (avgDrowsiness > 40) {
            status = 'Caution';
            statusClass = 'warning';
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${createdAt}</td>
            <td>${duration}</td>
            <td>${avgDrowsiness}%</td>
            <td>${summary.total_yawn_events || 0}</td>
            <td>${peakLevel}%</td>
            <td><span class="status-badge ${statusClass}">${status}</span></td>
        `;

        tbody.appendChild(row);
    });
}

function updateHistoryStats(data) {
    if (!data.sessions || data.sessions.length === 0) {
        document.getElementById('total-sessions').textContent = '0';
        document.getElementById('total-duration').textContent = '0h';
        document.getElementById('avg-drowsiness').textContent = '0%';
        document.getElementById('total-yawns').textContent = '0';
        return;
    }

    let totalSeconds = 0;
    let totalDrowsiness = 0;
    let totalYawns = 0;

    data.sessions.forEach(session => {
        const summary = session.summary;
        totalSeconds += summary.session_duration_seconds || 0;
        totalDrowsiness += summary.avg_drowsiness_level || 0;
        totalYawns += summary.total_yawn_events || 0;
    });

    const numSessions = data.sessions.length;
    const hours = Math.floor(totalSeconds / 3600);
    const avgDrowsiness = Math.round((totalDrowsiness / numSessions) * 100);

    document.getElementById('total-sessions').textContent = numSessions;
    document.getElementById('total-duration').textContent = hours + 'h';
    document.getElementById('avg-drowsiness').textContent = avgDrowsiness + '%';
    document.getElementById('total-yawns').textContent = totalYawns;
}

// ===== UTILITY FUNCTIONS =====
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// ===== CLEANUP =====
window.addEventListener('beforeunload', function() {
    if (state.statsUpdateInterval) {
        clearInterval(state.statsUpdateInterval);
    }
});

console.log('Dashboard script loaded successfully');
