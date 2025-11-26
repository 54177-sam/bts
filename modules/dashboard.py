from flask import Blueprint, render_template, session, jsonify
from modules.helpers import login_required
import psutil
import time
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


def get_system_stats():
    """Get comprehensive system statistics"""
    try:
        # CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory information
        memory = psutil.virtual_memory()
        
        # Disk information
        disk = psutil.disk_usage('/')
        
        # Network information
        net_io = psutil.net_io_counters()
        
        # System uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'load_1min': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 'N/A'
            },
            'memory': {
                'total': round(memory.total / (1024**3), 2),  # GB
                'used': round(memory.used / (1024**3), 2),
                'free': round(memory.free / (1024**3), 2),
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
                'bytes_recv': net_io.bytes_recv if net_io else 0
            },
            'system': {
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                'uptime': str(uptime).split('.')[0],
                'users': len(psutil.users())
            }
        }
    except Exception as e:
        print(f"Error getting system stats: {e}")
        return {}

def get_bts_status():
    """Get BTS system status"""
    try:
        # Check if BTS-related processes are running
        bts_processes = ['osmo-bts-trx', 'osmo-trx', 'osmo-bsc', 'osmo-msc']
        running_processes = []
        
        for proc in psutil.process_iter(['name']):
            try:
                if any(bts_proc in proc.info['name'].lower() for bts_proc in bts_processes):
                    running_processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            'processes_running': running_processes,
            'total_processes': len(running_processes),
            'status': 'active' if len(running_processes) > 0 else 'inactive',
            'last_check': datetime.now().strftime('%H:%M:%S')
        }
    except Exception as e:
        print(f"Error getting BTS status: {e}")
        return {'processes_running': [], 'total_processes': 0, 'status': 'error'}

