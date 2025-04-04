# Python Network Video Recorder (NVR) System

A modern, web-based Network Video Recorder system built with Flask and Tailwind CSS. This system provides a clean, iOS-inspired interface for managing IP cameras, recording footage, and monitoring system health.

## Features

- 📹 **Live Camera Dashboard**: View all connected cameras in real-time
- 🎥 **Video Recording**: Automatic recording with configurable storage settings
- ⏯️ **Playback**: Browse and view recorded footage with date/time filtering
- ⚙️ **Camera Management**: Easy addition and removal of RTSP camera streams
- 📊 **System Monitoring**: Real-time monitoring of CPU, memory, and disk usage
- 🎨 **Modern UI**: Clean, responsive interface with iOS-inspired design
- 📱 **Mobile-Friendly**: Fully responsive design that works on all devices

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Modern web browser
- RTSP-capable IP cameras

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-nvr-system.git
cd python-nvr-system
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create necessary directories:
```bash
mkdir -p recordings logs
```

4. Start the application:
```bash
python3 app.py
```

5. Access the web interface at `http://localhost:8000`

## Project Structure

```
.
├── app.py                 # Main Flask application
├── camera_manager.py      # Camera management module
├── recorder.py           # Video recording functionality
├── system_monitor.py     # System metrics monitoring
├── logger.py            # Application logging
├── config.json          # System configuration
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates
│   ├── base.html       # Base template with common elements
│   ├── dashboard.html  # Camera dashboard view
│   ├── playback.html   # Recording playback interface
│   ├── settings.html   # System settings page
│   └── health.html     # System health monitoring
├── recordings/         # Directory for stored recordings
└── logs/              # Application logs
```

## Usage

### Adding a Camera

1. Navigate to the Settings page
2. Enter the camera name and RTSP URL
3. Click "Add Camera"
4. The camera will appear on the dashboard

### Viewing Recordings

1. Go to the Playback page
2. Select the date and camera
3. Click on a recording to play
4. Use the video controls to navigate the footage

### System Health Monitoring

1. Visit the Health page
2. View real-time metrics for:
   - CPU usage
   - Memory utilization
   - Disk space
   - System uptime

## API Endpoints

- `GET /api/cameras`: List all configured cameras
- `POST /api/cameras`: Add a new camera
- `DELETE /api/cameras/<id>`: Remove a camera
- `GET /api/recordings`: List available recordings
- `GET /api/recordings/<filename>`: Serve a specific recording
- `GET /api/health/metrics`: Get system health metrics

## Configuration

The system configuration is stored in `config.json`:

```json
{
  "cameras": [],
  "recording_settings": {
    "storage_directory": "./recordings",
    "retention_days": 7
  }
}
```

## Development

The application uses:
- Flask for the backend
- Tailwind CSS for styling
- Chart.js for metrics visualization
- OpenCV for video handling

## Security Considerations

- This is a development server and should not be used in production without proper security measures
- RTSP streams should be properly secured with authentication
- Consider implementing user authentication for the web interface
- Use HTTPS in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask web framework
- Tailwind CSS for the UI
- Chart.js for metrics visualization
- OpenCV for video processing