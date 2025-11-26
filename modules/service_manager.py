import psutil
import subprocess
import time
import logging

logger = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self):
        self.services = {
            'siberindo-bts-trx': {
                'name': 'SIBERINDO-bts-trx',
                'description': 'BTS Transceiver Service',
                'status': 'stopped',
                'port': 4242
            },
            'siberindo-stp': {
                'name': 'SIBERINDO-stp', 
                'description': 'Signal Transfer Point',
                'status': 'stopped',
                'port': 4244
            },
            'siberindo-bsc': {
                'name': 'SIBERINDO-bsc',
                'description': 'Base Station Controller',
                'status': 'stopped', 
                'port': 4241
            },
            'siberindo-trhx': {
                'name': 'SIBERINDO-THSC',
                'description': 'Transceiver Handler',
                'status': 'stopped',
                'port': 4246
            },
            'siberindo-mgw': {
                'name': 'SIBERINDO-mgw',
                'description': 'Media Gateway',
                'status': 'stopped',
                'port': 4243
            },
            'siberindo-hlr': {
                'name': 'SIBERINDO-hlr',
                'description': 'Home Location Register',
                'status': 'stopped',
                'port': 4258
            }
        }
    
    def check_service_status(self, service_name):
        try:
            # For demo purposes, always return stopped
            # In real implementation, this would check actual services
            return "stopped"
        except Exception as e:
            print(f"Error checking service {service_name}: {e}")
            return "stopped"
    
    def get_all_services_status(self):
        for service_key in self.services:
            self.services[service_key]['status'] = self.check_service_status(service_key)
        return self.services
    
    def start_service(self, service_name):
        try:
            if service_name in self.services:
                print(f"Starting SIBERINDO service: {service_name}")
                time.sleep(2)
                return True
            return False
        except Exception as e:
            print(f"Error starting SIBERINDO service {service_name}: {e}")
            return False
    
    def stop_service(self, service_name):
        try:
            if service_name in self.services:
                print(f"Stopping SIBERINDO service: {service_name}")
                time.sleep(2)
                return True
            return False
        except Exception as e:
            print(f"Error stopping SIBERINDO service {service_name}: {e}")
            return False