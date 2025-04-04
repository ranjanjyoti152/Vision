import json
import os
from logger import logger

class CameraManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_file} not found")
            return {"cameras": [], "recording_settings": {"storage_directory": "./recordings", "retention_days": 7}}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file {self.config_file}")
            return {"cameras": [], "recording_settings": {"storage_directory": "./recordings", "retention_days": 7}}

    def _save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            raise

    def list_cameras(self):
        """Return list of all configured cameras"""
        return self.config.get('cameras', [])

    def add_camera(self, name, rtsp_url):
        """Add a new camera to the configuration"""
        try:
            camera = {
                'id': len(self.config['cameras']) + 1,
                'name': name,
                'rtsp_url': rtsp_url,
                'enabled': True
            }
            self.config['cameras'].append(camera)
            self._save_config()
            logger.info(f"Added new camera: {name}")
            return camera
        except Exception as e:
            logger.error(f"Failed to add camera: {str(e)}")
            raise

    def delete_camera(self, camera_id):
        """Delete a camera from the configuration"""
        try:
            self.config['cameras'] = [cam for cam in self.config['cameras'] if cam['id'] != camera_id]
            self._save_config()
            logger.info(f"Deleted camera with ID: {camera_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete camera: {str(e)}")
            raise

    def update_settings(self, storage_directory, retention_days):
        """Update recording settings"""
        try:
            self.config['recording_settings']['storage_directory'] = storage_directory
            self.config['recording_settings']['retention_days'] = retention_days
            self._save_config()
            logger.info("Updated recording settings")
            return True
        except Exception as e:
            logger.error(f"Failed to update settings: {str(e)}")
            raise

    def get_settings(self):
        """Get current recording settings"""
        return self.config.get('recording_settings', {
            'storage_directory': './recordings',
            'retention_days': 7
        })