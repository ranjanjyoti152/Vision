import cv2
from flask import Response
import threading
import time
from logger import logger

class StreamHandler:
    def __init__(self):
        self.active_streams = {}
        self.stream_locks = {}
        self.frames = {}

    def _capture_stream(self, camera_id, rtsp_url):
        """Continuously capture frames from RTSP stream"""
        retry_count = 0
        max_retries = 3
        
        while self.active_streams.get(camera_id, False):
            try:
                cap = cv2.VideoCapture(rtsp_url)
                if not cap.isOpened():
                    raise Exception("Failed to open RTSP stream")

                logger.info(f"Successfully connected to camera {camera_id}")
                retry_count = 0  # Reset retry count on successful connection
                
                while self.active_streams.get(camera_id, False):
                    ret, frame = cap.read()
                    if not ret:
                        raise Exception("Failed to read frame")

                    # Acquire lock before updating frame
                    with self.stream_locks[camera_id]:
                        _, jpeg = cv2.imencode('.jpg', frame)
                        self.frames[camera_id] = jpeg.tobytes()
                    
                    time.sleep(0.033)  # ~30 FPS

            except Exception as e:
                logger.error(f"Error capturing stream for camera {camera_id}: {str(e)}")
                retry_count += 1
                
                if retry_count >= max_retries:
                    logger.error(f"Max retries reached for camera {camera_id}, stopping stream")
                    self.active_streams[camera_id] = False
                    break
                
                logger.info(f"Retrying connection to camera {camera_id} in 5 seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(5)
            
            finally:
                if 'cap' in locals():
                    cap.release()

        logger.info(f"Stream capture stopped for camera {camera_id}")

    def start_stream(self, camera_id, rtsp_url):
        """Start capturing stream for a camera"""
        if camera_id in self.active_streams and self.active_streams[camera_id]:
            return

        self.active_streams[camera_id] = True
        self.stream_locks[camera_id] = threading.Lock()
        self.frames[camera_id] = None

        thread = threading.Thread(
            target=self._capture_stream,
            args=(camera_id, rtsp_url),
            daemon=True
        )
        thread.start()
        logger.info(f"Started stream capture for camera {camera_id}")

    def stop_stream(self, camera_id):
        """Stop capturing stream for a camera"""
        if camera_id in self.active_streams:
            self.active_streams[camera_id] = False
            if camera_id in self.frames:
                del self.frames[camera_id]
            if camera_id in self.stream_locks:
                del self.stream_locks[camera_id]
            logger.info(f"Stopped stream capture for camera {camera_id}")

    def get_frame(self, camera_id):
        """Get the latest frame for a camera"""
        if camera_id not in self.frames or not self.frames[camera_id]:
            return None
        
        with self.stream_locks[camera_id]:
            return self.frames[camera_id]

    def generate_mjpeg(self, camera_id):
        """Generate MJPEG stream"""
        while True:
            frame = self.get_frame(camera_id)
            if frame is None:
                time.sleep(0.1)
                continue

            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.033)  # ~30 FPS