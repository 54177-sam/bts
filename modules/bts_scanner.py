from flask import Blueprint, render_template, jsonify, request, Response
from modules.helpers import login_required
from functools import wraps
import logging
import csv
from io import StringIO
from datetime import datetime

logger = logging.getLogger(__name__)
scanner_bp = Blueprint('scanner', __name__)

# Cache timeout configuration
CACHE_TIMEOUT_SCAN = 10  # 10 seconds for scan results


def cache_with_timeout(timeout):
    """Decorator to cache function results with timeout."""
    def decorator(f):
        cache = {}
        cache_time = {}
        
        @wraps(f)
        def decorated(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            import time
            now = time.time()
            
            if key in cache and (now - cache_time[key]) < timeout:
                return cache[key]
            
            result = f(*args, **kwargs)
            cache[key] = result
            cache_time[key] = now
            return result
        
        return decorated
    return decorator


class OptimizedHackRFManager:
    """HackRF manager with caching for scanner operations."""
    
    _instance = None
    _scan_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @cache_with_timeout(CACHE_TIMEOUT_SCAN)
    def get_detection_status(self):
        """Get cached HackRF detection status."""
        from modules.hackrf_manager import HackRFManager
        return HackRFManager().get_detection_status()
    
    @cache_with_timeout(CACHE_TIMEOUT_SCAN)
    def get_available_bands(self):
        """Get available bands with caching."""
        return {
            'GSM900': {'min': 890, 'max': 915, 'channels': 50},
            'GSM1800': {'min': 1710, 'max': 1785, 'channels': 75},
            'GSM850': {'min': 824, 'max': 894, 'channels': 70},
            'GSM1900': {'min': 1850, 'max': 1910, 'channels': 60}
        }
    
    def get_scan_status(self):
        """Get current scan status."""
        from modules.hackrf_manager import HackRFManager
        return HackRFManager().get_scan_status()
    
    def get_scan_results(self):
        """Get scan results (no cache - always fresh)."""
        from modules.hackrf_manager import HackRFManager
        return HackRFManager().get_scan_results()
    
    @cache_with_timeout(CACHE_TIMEOUT_SCAN)
    def get_scan_stats(self):
        """Get scan statistics with caching."""
        from modules.hackrf_manager import HackRFManager
        return HackRFManager().get_scan_stats()
    
    def start_scan(self, band, sample_rate, gain):
        """Start a new scan."""
        from modules.hackrf_manager import HackRFManager
        return HackRFManager().start_scan(band, sample_rate, gain)
    
    def stop_scan(self):
        """Stop current scan."""
        from modules.hackrf_manager import HackRFManager
        return HackRFManager().stop_scan()

@scanner_bp.route('/bts_scanner')
@login_required
def bts_scanner():
    """BTS scanner view with lazy loading."""
    try:
        hackrf = OptimizedHackRFManager()
        
        hackrf_status = hackrf.get_detection_status()
        available_bands = hackrf.get_available_bands()
        scan_status = hackrf.get_scan_status()
        scan_results = hackrf.get_scan_results()
        scan_stats = hackrf.get_scan_stats()
        
        return render_template('bts_scanner.html', 
                             hackrf_status=hackrf_status,
                             available_bands=available_bands,
                             scan_status=scan_status,
                             scan_results=scan_results,
                             scan_stats=scan_stats,
                             company='SIBERINDO')
    except Exception as e:
        logger.exception("Error loading BTS scanner")
        return jsonify({'error': str(e)}), 500

@scanner_bp.route('/api/bts_scan/start', methods=['POST'])
@login_required
def start_bts_scan():
    """Start BTS scan with parameter validation."""
    try:
        hackrf = OptimizedHackRFManager()
        data = request.get_json() or {}
        
        band = data.get('band', 'GSM900')
        sample_rate = int(data.get('sample_rate', 2000000))
        gain = int(data.get('gain', 40))
        
        success, message = hackrf.start_scan(band, sample_rate, gain)
        
        return jsonify({
            'success': success,
            'message': message,
            'band': band,
            'sample_rate': sample_rate,
            'gain': gain
        })
    except Exception as e:
        logger.exception("Error starting BTS scan")
        return jsonify({'success': False, 'message': str(e)}), 500


@scanner_bp.route('/api/bts_scan/stop', methods=['POST'])
@login_required
def stop_bts_scan():
    """Stop BTS scan."""
    try:
        hackrf = OptimizedHackRFManager()
        success, message = hackrf.stop_scan()
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.exception("Error stopping BTS scan")
        return jsonify({'success': False, 'message': str(e)}), 500


@scanner_bp.route('/api/bts_scan/status', methods=['GET'])
@login_required
def get_bts_scan_status():
    """Get BTS scan status and results."""
    try:
        hackrf = OptimizedHackRFManager()
        
        scan_status = hackrf.get_scan_status()
        scan_results = hackrf.get_scan_results()
        
        return jsonify({
            'scan_status': scan_status,
            'scan_results': scan_results,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.exception("Error getting BTS scan status")
        return jsonify({'error': str(e)}), 500


@scanner_bp.route('/api/bts_scan/results', methods=['GET'])
@login_required
def get_bts_scan_results():
    """Get BTS scan results and statistics."""
    try:
        hackrf = OptimizedHackRFManager()
        
        results = hackrf.get_scan_results()
        stats = hackrf.get_scan_stats()
        
        return jsonify({
            'results': results,
            'stats': stats,
            'count': len(results) if results else 0,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.exception("Error getting BTS scan results")
        return jsonify({'error': str(e)}), 500


@scanner_bp.route('/api/bts_scan/bands', methods=['GET'])
@login_required
def get_available_bands():
    """Get available frequency bands."""
    try:
        hackrf = OptimizedHackRFManager()
        bands = hackrf.get_available_bands()
        
        return jsonify({
            'bands': bands,
            'count': len(bands),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.exception("Error getting available bands")
        return jsonify({'error': str(e)}), 500

@scanner_bp.route('/api/bts_scan/analyze', methods=['POST'])
@login_required
def analyze_bts_results():
    """Analyze BTS scan results with signal quality assessment."""
    try:
        hackrf = OptimizedHackRFManager()
        results = hackrf.get_scan_results()
        
        if not results:
            return jsonify({'success': False, 'message': 'No scan results to analyze'})
        
        # Extract signal values safely
        signals = [r.get('signal', -100) for r in results if isinstance(r, dict)]
        frequencies = [r.get('frequency', 0) for r in results if isinstance(r, dict)]
        
        if not signals or not frequencies:
            return jsonify({'success': False, 'message': 'Invalid scan results'})
        
        # Calculate analysis metrics
        analysis = {
            'total_towers': len(results),
            'bands_found': list(set([r.get('band', 'Unknown') for r in results if isinstance(r, dict)])),
            'strongest_signal': max(signals),
            'weakest_signal': min(signals),
            'average_signal': sum(signals) / len(signals),
            'frequency_range': {
                'min': min(frequencies),
                'max': max(frequencies)
            },
            'network_operators': list(set([f"{r.get('mcc', '000')}-{r.get('mnc', '00')}" 
                                          for r in results if isinstance(r, dict)]))
        }
        
        # Signal quality assessment
        excellent = sum(1 for s in signals if s >= -65)
        good = sum(1 for s in signals if -75 <= s < -65)
        fair = sum(1 for s in signals if -85 <= s < -75)
        poor = sum(1 for s in signals if s < -85)
        
        analysis['signal_quality'] = {
            'excellent': excellent,
            'good': good,
            'fair': fair,
            'poor': poor
        }
        
        # Recommendations
        recommendations = []
        if analysis['strongest_signal'] >= -65:
            recommendations.append("Excellent signal strength detected. Suitable for high-quality communications.")
        if poor > 0:
            recommendations.append(f"{poor} towers have poor signal. Consider antenna optimization.")
        if len(analysis['bands_found']) > 1:
            recommendations.append("Multiple frequency bands detected. Good network diversity.")
        
        analysis['recommendations'] = recommendations
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.exception("Error analyzing BTS results")
        return jsonify({'success': False, 'message': str(e)}), 500


@scanner_bp.route('/api/bts_scan/export', methods=['GET'])
@login_required
def export_scan_results():
    """Export BTS scan results as CSV."""
    try:
        hackrf = OptimizedHackRFManager()
        results = hackrf.get_scan_results()
        
        if not results:
            return jsonify({'success': False, 'message': 'No results to export'}), 400
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ARFCN', 'Channel', 'Frequency (MHz)', 'Signal (dBm)', 'Band', 
                        'MCC', 'MNC', 'LAC', 'Cell ID', 'Network', 'Timestamp'])
        
        # Write data rows
        for result in results:
            if isinstance(result, dict):
                writer.writerow([
                    result.get('arfcn', ''),
                    result.get('channel', ''),
                    result.get('frequency', ''),
                    result.get('signal', ''),
                    result.get('band', ''),
                    result.get('mcc', ''),
                    result.get('mnc', ''),
                    result.get('lac', ''),
                    result.get('cell_id', ''),
                    result.get('network', ''),
                    result.get('timestamp', '')
                ])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=siberindo_bts_scan.csv"}
        )
        
    except Exception as e:
        logger.exception("Error exporting scan results")
        return jsonify({'success': False, 'message': str(e)}), 500