def calculate_health_score(services_running, hackrf_connected, memory_usage, cpu_usage):
    """Calculate overall system health score (0-100)"""
    score = 0
    
    # Services component (40 points max)
    service_score = (services_running / 6) * 40  # 6 total services
    
    # HackRF component (20 points max)
    hackrf_score = 20 if hackrf_connected else 0
    
    # Memory component (20 points max)
    memory_score = max(0, 20 - (memory_usage / 5))  # Lower usage = higher score
    
    # CPU component (20 points max)
    cpu_score = max(0, 20 - (cpu_usage / 5))  # Lower usage = higher score
    
    score = service_score + hackrf_score + memory_score + cpu_score
    return min(100, max(0, round(score)))

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        from modules.service_manager import ServiceManager
        from modules.hackrf_manager import HackRFManager
        from modules.database import get_subscribers_count, get_sms_history
        
        service_manager = ServiceManager()
        hackrf_manager = HackRFManager()
        
        # Get all status information
        services_status = service_manager.get_all_services_status()
        
        # FIX: Use try-except for get_hackrf_info to handle potential AttributeError
        try:
            hackrf_info = hackrf_manager.get_hackrf_info()
        except AttributeError:
            # Fallback to get_detection_status if get_hackrf_info doesn't exist
            hackrf_status = hackrf_manager.get_detection_status()
            hackrf_info = {
                'status': hackrf_status['display_text'],
                'board_id': hackrf_status['device_info'].get('board_id', 'N/A') if hackrf_status['device_info'] else 'N/A',
                'firmware': hackrf_status['device_info'].get('firmware', 'N/A') if hackrf_status['device_info'] else 'N/A',
                'serial': hackrf_status['device_info'].get('serial', 'N/A') if hackrf_status['device_info'] else 'N/A',
                'part_id': hackrf_status['device_info'].get('part_id', 'N/A') if hackrf_status['device_info'] else 'N/A',
                'version': hackrf_status['device_info'].get('version', 'N/A') if hackrf_status['device_info'] else 'N/A'
            }
        
        subscribers_count = get_subscribers_count()
        system_stats = get_system_stats()
        bts_status = get_bts_status()
        
        # Get SMS statistics
        sms_history = get_sms_history()
        recent_sms = len(sms_history)
        sms_today = len([sms for sms in sms_history 
                        if datetime.strptime(sms[6], '%Y-%m-%d %H:%M:%S').date() == datetime.now().date()])
        
        services_running = sum(1 for s in services_status.values() if s['status'] == 'running')
        
        # Calculate system health score
        health_score = calculate_health_score(
            services_running, 
            hackrf_info.get('status') == 'Connected',
            system_stats.get('memory', {}).get('percent', 0),
            system_stats.get('cpu', {}).get('percent', 0)
        )
        
        return render_template('dashboard.html',
                             services=services_status,
                             hackrf_info=hackrf_info,
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
        return f"Error loading dashboard: {e}", 500

@dashboard_bp.route('/api/dashboard/refresh')
@login_required
def refresh_dashboard():
    """API endpoint for real-time dashboard updates"""
    try:
        from modules.service_manager import ServiceManager
        from modules.hackrf_manager import HackRFManager
        from modules.database import get_subscribers_count
        
        service_manager = ServiceManager()
        hackrf_manager = HackRFManager()
        
        services_status = service_manager.get_all_services_status()
        
        # FIX: Same approach as main dashboard route
        try:
            hackrf_info = hackrf_manager.get_hackrf_info()
            hackrf_connected = hackrf_info.get('status') == 'Connected'
        except AttributeError:
            hackrf_status = hackrf_manager.get_detection_status()
            hackrf_info = {
                'status': hackrf_status['display_text'],
                'board_id': hackrf_status['device_info'].get('board_id', 'N/A') if hackrf_status['device_info'] else 'N/A',
                'firmware': hackrf_status['device_info'].get('firmware', 'N/A') if hackrf_status['device_info'] else 'N/A',
                'serial': hackrf_status['device_info'].get('serial', 'N/A') if hackrf_status['device_info'] else 'N/A',
                'part_id': hackrf_status['device_info'].get('part_id', 'N/A') if hackrf_status['device_info'] else 'N/A',
                'version': hackrf_status['device_info'].get('version', 'N/A') if hackrf_status['device_info'] else 'N/A'
            }
            hackrf_connected = hackrf_status['connected']
        
        subscribers_count = get_subscribers_count()
        system_stats = get_system_stats()
        bts_status = get_bts_status()
        
        services_running = sum(1 for s in services_status.values() if s['status'] == 'running')
        
        health_score = calculate_health_score(
            services_running, 
            hackrf_connected,
            system_stats.get('memory', {}).get('percent', 0),
            system_stats.get('cpu', {}).get('percent', 0)
        )
        
        return jsonify({
            'services': services_status,
            'hackrf_info': hackrf_info,
            'subscribers_count': subscribers_count,
            'services_running': services_running,
            'system_stats': system_stats,
            'bts_status': bts_status,
            'health_score': health_score,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/hackrf/detect')
@login_required
def detect_hackrf():
    """API endpoint for manual HackRF detection"""
    try:
        from modules.hackrf_manager import HackRFManager
        hackrf_manager = HackRFManager()
        
        # Force new detection
        detected = hackrf_manager.detect_hackrf()
        
        # FIX: Use try-except for get_hackrf_info
        try:
            status_info = hackrf_manager.get_hackrf_info()
        except AttributeError:
            status = hackrf_manager.get_detection_status()
            status_info = {
                'status': status['display_text'],
                'board_id': status['device_info'].get('board_id', 'N/A') if status['device_info'] else 'N/A',
                'firmware': status['device_info'].get('firmware', 'N/A') if status['device_info'] else 'N/A',
                'serial': status['device_info'].get('serial', 'N/A') if status['device_info'] else 'N/A',
                'part_id': status['device_info'].get('part_id', 'N/A') if status['device_info'] else 'N/A',
                'version': status['device_info'].get('version', 'N/A') if status['device_info'] else 'N/A'
            }
        
        return jsonify({
            'success': True,
            'detected': detected,
            'status': status_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500