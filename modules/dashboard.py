from flask import Blueprint, render_template, session, jsonify
import psutil
import time
from datetime import datetime, timedelta
import subprocess
import os

dashboard_bp = Blueprint('dashboard', __name__)

# Simple login_required decorator for development
def login_required(f):
    def decorated_function(*args, **kwargs):
        # For development, always consider logged in
        session['logged_in'] = True
        session['username'] = 'admin'
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

class SystemMonitor:
    """Enhanced system monitoring class"""
    
    @staticmethod
    def get_system_stats():
        """Get comprehensive system statistics with error handling"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count(logical=False) or 1
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Network information
            net_io = psutil.net_io_counters()
            
            # System uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # Load average (Unix-like systems)
            try:
                load_1, load_5, load_15 = os.getloadavg()
            except:
                load_1, load_5, load_15 = 0.0, 0.0, 0.0
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count_physical': cpu_count,
                    'count_logical': psutil.cpu_count(logical=True),
                    'load_1min': round(load_1, 2),
                    'load_5min': round(load_5, 2),
                    'load_15min': round(load_15, 2)
                },
                'memory': {
                    'total': round(memory.total / (1024**3), 2),
                    'used': round(memory.used / (1024**3), 2),
                    'free': round(memory.free / (1024**3), 2),
                    'available': round(memory.available / (1024**3), 2),
                    'percent': memory.percent
                },
                'disk': {
                    'total': round(disk.total / (1024**3), 2),
                    'used': round(disk.used / (1024**3), 2),
                    'free': round(disk.free / (1024**3), 2),
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent if net_io else 0,
                    'bytes_recv': net_io.bytes_recv if net_io else 0,
                    'packets_sent': net_io.packets_sent if net_io else 0,
                    'packets_recv': net_io.packets_recv if net_io else 0
                },
                'system': {
                    'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'uptime': str(uptime).split('.')[0],
                    'users': len(psutil.users()),
                    'platform': os.uname().sysname if hasattr(os, 'uname') else 'Unknown'
                }
            }
        except Exception as e:
            print(f"Error getting system stats: {e}")
            # Return default values
            return {
                'cpu': {'percent': 0, 'count_physical': 1, 'count_logical': 1, 'load_1min': 0},
                'memory': {'total': 0, 'used': 0, 'free': 0, 'percent': 0},
                'disk': {'total': 0, 'used': 0, 'free': 0, 'percent': 0},
                'network': {'bytes_sent': 0, 'bytes_recv': 0},
                'system': {'uptime': 'Unknown', 'users': 0, 'platform': 'Unknown'}
            }

class BTSMonitor:
    """BTS-specific monitoring"""
    
    @staticmethod
    def get_bts_status():
        """Get BTS system status with process detection"""
        try:
            # Common BTS/GSM processes to check
            bts_processes = [
                'osmo-bts', 'osmo-trx', 'osmo-bsc', 'osmo-msc', 
                'osmo-hlr', 'osmo-sgsn', 'osmo-ggsn', 'osmocon',
                'python', 'flask'  # Add our own processes
            ]
            running_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    if any(bts_proc in proc_name for bts_proc in bts_processes):
                        running_processes.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'memory': round(proc.info['memory_info'].rss / 1024 / 1024, 1) if proc.info['memory_info'] else 0,
                            'cpu': proc.info['cpu_percent'] or 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                    continue
            
            status = 'active' if len(running_processes) > 2 else 'inactive'  # At least 2 BTS processes
            
            return {
                'processes_running': running_processes,
                'total_processes': len(running_processes),
                'status': status,
                'last_check': datetime.now().strftime('%H:%M:%S')
            }
        except Exception as e:
            print(f"Error getting BTS status: {e}")
            return {
                'processes_running': [],
                'total_processes': 0, 
                'status': 'error',
                'last_check': datetime.now().strftime('%H:%M:%S')
            }

class HackRFManager:
    """Enhanced HackRF management with simulation mode"""
    
    def __init__(self):
        self.simulation_mode = True  # Default to simulation for development
    
    def get_detection_status(self):
        """Get HackRF detection status with simulation"""
        try:
            if self.simulation_mode:
                # Simulation mode - random status for development
                import random
                status_options = [
                    {
                        'connected': True,
                        'display_text': 'Connected',
                        'badge_type': 'success',
                        'description': 'HackRF One is connected and ready',
                        'device_info': {
                            'board_id': 'HackRF One',
                            'firmware': '2024.01.1',
                            'serial': 'SIM000000000000000000001',
                            'part_id': '0000000000000000',
                            'version': 'git-1a2b3c4'
                        },
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    },
                    {
                        'connected': False, 
                        'display_text': 'Disconnected',
                        'badge_type': 'danger',
                        'description': 'HackRF One is not connected',
                        'device_info': None,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }
                ]
                return random.choice(status_options)
            else:
                # Real detection would go here
                return {
                    'connected': False,
                    'display_text': 'Real mode disabled',
                    'badge_type': 'warning',
                    'description': 'Real HackRF detection is disabled in simulation mode',
                    'device_info': None,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
        except Exception as e:
            return {
                'connected': False,
                'display_text': 'Error',
                'badge_type': 'danger',
                'description': f'Error detecting HackRF: {str(e)}',
                'device_info': None,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
    
    def detect_hackrf(self):
        """Simulate HackRF detection"""
        return True  # Always success in simulation

class ServiceManager:
    """Service management with simulation"""
    
    def get_all_services_status(self):
        """Get status of all BTS services"""
        try:
            # Simulated services status
            services = {
                'osmo_bts': {
                    'name': 'OsmoBTS',
                    'description': 'GSM Base Transceiver Station',
                    'port': 4238,
                    'status': 'running'
                },
                'osmo_bsc': {
                    'name': 'OsmoBSC', 
                    'description': 'GSM Base Station Controller',
                    'port': 4240,
                    'status': 'running'
                },
                'osmo_msc': {
                    'name': 'OsmoMSC',
                    'description': 'GSM Mobile Switching Center', 
                    'port': 4242,
                    'status': 'running'
                },
                'osmo_hlr': {
                    'name': 'OsmoHLR',
                    'description': 'GSM Home Location Register',
                    'port': 4243,
                    'status': 'stopped'
                },
                'osmo_sgsn': {
                    'name': 'OsmoSGSN',
                    'description': 'GSM Serving GPRS Support Node',
                    'port': 4244, 
                    'status': 'stopped'
                },
                'osmo_ggsn': {
                    'name': 'OsmoGGSN',
                    'description': 'GSM Gateway GPRS Support Node',
                    'port': 4245,
                    'status': 'stopped'
                }
            }
            return services
        except Exception as e:
            print(f"Error getting services status: {e}")
            return {}

# Database simulation functions
def get_subscribers_count():
    """Simulate getting subscribers count"""
    return 42  # Mock data

def get_sms_history():
    """Simulate getting SMS history"""
    return []  # Mock data

def calculate_health_score(services_running, hackrf_connected, memory_usage, cpu_usage):
    """Calculate overall system health score (0-100)"""
    try:
        score = 0
        
        # Services component (40 points max)
        service_score = (services_running / 6) * 40  # 6 total services
        
        # HackRF component (20 points max)
        hackrf_score = 20 if hackrf_connected else 0
        
        # Memory component (20 points max) - lower usage = higher score
        memory_score = max(0, 20 - (memory_usage / 5))
        
        # CPU component (20 points max) - lower usage = higher score  
        cpu_score = max(0, 20 - (cpu_usage / 5))
        
        score = service_score + hackrf_score + memory_score + cpu_score
        return min(100, max(0, round(score)))
    except Exception as e:
        print(f"Error calculating health score: {e}")
        return 75  # Default score

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard endpoint"""
    try:
        # Initialize managers
        service_manager = ServiceManager()
        hackrf_manager = HackRFManager()
        system_monitor = SystemMonitor()
        bts_monitor = BTSMonitor()
        
        # Get all status information
        services_status = service_manager.get_all_services_status()
        hackrf_status = hackrf_manager.get_detection_status()
        system_stats = system_monitor.get_system_stats()
        bts_status = bts_monitor.get_bts_status()
        
        # Get additional data
        subscribers_count = get_subscribers_count()
        sms_history = get_sms_history()
        
        # Calculate metrics
        services_running = sum(1 for s in services_status.values() if s.get('status') == 'running')
        recent_sms = len(sms_history)
        sms_today = len([sms for sms in sms_history 
                        if isinstance(sms, dict) and 
                        datetime.strptime(sms.get('timestamp', '2000-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S').date() == datetime.now().date()])
        
        # Calculate system health score
        health_score = calculate_health_score(
            services_running, 
            hackrf_status.get('connected', False),
            system_stats.get('memory', {}).get('percent', 0),
            system_stats.get('cpu', {}).get('percent', 0)
        )
        
        return render_template('dashboard.html',
                             services=services_status,
                             hackrf_status=hackrf_status,  # Fixed: using hackrf_status consistently
                             subscribers_count=subscribers_count,
                             services_running=services_running,
                             system_stats=system_stats,
                             bts_status=bts_status,
                             recent_sms=recent_sms,
                             sms_today=sms_today,
                             health_score=health_score,
                             company='SIBERINDO',
                             full_company='SIBERINDO Technology')
                             
    except Exception as e:
        error_msg = f"Error loading dashboard: {str(e)}"
        print(error_msg)
        return render_template('error.html', 
                             error_message=error_msg,
                             company='SIBERINDO')

@dashboard_bp.route('/api/dashboard/refresh')
@login_required
def refresh_dashboard():
    """API endpoint for real-time dashboard updates"""
    try:
        service_manager = ServiceManager()
        hackrf_manager = HackRFManager() 
        system_monitor = SystemMonitor()
        bts_monitor = BTSMonitor()
        
        # Get updated status
        services_status = service_manager.get_all_services_status()
        hackrf_status = hackrf_manager.get_detection_status()
        system_stats = system_monitor.get_system_stats()
        bts_status = bts_monitor.get_bts_status()
        
        subscribers_count = get_subscribers_count()
        services_running = sum(1 for s in services_status.values() if s.get('status') == 'running')
        
        # Calculate health score
        health_score = calculate_health_score(
            services_running,
            hackrf_status.get('connected', False),
            system_stats.get('memory', {}).get('percent', 0),
            system_stats.get('cpu', {}).get('percent', 0)
        )
        
        return jsonify({
            'success': True,
            'services': services_status,
            'hackrf_status': hackrf_status,
            'subscribers_count': subscribers_count,
            'services_running': services_running,
            'system_stats': system_stats,
            'bts_status': bts_status,
            'health_score': health_score,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }), 500

@dashboard_bp.route('/api/hackrf/detect')
@login_required
def detect_hackrf():
    """API endpoint for manual HackRF detection"""
    try:
        hackrf_manager = HackRFManager()
        
        # Force new detection
        detected = hackrf_manager.detect_hackrf()
        status_info = hackrf_manager.get_detection_status()
        
        return jsonify({
            'success': True,
            'detected': detected,
            'hackrf_status': status_info
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500