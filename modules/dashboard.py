from flask import Blueprint, render_template, session, jsonify, request
import psutil
import time
import logging
from datetime import datetime, timedelta
import subprocess
import os
import json
import platform

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)

class AdvancedSystemMonitor:
    """Enhanced system monitoring with comprehensive metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics_history = {
            'cpu': [],
            'memory': [],
            'network': [],
            'disk': []
        }
    
    def get_comprehensive_system_stats(self):
        """Get comprehensive system statistics with enhanced metrics"""
        try:
            # CPU information with detailed metrics
            cpu_times = psutil.cpu_times_percent(interval=0.5)
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_freq = psutil.cpu_freq()
            
            # Memory information with swap
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information with IO stats
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network information with detailed stats
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            # System information
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # Temperature sensors (if available)
            try:
                temps = psutil.sensors_temperatures()
                cpu_temp = temps.get('coretemp', [{}])[0].current if temps.get('coretemp') else 'N/A'
            except:
                cpu_temp = 'N/A'
            
            # Load average
            try:
                load_1, load_5, load_15 = os.getloadavg()
            except:
                load_1, load_5, load_15 = 0.0, 0.0, 0.0
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count_physical': psutil.cpu_count(logical=False),
                    'count_logical': psutil.cpu_count(logical=True),
                    'frequency_current': round(cpu_freq.current, 2) if cpu_freq else 'N/A',
                    'frequency_max': round(cpu_freq.max, 2) if cpu_freq else 'N/A',
                    'user_time': round(cpu_times.user, 2),
                    'system_time': round(cpu_times.system, 2),
                    'idle_time': round(cpu_times.idle, 2),
                    'load_1min': round(load_1, 2),
                    'load_5min': round(load_5, 2),
                    'load_15min': round(load_15, 2),
                    'temperature': cpu_temp
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'free_gb': round(memory.free / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'percent': memory.percent,
                    'swap_total_gb': round(swap.total / (1024**3), 2),
                    'swap_used_gb': round(swap.used / (1024**3), 2),
                    'swap_percent': swap.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'percent': disk.percent,
                    'read_mb': round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
                    'write_mb': round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0
                },
                'network': {
                    'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2) if net_io else 0,
                    'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2) if net_io else 0,
                    'packets_sent': net_io.packets_sent if net_io else 0,
                    'packets_recv': net_io.packets_recv if net_io else 0,
                    'active_connections': net_connections
                },
                'system': {
                    'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'uptime': str(uptime).split('.')[0],
                    'users': len(psutil.users()),
                    'platform': platform.system(),
                    'platform_version': platform.version(),
                    'hostname': platform.node(),
                    'python_version': platform.python_version(),
                    'app_uptime': str(datetime.now() - self.start_time).split('.')[0]
                }
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return self.get_fallback_stats()

    def get_fallback_stats(self):
        """Provide fallback stats in case of errors"""
        return {
            'cpu': {'percent': 0, 'count_physical': 1, 'count_logical': 1},
            'memory': {'percent': 0, 'total_gb': 0, 'used_gb': 0},
            'disk': {'percent': 0, 'total_gb': 0, 'used_gb': 0},
            'network': {'bytes_sent_mb': 0, 'bytes_recv_mb': 0},
            'system': {'uptime': 'Unknown', 'users': 0, 'platform': 'Unknown'}
        }

class EnhancedBTSMonitor:
    """Enhanced BTS monitoring with process management"""
    
    def __init__(self):
        self.bts_processes = [
            'osmo-bts', 'osmo-trx', 'osmo-bsc', 'osmo-msc', 
            'osmo-hlr', 'osmo-sgsn', 'osmo-ggsn', 'osmocon',
            'python', 'flask', 'hackrf'
        ]
    
    def get_detailed_bts_status(self):
        """Get detailed BTS system status with process information"""
        try:
            running_processes = []
            total_memory_usage = 0
            total_cpu_usage = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'status', 'create_time']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    if any(bts_proc in proc_name for bts_proc in self.bts_processes):
                        process_info = {
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'memory_mb': round(proc.info['memory_info'].rss / 1024 / 1024, 1) if proc.info['memory_info'] else 0,
                            'cpu_percent': round(proc.info['cpu_percent'] or 0, 1),
                            'status': proc.info['status'],
                            'uptime': str(datetime.now() - datetime.fromtimestamp(proc.info['create_time'])).split('.')[0] if proc.info['create_time'] else 'Unknown'
                        }
                        running_processes.append(process_info)
                        total_memory_usage += process_info['memory_mb']
                        total_cpu_usage += process_info['cpu_percent']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Determine overall status
            if len(running_processes) >= 3:
                status = 'active'
                status_level = 'success'
            elif len(running_processes) >= 1:
                status = 'partial'
                status_level = 'warning'
            else:
                status = 'inactive'
                status_level = 'danger'
            
            return {
                'processes_running': running_processes,
                'total_processes': len(running_processes),
                'total_memory_usage_mb': round(total_memory_usage, 1),
                'total_cpu_usage': round(total_cpu_usage, 1),
                'status': status,
                'status_level': status_level,
                'last_check': datetime.now().strftime('%H:%M:%S'),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting BTS status: {e}")
            return {
                'processes_running': [],
                'total_processes': 0,
                'status': 'error',
                'status_level': 'danger',
                'last_check': datetime.now().strftime('%H:%M:%S')
            }

class AdvancedHackRFManager:
    """Advanced HackRF management with simulation and real modes"""
    
    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
        self.detection_history = []
    
    def get_enhanced_detection_status(self):
        """Get enhanced HackRF detection status with history"""
        try:
            if self.simulation_mode:
                status = self.get_simulation_status()
            else:
                status = self.get_real_hardware_status()
            
            # Add to history
            self.detection_history.append({
                'timestamp': datetime.now().isoformat(),
                'status': status['connected'],
                'mode': 'simulation' if self.simulation_mode else 'hardware'
            })
            
            # Keep only last 10 entries
            if len(self.detection_history) > 10:
                self.detection_history = self.detection_history[-10:]
            
            status['detection_history'] = self.detection_history
            return status
            
        except Exception as e:
            return self.get_error_status(str(e))
    
    def get_simulation_status(self):
        """Get simulation mode status with realistic data"""
        import random
        status_options = [
            {
                'connected': True,
                'display_text': 'Connected',
                'badge_type': 'success',
                'description': 'HackRF One is connected and ready for operation',
                'device_info': {
                    'board_id': 'HackRF One',
                    'firmware': '2024.01.1',
                    'serial': 'SIM' + ''.join(random.choices('0123456789ABCDEF', k=16)),
                    'part_id': '000' + ''.join(random.choices('0123456789ABCDEF', k=13)),
                    'version': f'git-{random.randint(1000, 9999):04x}',
                    'supported_sample_rates': ['2 MHz', '4 MHz', '8 MHz', '10 MHz', '16 MHz', '20 MHz'],
                    'frequency_range': '10 MHz - 6000 MHz'
                },
                'performance': {
                    'signal_strength': random.randint(-80, -30),
                    'noise_floor': random.randint(-120, -90),
                    'temperature': random.randint(25, 45)
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'connected': False,
                'display_text': 'Disconnected',
                'badge_type': 'danger',
                'description': 'HackRF One is not connected. Please check USB connection.',
                'device_info': None,
                'performance': None,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        return random.choice(status_options)
    
    def get_real_hardware_status(self):
        """Get real hardware status (placeholder for actual implementation)"""
        # This would implement actual HackRF detection
        return {
            'connected': False,
            'display_text': 'Hardware Mode Disabled',
            'badge_type': 'warning',
            'description': 'Real hardware detection is disabled in configuration',
            'device_info': None,
            'performance': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_error_status(self, error_message):
        """Get error status response"""
        return {
            'connected': False,
            'display_text': 'Error',
            'badge_type': 'danger',
            'description': f'Error detecting HackRF: {error_message}',
            'device_info': None,
            'performance': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def detect_hackrf(self):
        """Simulate HackRF detection"""
        if self.simulation_mode:
            return True, "HackRF detected in simulation mode"
        else:
            # Real detection would go here
            return False, "Real hardware detection not implemented"

# Database functions (enhanced)
def get_subscribers_count():
    """Enhanced subscriber count with simulation"""
    import random
    return random.randint(0, 100)

def get_sms_history():
    """Enhanced SMS history with simulation"""
    import random
    from datetime import datetime, timedelta
    
    sms_messages = []
    for i in range(random.randint(5, 20)):
        sms_messages.append({
            'id': i + 1,
            'imsi': f'00101{random.randint(1000000000, 9999999999)}',
            'message': f'Test message {i + 1}',
            'direction': random.choice(['in', 'out']),
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 1440))).strftime('%Y-%m-%d %H:%M:%S'),
            'status': random.choice(['delivered', 'sent', 'failed'])
        })
    return sms_messages

def calculate_advanced_health_score(services_running, hackrf_connected, memory_usage, cpu_usage, disk_usage):
    """Calculate advanced system health score (0-100) with multiple factors"""
    try:
        score = 0
        
        # Services component (30 points max)
        service_score = (services_running / 6) * 30
        
        # HackRF component (20 points max)
        hackrf_score = 20 if hackrf_connected else 0
        
        # Memory component (15 points max) - lower usage = higher score
        memory_score = max(0, 15 - (memory_usage / 6.67))
        
        # CPU component (15 points max) - lower usage = higher score
        cpu_score = max(0, 15 - (cpu_usage / 6.67))
        
        # Disk component (10 points max) - lower usage = higher score
        disk_score = max(0, 10 - (disk_usage / 10))
        
        # System load component (10 points max)
        load_score = 10  # Placeholder for load calculation
        
        score = service_score + hackrf_score + memory_score + cpu_score + disk_score + load_score
        return min(100, max(0, round(score)))
    except Exception as e:
        logger.error(f"Error calculating health score: {e}")
        return 75

# Login required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        # For development, always consider logged in
        session['logged_in'] = True
        session['username'] = 'admin'
        session['role'] = 'administrator'
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Initialize managers
system_monitor = AdvancedSystemMonitor()
bts_monitor = EnhancedBTSMonitor()
hackrf_manager = AdvancedHackRFManager(simulation_mode=True)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Enhanced main dashboard endpoint"""
    try:
        # Get service manager (simulated for now)
        from modules.service_manager import ServiceManager
        service_manager = ServiceManager()
        
        # Get all status information
        services_status = service_manager.get_all_services_status()
        hackrf_status = hackrf_manager.get_enhanced_detection_status()
        system_stats = system_monitor.get_comprehensive_system_stats()
        bts_status = bts_monitor.get_detailed_bts_status()
        
        # Get additional data
        subscribers_count = get_subscribers_count()
        sms_history = get_sms_history()
        
        # Calculate metrics
        services_running = sum(1 for s in services_status.values() if s.get('status') == 'running')
        recent_sms = len(sms_history)
        sms_today = len([sms for sms in sms_history 
                        if isinstance(sms, dict) and 
                        datetime.strptime(sms.get('timestamp', '2000-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S').date() == datetime.now().date()])
        
        # Calculate advanced health score
        health_score = calculate_advanced_health_score(
            services_running, 
            hackrf_status.get('connected', False),
            system_stats.get('memory', {}).get('percent', 0),
            system_stats.get('cpu', {}).get('percent', 0),
            system_stats.get('disk', {}).get('percent', 0)
        )
        
        # Prepare dashboard data
        dashboard_data = {
            'services': services_status,
            'hackrf_status': hackrf_status,
            'subscribers_count': subscribers_count,
            'services_running': services_running,
            'system_stats': system_stats,
            'bts_status': bts_status,
            'recent_sms': recent_sms,
            'sms_today': sms_today,
            'health_score': health_score,
            'company': 'SIBERINDO',
            'full_company': 'SIBERINDO Technology',
            'dashboard_version': '2.0.0',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('dashboard.html', **dashboard_data)
                             
    except Exception as e:
        error_msg = f"Error loading dashboard: {str(e)}"
        logger.error(error_msg)
        return render_template('error.html', 
                             error_message=error_msg,
                             company='SIBERINDO',
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@dashboard_bp.route('/api/dashboard/refresh')
@login_required
def refresh_dashboard():
    """Enhanced API endpoint for real-time dashboard updates"""
    try:
        from modules.service_manager import ServiceManager
        service_manager = ServiceManager()
        
        # Get updated status
        services_status = service_manager.get_all_services_status()
        hackrf_status = hackrf_manager.get_enhanced_detection_status()
        system_stats = system_monitor.get_comprehensive_system_stats()
        bts_status = bts_monitor.get_detailed_bts_status()
        
        subscribers_count = get_subscribers_count()
        services_running = sum(1 for s in services_status.values() if s.get('status') == 'running')
        
        # Calculate health score
        health_score = calculate_advanced_health_score(
            services_running,
            hackrf_status.get('connected', False),
            system_stats.get('memory', {}).get('percent', 0),
            system_stats.get('cpu', {}).get('percent', 0),
            system_stats.get('disk', {}).get('percent', 0)
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
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error refreshing dashboard: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }), 500

@dashboard_bp.route('/api/hackrf/detect', methods=['POST'])
@login_required
def detect_hackrf():
    """Enhanced API endpoint for manual HackRF detection"""
    try:
        # Force new detection
        detected, message = hackrf_manager.detect_hackrf()
        status_info = hackrf_manager.get_enhanced_detection_status()
        
        return jsonify({
            'success': True,
            'detected': detected,
            'message': message,
            'hackrf_status': status_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error detecting HackRF: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@dashboard_bp.route('/api/system/restart-service', methods=['POST'])
@login_required
def restart_service():
    """API endpoint to restart BTS services"""
    try:
        data = request.get_json()
        service_name = data.get('service_name')
        
        # Simulate service restart
        import time
        time.sleep(2)
        
        return jsonify({
            'success': True,
            'message': f'Service {service_name} restarted successfully',
            'service': service_name,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/system/shutdown', methods=['POST'])
@login_required
def system_shutdown():
    """API endpoint for system shutdown (simulated)"""
    try:
        # This would be a dangerous operation in production
        return jsonify({
            'success': True,
            'message': 'System shutdown command received (simulated)',
            'warning': 'This is a simulation. No actual shutdown performed.',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500