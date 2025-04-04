from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import os
from camera_manager import CameraManager
from system_monitor import SystemMonitor
from recorder import VideoRecorder
from logger import logger

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize components
camera_manager = CameraManager()
system_monitor = SystemMonitor()
video_recorder = VideoRecorder()

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Render dashboard with camera streams"""
    cameras = camera_manager.list_cameras()
    return render_template('dashboard.html', cameras=cameras)

@app.route('/playback')
def playback():
    """Render playback page"""
    cameras = camera_manager.list_cameras()
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        recordings = video_recorder.get_recordings(date=selected_date)
    except ValueError:
        recordings = []
    return render_template('playback.html', cameras=cameras, recordings=recordings, selected_date=date_str)

@app.route('/settings')
def settings():
    """Render settings page"""
    cameras = camera_manager.list_cameras()
    recording_settings = camera_manager.get_settings()
    return render_template('settings.html', cameras=cameras, settings=recording_settings)

@app.route('/health')
def health():
    """Render system health page"""
    return render_template('health.html')

# API Routes

@app.route('/api/cameras', methods=['GET'])
def list_cameras():
    """API endpoint to list all cameras"""
    return jsonify({"cameras": camera_manager.list_cameras()})

@app.route('/api/cameras', methods=['POST'])
def add_camera():
    """API endpoint to add a new camera"""
    try:
        data = request.get_json()
        name = data.get('name')
        rtsp_url = data.get('rtsp_url')
        
        if not name or not rtsp_url:
            return jsonify({"error": "Missing required fields"}), 400
        
        camera = camera_manager.add_camera(name, rtsp_url)
        return jsonify({"message": "Camera added successfully", "camera": camera}), 201
    except Exception as e:
        logger.error(f"Error adding camera: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cameras/<int:camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    """API endpoint to delete a camera"""
    try:
        video_recorder.stop_recording(camera_id)  # Stop recording if active
        camera_manager.delete_camera(camera_id)
        return jsonify({"message": "Camera deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting camera: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """API endpoint to update recording settings"""
    try:
        data = request.get_json()
        storage_dir = data.get('storage_directory')
        retention_days = int(data.get('retention_days', 7))
        
        camera_manager.update_settings(storage_dir, retention_days)
        return jsonify({"message": "Settings updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recordings/start/<int:camera_id>', methods=['POST'])
def start_recording(camera_id):
    """API endpoint to start recording a camera"""
    try:
        cameras = camera_manager.list_cameras()
        camera = next((c for c in cameras if c['id'] == camera_id), None)
        if not camera:
            return jsonify({"error": "Camera not found"}), 404
        
        if video_recorder.start_recording(camera_id, camera['rtsp_url']):
            return jsonify({"message": "Recording started"}), 200
        return jsonify({"error": "Failed to start recording"}), 500
    except Exception as e:
        logger.error(f"Error starting recording: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recordings/stop/<int:camera_id>', methods=['POST'])
def stop_recording(camera_id):
    """API endpoint to stop recording a camera"""
    try:
        if video_recorder.stop_recording(camera_id):
            return jsonify({"message": "Recording stopped"}), 200
        return jsonify({"error": "Failed to stop recording"}), 500
    except Exception as e:
        logger.error(f"Error stopping recording: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recordings', methods=['GET'])
def list_recordings():
    """API endpoint to list recordings"""
    try:
        camera_id = request.args.get('camera_id')
        date_str = request.args.get('date')
        
        date = None
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        recordings = video_recorder.get_recordings(
            camera_id=int(camera_id) if camera_id else None,
            date=date
        )
        return jsonify({"recordings": recordings})
    except Exception as e:
        logger.error(f"Error listing recordings: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recordings/<path:filename>')
def serve_recording(filename):
    """Serve a recorded video file"""
    try:
        return send_file(
            os.path.join(video_recorder.storage_dir, filename),
            mimetype='video/mp4'
        )
    except Exception as e:
        logger.error(f"Error serving recording: {str(e)}")
        return jsonify({"error": "Recording not found"}), 404

@app.route('/api/health/metrics')
def get_health_metrics():
    """API endpoint to get system health metrics"""
    try:
        metrics = system_monitor.get_all_metrics()
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting health metrics: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('recordings', exist_ok=True)
    
    # Start the application
    app.run(host='0.0.0.0', port=8000, debug=True)