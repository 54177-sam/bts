from flask import Blueprint, render_template, session, jsonify
from functools import lru_cache, wraps
import psutil
import time
import logging
from datetime import datetime, timedelta
import subprocess
import os

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

# Cache timeout configuration (seconds)
CACHE_TIMEOUT_SHORT = 5    # 5 seconds for system stats
CACHE_TIMEOUT_MEDIUM = 30  # 30 seconds for service status
CACHE_TIMEOUT_LONG = 300   # 5 minutes for device detection


def cache_with_timeout(timeout):
    """Decorator to cache function results with timeout."""
    def decorator(f):
        cache = {}
        cache_time = {}
        
        @wraps(f)
        def decorated(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            
            if key in cache and (now - cache_time[key]) < timeout:
                return cache[key]
            
            result = f(*args, **kwargs)
            cache[key] = result
            cache_time[key] = now
            return result
        
        return decorated
    return decorator


class SystemMonitor:
    """Optimized system monitoring with caching."""
    
    _last_stats = None
    _last_stats_time = 0
    
    @staticmethod
    @cache_with_timeout(CACHE_TIMEOUT_SHORT)
    def get_system_stats():
        """Get cached system statistics (5 second cache)."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count(logical=False) or 1
            
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
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
            logger.exception("Error getting system stats")
            return {
                'cpu': {'percent': 0, 'count_physical': 1, 'count_logical': 1},
                'memory': {'total': 0, 'used': 0, 'free': 0, 'percent': 0},
                'disk': {'total': 0, 'used': 0, 'free': 0, 'percent': 0},
                'network': {'bytes_sent': 0, 'bytes_recv': 0},
                'system': {'uptime': 'Unknown', 'users': 0, 'platform': 'Unknown'}
            }


class BTSMonitor:
    """Optimized BTS monitoring with caching."""
    
    BTS_PROCESSES = ['osmo-bts', 'osmo-trx', 'osmo-bsc', 'osmo-msc', 
                     'osmo-hlr', 'osmo-sgsn', 'osmo-ggsn', 'osmocon']
    
    @staticmethod
    @cache_with_timeout(CACHE_TIMEOUT_MEDIUM)
    def get_bts_status():
        """Get cached BTS status (30 second cache)."""
        try:
            running_processes = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info.get('name', '').lower()
                    if any(bts in proc_name for bts in BTSMonitor.BTS_PROCESSES):
                        running_processes.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            status = 'active' if len(running_processes) > 0 else 'inactive'
            
            return {
                'processes_running': running_processes,
                'total_processes': len(running_processes),
                'status': status,
                'last_check': datetime.now().strftime('%H:%M:%S')
            }
        except Exception:
            logger.exception("Error getting BTS status")
            return {
                'processes_running': [],
                'total_processes': 0,
                'status': 'error',
                'last_check': datetime.now().strftime('%H:%M:%S')
            }


class HackRFManager:
    """Optimized HackRF management with device detection caching."""
    
    _detection_cache = None
    _detection_cache_time = 0
    
    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
    
    @staticmethod
    @cache_with_timeout(CACHE_TIMEOUT_LONG)
    def get_detection_status():
        """Get cached HackRF detection status (5 minute cache)."""
        try:
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
                        'serial': 'SIM000000000000000000001'
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
        except Exception:
            logger.exception("Error detecting HackRF")
            return {
                'connected': False,
                'display_text': 'Error',
                'badge_type': 'danger',
                'description': 'Error detecting HackRF',
                'device_info': None,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
    
    def detect_hackrf(self):
        """Simulate HackRF detection."""
        return True


class ServiceManager:
    """Optimized service management with caching."""
    
    SERVICES = {
        'osmo_bts': {'name': 'OsmoBTS', 'description': 'GSM Base Transceiver Station', 'port': 4238},
        'osmo_bsc': {'name': 'OsmoBSC', 'description': 'GSM Base Station Controller', 'port': 4240},
        'osmo_msc': {'name': 'OsmoMSC', 'description': 'GSM Mobile Switching Center', 'port': 4242},
        'osmo_hlr': {'name': 'OsmoHLR', 'description': 'GSM Home Location Register', 'port': 4243},
        'osmo_sgsn': {'name': 'OsmoSGSN', 'description': 'GSM Serving GPRS Support Node', 'port': 4244},
        'osmo_ggsn': {'name': 'OsmoGGSN', 'description': 'GSM Gateway GPRS Support Node', 'port': 4245}
    }
    
    @staticmethod
    @cache_with_timeout(CACHE_TIMEOUT_MEDIUM)
    def get_all_services_status():
        """Get cached services status (30 second cache)."""
        try:
            services = {}
            default_status = {'status': 'stopped'}
            
            for key, service in ServiceManager.SERVICES.items():
                services[key] = {**service, **default_status}
            
            return services
        except Exception:
            logger.exception("Error getting services status")
            return {}


def calculate_health_score(services_running, hackrf_connected, memory_usage, cpu_usage):
    """Calculate overall system health score (0-100)."""
    try:
        service_score = (services_running / len(ServiceManager.SERVICES)) * 40
        hackrf_score = 20 if hackrf_connected else 0
        memory_score = max(0, 20 - (memory_usage / 5))
        cpu_score = max(0, 20 - (cpu_usage / 5))
        
        score = service_score + hackrf_score + memory_score + cpu_score
        return min(100, max(0, round(score)))
    except Exception:
        logger.exception("Error calculating health score")
        return 75

@dashboard_bp.route('/dashboard')
def dashboard():
    """Main dashboard endpoint with lazy loading."""
    try:
        system_monitor = SystemMonitor()
        bts_monitor = BTSMonitor()
        hackrf_manager = HackRFManager()
        service_manager = ServiceManager()
        
        system_stats = system_monitor.get_system_stats()
        bts_status = bts_monitor.get_bts_status()
        hackrf_status = hackrf_manager.get_detection_status()
        services_status = service_manager.get_all_services_status()
        
        # Lazy load database data
        from modules.database import get_subscribers_count, get_sms_history
        subscribers_count = get_subscribers_count()
        sms_history = get_sms_history(limit=50)
        
        services_running = sum(1 for s in services_status.values() if s.get('status') == 'running')
        recent_sms = len(sms_history)
        
        health_score = calculate_health_score(
            services_running,
            hackrf_status.get('connected', False),
            system_stats.get('memory', {}).get('percent', 0),
            system_stats.get('cpu', {}).get('percent', 0)
        )
        
        return render_template('dashboard.html',
                             services=services_status,
                             hackrf_status=hackrf_status,
                             subscribers_count=subscribers_count,
                             services_running=services_running,
                             system_stats=system_stats,
                             bts_status=bts_status,
                             recent_sms=recent_sms,
                             health_score=health_score,
                             company='SIBERINDO',
                             full_company='SIBERINDO Technology')
    except Exception as e:
        logger.exception("Error loading dashboard")
        return render_template('error.html', 
                             error_message=f"Error loading dashboard: {str(e)}",
                             company='SIBERINDO'), 500


@dashboard_bp.route('/api/dashboard/refresh')
def refresh_dashboard():
    """API endpoint for real-time dashboard updates."""
    try:
        system_stats = SystemMonitor.get_system_stats()
        bts_status = BTSMonitor.get_bts_status()
        hackrf_status = HackRFManager.get_detection_status()
        services_status = ServiceManager.get_all_services_status()
        
        from modules.database import get_subscribers_count
        subscribers_count = get_subscribers_count()
        services_running = sum(1 for s in services_status.values() if s.get('status') == 'running')
        
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
        logger.exception("Error refreshing dashboard")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }), 500


@dashboard_bp.route('/api/hackrf/detect')
def detect_hackrf():
    """API endpoint for HackRF detection."""
    try:
        hackrf_manager = HackRFManager()
        detected = hackrf_manager.detect_hackrf()
        status_info = hackrf_manager.get_detection_status()
        
        return jsonify({
            'success': True,
            'detected': detected,
            'hackrf_status': status_info
        })
    except Exception as e:
        logger.exception("Error detecting HackRF")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500