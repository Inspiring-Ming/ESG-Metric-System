import socket
import subprocess
import sys
import time
import signal
import os
from typing import Optional

class PortManager:
    """Utility to manage Flask application ports consistently"""
    
    DEFAULT_PORT = 5000
    BACKUP_PORTS = [5001, 5002, 5003, 5004, 5005]
    
    @staticmethod
    def is_port_in_use(port: int) -> bool:
        """Check if a port is currently in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except OSError:
                return True
    
    @staticmethod
    def find_process_on_port(port: int) -> Optional[int]:
        """Find the PID of process using the given port"""
        try:
            # Try netstat first (macOS/Linux)
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError, FileNotFoundError):
            pass
        
        return None
    
    @staticmethod
    def kill_process_on_port(port: int) -> bool:
        """Kill process running on the given port"""
        pid = PortManager.find_process_on_port(port)
        if pid:
            try:
                print(f"🔄 Killing existing process {pid} on port {port}")
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)  # Give process time to shutdown gracefully
                
                # Check if it's still running, force kill if necessary
                if PortManager.find_process_on_port(port):
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(1)
                
                return not PortManager.is_port_in_use(port)
            except (OSError, ProcessLookupError):
                return not PortManager.is_port_in_use(port)
        return True
    
    @staticmethod
    def get_available_port(preferred_port: int = None) -> int:
        """Get an available port with smart conflict resolution"""
        if preferred_port is None:
            preferred_port = PortManager.DEFAULT_PORT
        
        # First check if preferred port is available
        if not PortManager.is_port_in_use(preferred_port):
            print(f"✅ Using preferred port {preferred_port}")
            return preferred_port
        
        # Check what process is using the port
        existing_pid = PortManager.find_process_on_port(preferred_port)
        if existing_pid:
            print(f"⚠️ Port {preferred_port} is in use by process {existing_pid}")
            
            # Only try to kill if it's an old ESG process, not system processes
            try:
                result = subprocess.run(['ps', '-p', str(existing_pid), '-o', 'command='], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and any(keyword in result.stdout.lower() 
                                                for keyword in ['esg', 'demo', 'flask']):
                    print(f"🔄 Attempting to free port {preferred_port} from old ESG process...")
                    if PortManager.kill_process_on_port(preferred_port):
                        print(f"✅ Successfully freed port {preferred_port}")
                        return preferred_port
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass
        
        # Fall back to backup ports
        print(f"🔍 Searching for alternative port...")
        for backup_port in PortManager.BACKUP_PORTS:
            if not PortManager.is_port_in_use(backup_port):
                print(f"✅ Using alternative port {backup_port}")
                return backup_port
        
        # Extended search for higher ports
        for port in range(8080, 8090):
            if not PortManager.is_port_in_use(port):
                print(f"✅ Using available port {port}")
                return port
        
        # Last resort: find any available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            random_port = s.getsockname()[1]
            print(f"⚠️ Using system-assigned port {random_port}")
            return random_port
    
    @staticmethod
    def cleanup_esg_processes():
        """Clean up any existing ESG system processes (excluding current process)"""
        try:
            current_pid = os.getpid()
            
            # Find processes that might be ESG-related
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            esg_processes = []
            for line in result.stdout.split('\n'):
                if any(keyword in line.lower() for keyword in ['esg_api', 'flask']) and \
                   any(esg_keyword in line.lower() for esg_keyword in ['esg', 'demo', 'api']):
                    try:
                        pid = int(line.split()[1])
                        # Don't kill current process or its parent
                        if pid != current_pid and pid != os.getppid():
                            esg_processes.append(pid)
                    except (ValueError, IndexError):
                        pass
            
            # Kill ESG processes (excluding current)
            for pid in esg_processes:
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"🧹 Cleaned up old ESG process {pid}")
                except (OSError, ProcessLookupError):
                    pass
            
            if esg_processes:
                time.sleep(2)  # Give processes time to shutdown
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
    
    @staticmethod
    def run_flask_app_with_port_management(app, host='0.0.0.0', preferred_port=None, debug=False):
        """Run Flask app with proper port management"""
        if preferred_port is None:
            preferred_port = PortManager.DEFAULT_PORT
        
        # Clean up any existing processes first
        PortManager.cleanup_esg_processes()
        
        # Get available port
        port = PortManager.get_available_port(preferred_port)
        
        print(f"🚀 Starting ESG System on http://localhost:{port}")
        print(f"📊 Frontend available at: http://localhost:{port}/demo")
        print(f"🔧 API available at: http://localhost:{port}/api/...")
        
        try:
            app.run(host=host, port=port, debug=debug, use_reloader=False)
        except KeyboardInterrupt:
            print(f"\n⏹️ Shutting down ESG System on port {port}")
        except Exception as e:
            print(f"❌ Error running Flask app: {e}")
            # Try backup port if there's an error
            if port != PortManager.DEFAULT_PORT:
                print(f"🔄 Retrying on default port {PortManager.DEFAULT_PORT}")
                app.run(host=host, port=PortManager.DEFAULT_PORT, debug=debug, use_reloader=False) 