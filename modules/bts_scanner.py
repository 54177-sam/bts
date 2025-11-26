from flask import Blueprint, render_template, session, jsonify, request
from modules.helpers import login_required
import json
from datetime import datetime

scanner_bp = Blueprint('scanner', __name__)

 

@scanner_bp.route('/bts_scanner')
@login_required
def bts_scanner():
    try:
        from modules.hackrf_manager import HackRFManager
        hackrf_manager = HackRFManager()
        
        hackrf_status = hackrf_manager.get_detection_status()
        available_bands = hackrf_manager.get_available_bands()
        scan_status = hackrf_manager.get_scan_status()
        scan_results = hackrf_manager.get_scan_results()
        scan_stats = hackrf_manager.get_scan_stats()
        
        return render_template('bts_scanner.html', 
                             hackrf_status=hackrf_status,
                             available_bands=available_bands,
                             scan_status=scan_status,
                             scan_results=scan_results,
                             scan_stats=scan_stats,
                             company='SIBERINDO')
    except Exception as e:
        return f"Error loading BTS scanner: {e}", 500

@scanner_bp.route('/api/bts_scan/start', methods=['POST'])
@login_required
def start_bts_scan():
    try:
        from modules.hackrf_manager import HackRFManager
        hackrf_manager = HackRFManager()
        
        data = request.get_json()
        band = data.get('band', 'GSM900')
        sample_rate = data.get('sample_rate', 2000000)
        gain = data.get('gain', 40)
        
        success, message = hackrf_manager.start_scan(band, sample_rate, gain)
        
        return jsonify({
            'success': success,
            'message': message,
            'band': band
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@scanner_bp.route('/api/bts_scan/stop')
@login_required
def stop_bts_scan():
    try:
        from modules.hackrf_manager import HackRFManager
        hackrf_manager = HackRFManager()
        
        success, message = hackrf_manager.stop_scan()
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@scanner_bp.route('/api/bts_scan/status')
@login_required
def get_bts_scan_status():
    try:
        from modules.hackrf_manager import HackRFManager
        hackrf_manager = HackRFManager()
        
        scan_status = hackrf_manager.get_scan_status()
        scan_results = hackrf_manager.get_scan_results()
        
        return jsonify({
            'scan_status': scan_status,
            'scan_results': scan_results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scanner_bp.route('/api/bts_scan/results')
@login_required
def get_bts_scan_results():
    try:
        from modules.hackrf_manager import HackRFManager
        hackrf_manager = HackRFManager()
        
        results = hackrf_manager.get_scan_results()
        stats = hackrf_manager.get_scan_stats()
        
        return jsonify({
            'results': results,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scanner_bp.route('/api/bts_scan/bands')
@login_required
def get_available_bands():
    try:
        from modules.hackrf_manager import HackRFManager
        hackrf_manager = HackRFManager()
        
        bands = hackrf_manager.get_available_bands()
        
        return jsonify({
            'bands': bands
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scanner_bp.route('/api/bts_scan/analyze', methods=['POST'])
@login_required
def analyze_bts_results():
    try:
        from modules.hackrf_manager import HackRFManager
        hackrf_manager = HackRFManager()
        
        results = hackrf_manager.get_scan_results()
        
        if not results:
            return jsonify({'success': False, 'message': 'No scan results to analyze'})
        
        # Analyze results
        analysis = {
            'total_towers': len(results),
            'bands_found': list(set([r['band'] for r in results])),
            'strongest_signal': max([r['signal'] for r in results]),
            'weakest_signal': min([r['signal'] for r in results]),
            'average_signal': sum([r['signal'] for r in results]) / len(results),
            'frequency_range': {
                'min': min([r['frequency'] for r in results]),
                'max': max([r['frequency'] for r in results])
            },
            'network_operators': list(set([f"{r['mcc']}-{r['mnc']}" for r in results]))
        }
        
        # Signal quality assessment
        excellent = len([r for r in results if r['signal'] >= -65])
        good = len([r for r in results if -75 <= r['signal'] < -65])
        fair = len([r for r in results if -85 <= r['signal'] < -75])
        poor = len([r for r in results if r['signal'] < -85])
        
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
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@scanner_bp.route('/api/bts_scan/export')
@login_required
def export_scan_results():
    try:
        from modules.hackrf_manager import HackRFManager
        import csv
        from io import StringIO
        from flask import Response
        
        hackrf_manager = HackRFManager()
        results = hackrf_manager.get_scan_results()
        
        if not results:
            return jsonify({'success': False, 'message': 'No results to export'})
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ARFCN', 'Channel', 'Frequency (MHz)', 'Signal (dBm)', 'Band', 
                        'MCC', 'MNC', 'LAC', 'Cell ID', 'Network', 'Timestamp'])
        
        # Write data
        for result in results:
            writer.writerow([
                result['arfcn'],
                result['channel'],
                result['frequency'],
                result['signal'],
                result['band'],
                result['mcc'],
                result['mnc'],
                result['lac'],
                result['cell_id'],
                result['network'],
                result['timestamp']
            ])
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=siberindo_bts_scan.csv"}
        )
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500