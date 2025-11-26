import psutil
import subprocess
import time
import threading
from datetime import datetime
import os
import signal

class ServiceManager:
    """Enhanced service management with process control"""
    
    def __init__(self):
        self.services = {
            'osmo_bts': {
                'name': 'OsmoBTS',
                'description': 'GSM Base Transceiver Station',
                'port': 4238,
                'enabled': True,
                'process_name': 'osmo-bts-trx',
                'start_command': ['osmo-bts-trx', '-c', '/etc/osmocom/osmo-bts-trx.cfg'],
                'stop_command': ['pkill', '-f', 'osmo-bts-trx'],
                'config_file': '/etc/osmocom/osmo-bts-trx.cfg',
                'log_file': '/var/log/osmocom/osmo-bts-trx.log'
            },
            'osmo_bsc': {
                'name': 'OsmoBSC',
                'description': 'GSM Base Station Controller', 
                'port': 4240,
                'enabled': True,
                'process_name': 'osmo-bsc',
                'start_command': ['osmo-bsc', '-c', '/etc/osmocom/osmo-bsc.cfg'],
                'stop_command': ['pkill', '-f', 'osmo-bsc'],
                'config_file': '/etc/osmocom/osmo-bsc.cfg',
                'log_file': '/var/log/osmocom/osmo-bsc.log'
            },
            'osmo_msc': {
                'name': 'OsmoMSC',
                'description': 'GSM Mobile Switching Center',
                'port': 4242,
                'enabled': True,
                'process_name': 'osmo-msc',
                'start_command': ['osmo-msc', '-c', '/etc/osmocom/osmo-msc.cfg'],
                'stop_command': ['pkill', '-f', 'osmo-msc'],
                'config_file': '/etc/osmocom/osmo-msc.cfg',
                'log_file': '/var/log/osmocom/osmo-msc.log'
            },
            'osmo_hlr': {
                'name': 'OsmoHLR',
                'description': 'GSM Home Location Register',
                'port': 4243,
                'enabled': False,
                'process_name': 'osmo-hlr',
                'start_command': ['osmo-hlr', '-c', '/etc/osmocom/osmo-hlr.cfg'],
                'stop_command': ['pkill', '-f', 'osmo-hlr'],
                'config_file': '/etc/osmocom/osmo-hlr.cfg',
                'log_file': '/var/log/osmocom/osmo-hlr.log'
            },
            'osmo_sgsn': {
                'name': 'OsmoSGSN',
                'description': 'GSM Serving GPRS Support Node',
                'port': 4244,
                'enabled': False,
                'process_name': 'osmo-sgsn',
                'start_command': ['osmo-sgsn', '-c', '/etc/osmocom/osmo-sgsn.cfg'],
                'stop_command': ['pkill', '-f', 'osmo-sgsn'],
                'config_file': '/etc/osmocom/osmo-sgsn.cfg',
                'log_file': '/var/log/osmocom/osmo-sgsn.log'
            },
            'osmo_ggsn': {
                'name': 'OsmoGGSN',
                'description': 'GSM Gateway GPRS Support Node',
                'port': 4245,
                'enabled': False,
                'process_name': 'osmo-ggsn',
                'start_command': ['osmo-ggsn', '-c', '/etc/osmocom/osmo-ggsn.cfg'],
                'stop_command': ['pkill', '-f', 'osmo-ggsn'],
                'config_file': '/etc/osmocom/osmo-ggsn.cfg',
                'log_file': '/var/log/osmocom/osmo-ggsn.log'
            }
        }
        
        self.service_status_cache = {}
        self.last_update = datetime.now()

    def get_all_services_status(self):
        """Get comprehensive status of all BTS services"""
        # Update cache if stale (older than 5 seconds)
        if (datetime.now() - self.last_update).total_seconds() > 5:
            self._update_service_status_cache()
        
        return self.service_status_cache

    def _update_service_status_cache(self):
        """Update the service status cache"""
        for service_key, service in self.services.items():
            status_info = self._get_detailed_service_status(service)
            self.service_status_cache[service_key] = status_info
        
        self.last_update = datetime.now()

    def _get_detailed_service_status(self, service):
        """Get detailed status for a single service"""
        process_info = self._find_service_process(service['process_name'])
        
        status = 'stopped'
        pid = None
        cpu_percent = 0
        memory_mb = 0
        uptime = None
        
        if process_info:
            status = 'running'
            pid = process_info['pid']
            cpu_percent = process_info.get('cpu_percent', 0)
            memory_mb = process_info.get('memory_mb', 0)
            
            # Calculate uptime
            if process_info.get('create_time'):
                uptime_seconds = time.time() - process_info['create_time']
                uptime = self._format_uptime(uptime_seconds)
        
        # Check if port is listening
        port_status = self._check_port_status(service['port'])
        
        return {
            'name': service['name'],
            'description': service['description'],
            'port': service['port'],
            'status': status,
            'pid': pid,
            'cpu_percent': round(cpu_percent, 1),
            'memory_mb': round(memory_mb, 1),
            'uptime': uptime,
            'port_status': port_status,
            'enabled': service['enabled'],
            'last_checked': datetime.now().strftime('%H:%M:%S')
        }

    def _find_service_process(self, process_name):
        """Find process by name with detailed information"""
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'create_time']):
            try:
                if proc.info['name'] and process_name in proc.info['name'].lower():
                    return {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_mb': proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0,
                        'cpu_percent': proc.info['cpu_percent'] or 0,
                        'create_time': proc.info['create_time']
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                continue
        return None

    def _check_port_status(self, port):
        """Check if a port is listening"""
        try:
            # Use netstat to check if port is listening
            result = subprocess.run(
                ['netstat', '-tln'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if str(port) in result.stdout:
                return 'listening'
            else:
                return 'closed'
        except:
            return 'unknown'

    def _format_uptime(self, seconds):
        """Format uptime in human readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def start_service(self, service_name):
        """Start a BTS service"""
        service = self.services.get(service_name)
        if not service:
            return False, "Service not found"
        
        if not service['enabled']:
            return False, "Service is disabled"
        
        try:
            # Check if already running
            if self._find_service_process(service['process_name']):
                return True, f"Service {service['name']} is already running"
            
            # Start service (simulated for now)
            # In production, this would execute the actual start command
            result = subprocess.run(
                service['start_command'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Wait a bit for service to start
                time.sleep(2)
                
                # Verify service started
                if self._find_service_process(service['process_name']):
                    self._log_service_event(service_name, 'started', 'Service started successfully')
                    return True, f"Service {service['name']} started successfully"
                else:
                    return False, f"Service {service['name']} failed to start"
            else:
                return False, f"Failed to start service: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Service start timed out"
        except Exception as e:
            return False, f"Error starting service: {str(e)}"

    def stop_service(self, service_name):
        """Stop a BTS service"""
        service = self.services.get(service_name)
        if not service:
            return False, "Service not found"
        
        try:
            process_info = self._find_service_process(service['process_name'])
            if not process_info:
                return True, f"Service {service['name']} is not running"
            
            # Stop service (simulated for now)
            result = subprocess.run(
                service['stop_command'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Wait a bit for service to stop
            time.sleep(2)
            
            # Verify service stopped
            if not self._find_service_process(service['process_name']):
                self._log_service_event(service_name, 'stopped', 'Service stopped successfully')
                return True, f"Service {service['name']} stopped successfully"
            else:
                return False, f"Service {service['name']} failed to stop"
                
        except subprocess.TimeoutExpired:
            return False, "Service stop timed out"
        except Exception as e:
            return False, f"Error stopping service: {str(e)}"

    def restart_service(self, service_name):
        """Restart a BTS service"""
        success_stop, message_stop = self.stop_service(service_name)
        if success_stop:
            time.sleep(1)
            success_start, message_start = self.start_service(service_name)
            return success_start, message_start
        else:
            return False, message_stop

    def enable_service(self, service_name):
        """Enable a BTS service"""
        service = self.services.get(service_name)
        if service:
            service['enabled'] = True
            self._log_service_event(service_name, 'enabled', 'Service enabled')
            return True, f"Service {service['name']} enabled"
        return False, "Service not found"

    def disable_service(self, service_name):
        """Disable a BTS service"""
        service = self.services.get(service_name)
        if service:
            service['enabled'] = False
            self._log_service_event(service_name, 'disabled', 'Service disabled')
            return True, f"Service {service['name']} disabled"
        return False, "Service not found"

    def get_service_logs(self, service_name, lines=50):
        """Get service logs (simulated)"""
        service = self.services.get(service_name)
        if not service:
            return []
        
        # Simulated logs - in production, this would read actual log files
        logs = []
        for i in range(lines):
            logs.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'INFO',
                'message': f'Simulated log entry {i+1} for {service["name"]}'
            })
        
        return logs[-lines:]

    def _log_service_event(self, service_name, action, message):
        """Log service management events"""
        from modules.database import log_system_event
        log_system_event('SERVICE', action.upper(), f'{service_name}: {message}')

# Service Manager Blueprint
from flask import Blueprint
from modules.helpers import login_required

service_bp = Blueprint('service', __name__)

@service_bp.route('/services')
@login_required
def service_management():
    """Service management page"""
    service_manager = ServiceManager()
    services_status = service_manager.get_all_services_status()
    
    return render_template('services.html', 
                         services=services_status,
                         company='SIBERINDO')

@service_bp.route('/api/services/<service_name>/start', methods=['POST'])
@login_required
def api_start_service(service_name):
    """API endpoint to start a service"""
    service_manager = ServiceManager()
    success, message = service_manager.start_service(service_name)
    
    return jsonify({
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })

@service_bp.route('/api/services/<service_name>/stop', methods=['POST'])
@login_required
def api_stop_service(service_name):
    """API endpoint to stop a service"""
    service_manager = ServiceManager()
    success, message = service_manager.stop_service(service_name)
    
    return jsonify({
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })

@service_bp.route('/api/services/<service_name>/restart', methods=['POST'])
@login_required
def api_restart_service(service_name):
    """API endpoint to restart a service"""
    service_manager = ServiceManager()
    success, message = service_manager.restart_service(service_name)
    
    return jsonify({
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })

@service_bp.route('/api/services/<service_name>/logs')
@login_required
def api_get_service_logs(service_name):
    """API endpoint to get service logs"""
    service_manager = ServiceManager()
    lines = request.args.get('lines', 50, type=int)
    logs = service_manager.get_service_logs(service_name, lines)
    
    return jsonify({
        'success': True,
        'logs': logs,
        'service': service_name
    })