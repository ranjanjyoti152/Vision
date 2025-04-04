import cv2
import os
from datetime import datetime
import threading
from logger import logger
import time

class VideoRecorder:
    def __init__(self, storage_dir="./recordings"):
        self.storage_dir = storage_dir
        self.active_recordings = {}
        self.recording_threads = {}
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def _generate_filename(self, camera_id):
        """Generate filename based on current timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"camera_{camera_id}_{timestamp}.mp4"

    def _record_camera(self, camera_id, rtsp_url):
        """Recording function to run in separate thread"""
        try:
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                logger.error(f"Failed to open camera stream: {rtsp_url}")
                return

            # Get video properties
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))

            # Create video writer
            filename = self._generate_filename(camera_id)
            filepath = os.path.join(self.storage_dir, filename)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, fps, (frame_width, frame_height))

            logger.info(f"Started recording camera {camera_id} to {filepath}")

            while self.active_recordings.get(camera_id, False):
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Failed to read frame from camera {camera_id}")
                    break
                
                out.write(frame)

            # Cleanup
            cap.release()
            out.release()
            logger.info(f"Stopped recording camera {camera_id}")

        except Exception as e:
            logger.error(f"Error recording camera {camera_id}: {str(e)}")
        finally:
            self.active_recordings[camera_id] = False

    def start_recording(self, camera_id, rtsp_url):
        """Start recording a camera"""
        try:
            if camera_id in self.active_recordings and self.active_recordings[camera_id]:
                logger.warning(f"Camera {camera_id} is already recording")
                return False

            self.active_recordings[camera_id] = True
            thread = threading.Thread(
                target=self._record_camera,
                args=(camera_id, rtsp_url),
                daemon=True
            )
            self.recording_threads[camera_id] = thread
            thread.start()
            
            logger.info(f"Started recording thread for camera {camera_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start recording camera {camera_id}: {str(e)}")
            return False

    def stop_recording(self, camera_id):
        """Stop recording a camera"""
        try:
            if camera_id not in self.active_recordings or not self.active_recordings[camera_id]:
                logger.warning(f"Camera {camera_id} is not recording")
                return False

            self.active_recordings[camera_id] = False
            if camera_id in self.recording_threads:
                self.recording_threads[camera_id].join(timeout=5)
                del self.recording_threads[camera_id]
            
            logger.info(f"Stopped recording camera {camera_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop recording camera {camera_id}: {str(e)}")
            return False

    def get_recordings(self, camera_id=None, date=None):
        """Get list of recordings, optionally filtered by camera ID and date"""
        try:
            recordings = []
            for filename in os.listdir(self.storage_dir):
                if not filename.endswith('.mp4'):
                    continue

                # Parse filename to get camera ID and timestamp
                parts = filename.split('_')
                if len(parts) >= 3:
                    file_camera_id = parts[1]
                    timestamp = datetime.strptime('_'.join(parts[2:]).replace('.mp4', ''), 
                                               "%Y%m%d_%H%M%S")

                    # Apply filters
                    if camera_id and file_camera_id != str(camera_id):
                        continue
                    if date and timestamp.date() != date:
                        continue

                    recordings.append({
                        'filename': filename,
                        'camera_id': file_camera_id,
                        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        'filepath': os.path.join(self.storage_dir, filename)
                    })

            return sorted(recordings, key=lambda x: x['timestamp'], reverse=True)

        except Exception as e:
            logger.error(f"Error getting recordings list: {str(e)}")
            return []

    def cleanup_old_recordings(self, retention_days):
        """Delete recordings older than retention_days"""
        try:
            current_time = datetime.now()
            deleted_count = 0

            for filename in os.listdir(self.storage_dir):
                if not filename.endswith('.mp4'):
                    continue

                filepath = os.path.join(self.storage_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                age_days = (current_time - file_time).days

                if age_days > retention_days:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"Deleted old recording: {filename}")

            logger.info(f"Cleanup complete. Deleted {deleted_count} old recordings")
            return deleted_count

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return 0