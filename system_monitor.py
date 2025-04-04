import psutil
import os
from datetime import datetime
from logger import logger

class SystemMonitor:
    @staticmethod
    def get_cpu_usage():
        """Get CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logger.error(f"Error getting CPU usage: {str(e)}")
            return 0

    @staticmethod
    def get_memory_usage():
        """Get memory usage statistics"""
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {str(e)}")
            return {}

    @staticmethod
    def get_disk_usage(path="./recordings"):
        """Get disk usage statistics for recordings directory"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            disk = psutil.disk_usage(path)
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        except Exception as e:
            logger.error(f"Error getting disk usage: {str(e)}")
            return {}

    @staticmethod
    def get_system_uptime():
        """Get system uptime"""
        try:
            return datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.error(f"Error getting system uptime: {str(e)}")
            return None

    @staticmethod
    def get_all_metrics():
        """Get all system metrics"""
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cpu': SystemMonitor.get_cpu_usage(),
            'memory': SystemMonitor.get_memory_usage(),
            'disk': SystemMonitor.get_disk_usage(),
            'uptime': SystemMonitor.get_system_uptime()
        }

    @staticmethod
    def format_bytes(bytes_value):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} PB"