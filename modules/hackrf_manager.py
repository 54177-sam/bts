import subprocess
import logging
import re
import json
import threading
import time
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class HackRFManager:
    def __init__(self):
        self.scan_process = None
        self.is_scanning = False
        self.scan_results = []
        self._hackrf_status = None
        self.last_detection = None
        self.detection_history = []
        self.scan_progress = 0
        self.current_operation = ""
        self.scan_thread = None
        
        # GSM frequency bands (in MHz)
        self.gsm_bands = {
            'GSM900': {'start': 925, 'end': 960, 'uplink_offset': 45},
            'DCS1800': {'start': 1805, 'end': 1880, 'uplink_offset': 95},
            'PCS1900': {'start': 1930, 'end': 1990, 'uplink_offset': 80}
        }
    
    def _check_hackrf_availability(self):
        """Check if hackrf tools are available"""
        try:
            result = subprocess.run(['which', 'hackrf_info'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def detect_hackrf(self):
        """Detect HackRF device with detailed information"""
        detection_time = datetime.now()
        
        if self._hackrf_status is None:
            self._hackrf_status = self._check_hackrf_availability()
        
        if not self._hackrf_status:
            self.last_detection = {
                'timestamp': detection_time,
                'status': 'tools_not_available',
                'device_info': None
            }
            return False
            
        try:
            # Run hackrf_info to detect device
            result = subprocess.run(
                ['hackrf_info'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            detected = result.returncode == 0 and "Found HackRF" in result.stdout
            
            # Parse detailed information if detected
            device_info = {}
            if detected:
                for line in result.stdout.split('\n'):
                    if 'Board ID Number' in line:
                        device_info['board_id'] = line.split(':')[1].strip()
                    elif 'Firmware Version' in line:
                        device_info['firmware'] = line.split(':')[1].strip()
                    elif 'Serial number' in line:
                        device_info['serial'] = line.split(':')[1].strip()
                    elif 'Part ID Number' in line:
                        device_info['part_id'] = line.split(':')[1].strip()
                    elif 'Hardware Rev' in line:
                        device_info['version'] = line.split(':')[1].strip()
            
            self.last_detection = {
                'timestamp': detection_time,
                'status': 'connected' if detected else 'not_connected',
                'device_info': device_info if detected else None,
                'raw_output': result.stdout if detected else None
            }
            
            # Add to history (keep last 10 detections)
            self.detection_history.append(self.last_detection)
            if len(self.detection_history) > 10:
                self.detection_history.pop(0)
                
            logger.info(f"HackRF detection: {detected}")
            return detected
                
        except subprocess.TimeoutExpired:
            self.last_detection = {
                'timestamp': detection_time,
                'status': 'timeout',
                'device_info': None
            }
            logger.error("HackRF detection timeout")
            return False
        except Exception as e:
            self.last_detection = {
                'timestamp': detection_time,
                'status': 'error',
                'device_info': None,
                'error': str(e)
            }
            logger.error(f"HackRF detection error: {e}")
            return False

    def get_detection_status(self):
        """Get detailed detection status"""
        if self.last_detection is None:
            self.detect_hackrf()
        
        status_map = {
            'connected': ('Connected', 'success', 'HackRF device is connected and ready'),
            'not_connected': ('Not Connected', 'danger', 'No HackRF device detected'),
            'tools_not_available': ('Tools Not Installed', 'warning', 'HackRF tools are not installed'),
            'timeout': ('Detection Timeout', 'warning', 'HackRF detection timed out'),
            'error': ('Detection Error', 'danger', 'Error during HackRF detection')
        }
        
        status = self.last_detection['status']
        display_text, badge_type, description = status_map.get(status, ('Unknown', 'secondary', 'Unknown status'))
        
        return {
            'connected': status == 'connected',
            'display_text': display_text,
            'badge_type': badge_type,
            'description': description,
            'device_info': self.last_detection.get('device_info'),
            'timestamp': self.last_detection['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'detection_count': len(self.detection_history)
        }

    def get_hackrf_info(self):
        """Get detailed HackRF information - FIXED METHOD"""
        info = {
            "status": "Not detected",
            "board_id": "N/A",
            "firmware": "N/A", 
            "serial": "N/A",
            "part_id": "N/A",
            "version": "N/A"
        }
        
        detection_status = self.get_detection_status()
        
        if detection_status['connected'] and detection_status['device_info']:
            info.update(detection_status['device_info'])
            info["status"] = "Connected"
        else:
            info["status"] = detection_status['display_text']
            
        return info

    def _run_actual_scan(self, band, sample_rate, gain):
        """Run actual BTS scan using HackRF and kalibrate-hackrf"""
        try:
            self.current_operation = f"Scanning {band} band"
            self.scan_progress = 10
            
            # Check if kalibrate-hackrf is available
            kalibrate_check = subprocess.run(['which', 'kalibrate-hackrf'], 
                                           capture_output=True, text=True)
            if kalibrate_check.returncode != 0:
                logger.warning("kalibrate-hackrf not found, using simulated scan")
                return self._run_simulated_scan(band)
            
            # Determine frequency range based on band
            if band == 'GSM900':
                freq_range = '-g'
            elif band == 'DCS1800':
                freq_range = '-d'
            else:
                freq_range = '-g'  # Default to GSM900
            
            # Run kalibrate-hackrf
            cmd = ['kalibrate-hackrf', freq_range, '-s', str(sample_rate), '-g', str(gain)]
            
            logger.info(f"Running BTS scan: {' '.join(cmd)}")
            self.scan_progress = 30
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.scan_process = process
            
            # Read output in real-time
            results = []
            output_lines = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    output_lines.append(line.strip())
                    logger.debug(f"kalibrate output: {line.strip()}")
                    
                    # Parse kalibrate output
                    bts_data = self._parse_kalibrate_output(line)
                    if bts_data:
                        results.append(bts_data)
                        self.scan_progress = min(90, 30 + len(results) * 10)
            
            process.wait()
            self.scan_progress = 100
            
            if results:
                logger.info(f"Found {len(results)} BTS towers")
                return True, f"Scan completed. Found {len(results)} BTS towers.", results
            else:
                # If no results from parsing, try to parse all output
                for line in output_lines:
                    bts_data = self._parse_kalibrate_output(line + '\n')
                    if bts_data:
                        results.append(bts_data)
                
                if results:
                    logger.info(f"Found {len(results)} BTS towers (from full output)")
                    return True, f"Scan completed. Found {len(results)} BTS towers.", results
                else:
                    return False, "No BTS towers found in scan.", []
                
        except Exception as e:
            logger.error(f"Error during actual scan: {e}")
            return False, f"Scan error: {str(e)}", []

    def _parse_kalibrate_output(self, line):
        """Parse kalibrate-hackrf output to extract BTS information"""
        try:
            # Example kalibrate output: "chan: 51 (935.2MHz + 320Hz)	power: 78202.95"
            line = line.strip()
            if 'chan:' in line and 'power:' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    chan_part = parts[0]
                    power_part = parts[1]
                    
                    # Extract channel number
                    chan_match = re.search(r'chan:\s*(\d+)', chan_part)
                    if not chan_match:
                        return None
                    
                    channel = int(chan_match.group(1))
                    
                    # Extract frequency
                    freq_match = re.search(r'\((\d+\.?\d*)MHz', chan_part)
                    if freq_match:
                        frequency = float(freq_match.group(1))
                    else:
                        # Calculate frequency from channel
                        if channel <= 124:  # GSM900
                            frequency = 935.0 + 0.2 * (channel - 1)
                        else:  # DCS1800
                            frequency = 1805.2 + 0.2 * (channel - 512)
                    
                    # Extract power
                    power_match = re.search(r'power:\s*([\d.]+)', power_part)
                    power = float(power_match.group(1)) if power_match else 0
                    
                    # Convert power to dBm (approximate)
                    signal_dbm = -30 - (power / 10000) if power > 0 else -100
                    
                    # Determine band and other parameters
                    if frequency < 1000:
                        band_name = "GSM900"
                        mcc, mnc = "510", "10"  # Default Indonesia
                    else:
                        band_name = "DCS1800"
                        mcc, mnc = "510", "10"  # Default Indonesia
                    
                    return {
                        "arfcn": channel,
                        "frequency": round(frequency, 2),
                        "signal": round(signal_dbm, 1),
                        "power": round(power, 2),
                        "mcc": mcc,
                        "mnc": mnc,
                        "lac": random.randint(1000, 2000),
                        "cell_id": random.randint(1, 100),
                        "band": band_name,
                        "network": f"SIBERINDO {band_name}",
                        "timestamp": datetime.now().strftime('%H:%M:%S'),
                        "channel": f"CH{channel}"
                    }
            return None
        except Exception as e:
            logger.error(f"Error parsing kalibrate output: {e}")
            return None

    def _run_simulated_scan(self, band):
        """Run simulated BTS scan (fallback when kalibrate not available)"""
        try:
            self.current_operation = f"Simulating {band} scan"
            
            # Simulate scanning process
            steps = 10
            for i in range(steps):
                time.sleep(0.5)
                self.scan_progress = (i + 1) * 10
                if self.scan_process and self.scan_process.poll() is not None:
                    break
            
            # Generate realistic simulated results based on band
            results = []
            if band == 'GSM900':
                channels = [51, 52, 53, 54, 76, 77, 78, 79, 975, 976, 977]
                base_freq = 935.0
            elif band == 'DCS1800':
                channels = [512, 513, 514, 562, 563, 564, 612, 613, 614]
                base_freq = 1805.2
            else:  # PCS1900
                channels = [512, 513, 562, 563, 612, 613, 661, 662, 710, 711]
                base_freq = 1930.2
            
            for channel in random.sample(channels, random.randint(3, min(6, len(channels)))):
                frequency = base_freq + 0.2 * (channel - (1 if band == 'GSM900' else 512))
                signal = random.randint(-85, -45)
                
                results.append({
                    "arfcn": channel,
                    "frequency": round(frequency, 2),
                    "signal": signal,
                    "power": abs(signal) * 1000,
                    "mcc": "510",
                    "mnc": "10",
                    "lac": random.randint(1000, 2000),
                    "cell_id": random.randint(1, 100),
                    "band": band,
                    "network": f"SIBERINDO {band}",
                    "timestamp": datetime.now().strftime('%H:%M:%S'),
                    "channel": f"CH{channel}",
                    "simulated": True
                })
            
            # Sort by signal strength (strongest first)
            results.sort(key=lambda x: x['signal'], reverse=True)
            
            self.scan_progress = 100
            
            if results:
                return True, f"Simulated scan completed. Found {len(results)} BTS towers.", results
            else:
                return False, "No BTS towers found in simulated scan.", []
                
        except Exception as e:
            logger.error(f"Error during simulated scan: {e}")
            return False, f"Simulated scan error: {str(e)}", []

    def start_scan(self, band='GSM900', sample_rate=2000000, gain=40):
        """Start BTS scanning with HackRF"""
        detection_status = self.get_detection_status()
        
        if not detection_status['connected']:
            return False, f"HackRF not available: {detection_status['description']}"
        
        if self.is_scanning:
            return False, "Scan already in progress"
        
        try:
            self.is_scanning = True
            self.scan_progress = 0
            self.scan_results = []
            self.current_operation = f"Initializing {band} scan"
            
            # Start scan in a separate thread
            def scan_thread():
                try:
                    success, message, results = self._run_actual_scan(band, sample_rate, gain)
                    self.scan_results = results
                    self.is_scanning = False
                    self.scan_progress = 100
                    self.current_operation = "Scan completed"
                    logger.info(f"Scan thread completed: {message}")
                except Exception as e:
                    logger.error(f"Scan thread error: {e}")
                    self.is_scanning = False
                    self.scan_progress = 0
                    self.current_operation = f"Scan error: {str(e)}"
            
            self.scan_thread = threading.Thread(target=scan_thread)
            self.scan_thread.daemon = True
            self.scan_thread.start()
            
            return True, f"Started {band} band scan. Please wait..."
            
        except Exception as e:
            logger.error(f"Error starting scan: {e}")
            self.is_scanning = False
            return False, f"Scan error: {str(e)}"

    def stop_scan(self):
        """Stop ongoing scan"""
        if self.is_scanning and self.scan_process:
            try:
                self.scan_process.terminate()
                self.scan_process.wait(timeout=5)
            except:
                try:
                    self.scan_process.kill()
                except:
                    pass
            finally:
                self.is_scanning = False
                self.scan_progress = 0
                self.current_operation = "Scan stopped"
                logger.info("BTS scan stopped by user")
                return True, "Scan stopped successfully"
        
        self.is_scanning = False
        self.scan_progress = 0
        self.current_operation = "Scan stopped"
        return False, "No active scan to stop"

    def get_scan_results(self):
        """Get current scan results"""
        return self.scan_results

    def get_scan_status(self):
        """Get current scan status"""
        return {
            'is_scanning': self.is_scanning,
            'progress': self.scan_progress,
            'current_operation': self.current_operation,
            'results_count': len(self.scan_results),
            'band_being_scanned': self.current_operation.replace('Scanning ', '').replace(' band', '') if 'Scanning' in self.current_operation else 'Unknown'
        }

    def get_available_bands(self):
        """Get available GSM frequency bands"""
        return [
            {'name': 'GSM900', 'description': '900 MHz (Primary GSM)', 'range': '925-960 MHz'},
            {'name': 'DCS1800', 'description': '1800 MHz (Digital Cellular)', 'range': '1805-1880 MHz'},
            {'name': 'PCS1900', 'description': '1900 MHz (Personal Comm)', 'range': '1930-1990 MHz'}
        ]

    def get_scan_stats(self):
        """Get scanning statistics"""
        total_bts = sum(1 for result in self.scan_results if not result.get('simulated', False))
        simulated_bts = sum(1 for result in self.scan_results if result.get('simulated', False))
        
        return {
            'total_scans': len([d for d in self.detection_history if d.get('scan_triggered')]),
            'last_scan_time': self.last_detection['timestamp'] if self.last_detection else None,
            'total_bts_found': len(self.scan_results),
            'real_bts_found': total_bts,
            'simulated_bts_found': simulated_bts,
            'strongest_signal': max([r['signal'] for r in self.scan_results]) if self.scan_results else -100
        }