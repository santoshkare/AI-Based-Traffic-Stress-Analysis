# Drowsiness Detection Frontend

This is the frontend interface for the Real-Time Drowsiness Detection System.

## Setup

1. Ensure the backend is running on http://localhost:5000

2. Open index.html in a web browser, or serve it with a static server:
   ```bash
   python -m http.server 8000
   ```
   Then open http://localhost:8000

## Features

- Live video feed from backend
- Real-time statistics
- Camera control
- Configuration settings
- Session management

## Backend Dependency

This frontend requires the backend API to be running. Update the `baseURL` in `static/script.js` if the backend is on a different URL.
