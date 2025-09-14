"""
Enhanced callback logging system with colors and consistent formatting
"""
import json
import threading
import uuid
import inspect
from typing import Dict, Any, Optional
from datetime import datetime


class CallbackLogger:
    """Enhanced logger for Dash callbacks with colors and consistent formatting"""
    
    # Thread-local storage for execution context
    _local = threading.local()
    _print_lock = threading.Lock()
    
    # ANSI color codes
    COLORS = {
        'RESET': '\033[0m',
        'BOLD': '\033[1m',
        'DIM': '\033[2m',
        
        # Callback type colors
        'RENDER': '\033[94m',      # Blue - for render callbacks
        'UPDATE': '\033[92m',      # Green - for update/filter callbacks
        'TOGGLE': '\033[93m',      # Yellow - for toggle callbacks
        'RESET_CB': '\033[91m',    # Red - for reset callbacks
        'LOAD': '\033[95m',        # Magenta - for load callbacks
        'DISPLAY': '\033[96m',     # Cyan - for display callbacks
        
        # Status colors
        'SUCCESS': '\033[92m',     # Green
        'WARNING': '\033[93m',     # Yellow
        'ERROR': '\033[91m',       # Red
        'INFO': '\033[94m',        # Blue
        
        # Component colors
        'HEADER': '\033[1;97m',    # Bold white
        'SEPARATOR': '\033[90m',   # Dark gray
        'KEY': '\033[96m',         # Cyan
        'VALUE': '\033[97m',       # White
    }
    
    @classmethod
    def _get_callback_color(cls, callback_name: str) -> str:
        """Determine color based on callback name pattern"""
        name_lower = callback_name.lower()
        
        if 'render' in name_lower:
            return cls.COLORS['RENDER']
        elif any(word in name_lower for word in ['update', 'filter', 'apply']):
            return cls.COLORS['UPDATE']
        elif 'toggle' in name_lower:
            return cls.COLORS['TOGGLE']
        elif 'reset' in name_lower:
            return cls.COLORS['RESET_CB']
        elif any(word in name_lower for word in ['load', 'get', 'page']):
            return cls.COLORS['LOAD']
        elif 'display' in name_lower:
            return cls.COLORS['DISPLAY']
        else:
            return cls.COLORS['INFO']
    
    @classmethod
    def _short_str(cls, s: Any, max_len: int = 14) -> str:
        """Shorten string representation for display"""
        try:
            s = str(s)
        except Exception:
            return str(s)
        if len(s) > max_len:
            return f"{s[:4]}…{s[-4:]}"
        return s
    
    @classmethod
    def _clean_value(cls, value: Any, key_name: str = "") -> Any:
        """Clean and format values for display"""
        if isinstance(value, dict):
            cleaned = {}
            for k, v in value.items():
                if v is None or v == "":
                    continue
                if isinstance(v, str) and v == "all":
                    continue
                # Special handling for trip selection
                if k in ("selected_trip", "selected_trip_id") and isinstance(v, dict) and "trip_id" in v:
                    cleaned["selected_trip_id"] = cls._short_str(v.get("trip_id"))
                    continue
                cleaned[k] = cls._clean_value(v, k)
            return cleaned
        elif isinstance(value, list):
            return [cls._clean_value(v, key_name) for v in value if v is not None and v != ""]
        elif isinstance(value, str):
            # Ne jamais tronquer les erreurs
            if 'error' in key_name.lower() or any(keyword in value.lower() for keyword in ['error', 'exception', 'traceback', 'failed']):
                return value  # Retourner l'erreur complète
            elif len(value) < 50:
                return value  # Retourner les courtes chaînes
            return cls._short_str(value)
        return value
    
    @classmethod
    def _format_key_value_pairs(cls, data: Dict[str, Any], indent: str = "  ") -> list:
        """Format key-value pairs with colors"""
        if not data:
            return [f"{indent}{cls.COLORS['DIM']}(none){cls.COLORS['RESET']}"]
        
        lines = []
        for key, value in data.items():
            try:
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, ensure_ascii=False)
                else:
                    value_str = str(value)
            except Exception:
                value_str = str(value)
            
            # Ne pas tronquer les erreurs dans l'affichage final
            if key == 'error' or 'error' in key.lower():
                # Afficher l'erreur complète sans troncature
                pass
            elif len(value_str) > 200 and not any(keyword in value_str.lower() for keyword in ['error', 'exception', 'traceback']):
                # Tronquer seulement les très longues valeurs qui ne sont pas des erreurs
                value_str = f"{value_str[:100]}...{value_str[-50:]}"
            
            # Color formatting
            key_colored = f"{cls.COLORS['KEY']}{key}{cls.COLORS['RESET']}"
            value_colored = f"{cls.COLORS['VALUE']}{value_str}{cls.COLORS['RESET']}"
            lines.append(f"{indent}- {key_colored}: {value_colored}")
        
        return lines
    
    @classmethod
    def _get_execution_id(cls) -> str:
        """Get or create execution ID for current thread"""
        if not hasattr(cls._local, 'execution_id'):
            cls._local.execution_id = str(uuid.uuid4())[:8]
        return cls._local.execution_id
    
    @classmethod
    def _create_separator(cls, char: str = "─", length: int = 50) -> str:
        """Create colored separator line"""
        return f"{cls.COLORS['SEPARATOR']}{char * length}{cls.COLORS['RESET']}"
    
    @classmethod
    def log_data_dict(cls, title: str, data: Dict[str, Any], status: str = "INFO") -> None:
        """Log a dictionary with formatted display"""
        with cls._print_lock:
            # Header
            print(f"\n{cls.COLORS['HEADER']}📊 {title.upper()}{cls.COLORS['RESET']}")
            print(cls._create_separator("=", 80))
            
            # Data display
            if not data:
                print(f"   {cls.COLORS['DIM']}(aucune donnée){cls.COLORS['RESET']}")
            else:
                for key, value in data.items():
                    # Format value based on type
                    if value is None:
                        value_str = f"{cls.COLORS['DIM']}None{cls.COLORS['RESET']}"
                    elif isinstance(value, bool):
                        value_str = f"{cls.COLORS['SUCCESS'] if value else cls.COLORS['ERROR']}{value}{cls.COLORS['RESET']}"
                    elif isinstance(value, (int, float)):
                        value_str = f"{cls.COLORS['VALUE']}{value}{cls.COLORS['RESET']}"
                    elif isinstance(value, str):
                        # Truncate long strings
                        if len(value) > 50:
                            value_str = f"{cls.COLORS['VALUE']}{value[:47]}...{cls.COLORS['RESET']}"
                        else:
                            value_str = f"{cls.COLORS['VALUE']}{value}{cls.COLORS['RESET']}"
                    else:
                        value_str = f"{cls.COLORS['VALUE']}{str(value)}{cls.COLORS['RESET']}"
                    
                    # Type info
                    type_str = f"{cls.COLORS['DIM']}({type(value).__name__}){cls.COLORS['RESET']}"
                    
                    # Format line
                    key_colored = f"{cls.COLORS['KEY']}{key:25}{cls.COLORS['RESET']}"
                    print(f"   {key_colored} = {value_str} {type_str}")
            
            print(cls._create_separator("=", 80) + "\n")
    
    @classmethod
    def _get_caller_info(cls) -> Dict[str, str]:
        """Get information about the calling function and class"""
        try:
            # Get the current frame and walk up the stack
            frame = inspect.currentframe()
            
            # Skip frames until we find the actual caller (not CallbackLogger methods)
            while frame:
                frame = frame.f_back
                if not frame:
                    break
                    
                # Get function name and filenam
                func_name = frame.f_code.co_name
                filename = frame.f_code.co_filename
                
                # Skip CallbackLogger methods and internal Python frames
                if (func_name not in ['log_callback', '_get_caller_info'] and 
                    'callback_logger.py' not in filename and
                    not filename.startswith('<')):
                    
                    # Try to get class name from 'self' or 'cls' in locals
                    class_name = None
                    if 'self' in frame.f_locals:
                        class_name = frame.f_locals['self'].__class__.__name__
                    elif 'cls' in frame.f_locals:
                        class_name = frame.f_locals['cls'].__name__
                    
                    # Extract module name from filename
                    module_parts = filename.replace('\\', '/').split('/')
                    if len(module_parts) > 1:
                        module_name = module_parts[-1].replace('.py', '')
                    else:
                        module_name = 'unknown'
                    
                    return {
                        'function': func_name,
                        'class': class_name or 'N/A',
                        'module': module_name
                    }
            
            return {'function': 'unknown', 'class': 'N/A', 'module': 'unknown'}
            
        except Exception:
            return {'function': 'unknown', 'class': 'N/A', 'module': 'unknown'}

    @classmethod
    def log_callback(cls, name: str, inputs: Dict[str, Any], states: Optional[Dict[str, Any]] = None, 
                    status: str = "INFO", extra_info: Optional[str] = None):
        """
        Enhanced callback logging with colors and consistent formatting
        
        Args:
            name: Callback function name
            inputs: Input parameters
            states: State parameters
            status: Log status (INFO, SUCCESS, WARNING, ERROR)
            extra_info: Additional information to display
        """
        try:
            # Get caller information
            caller_info = cls._get_caller_info()
            
            # Clean inputs and states, but preserve error messages
            cleaned_inputs = {}
            for k, v in (inputs or {}).items():
                cleaned_inputs[k] = cls._clean_value(v, k)
            
            cleaned_states = {}
            for k, v in (states or {}).items():
                cleaned_states[k] = cls._clean_value(v, k)
            
            # Get colors and execution context
            callback_color = cls._get_callback_color(name)
            status_color = cls.COLORS.get(status, cls.COLORS['INFO'])
            execution_id = cls._get_execution_id()
            
            # Create timestamp
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Thread-safe printing
            with cls._print_lock:
                # Print formatted log
                print(f"\n{cls._create_separator()}")
                
                # Header with callback name, execution ID and timestamp
                header = f"[CB:{execution_id}] {name}"
                if extra_info:
                    header += f" | {extra_info}"
                
                # Add caller information
                caller_display = f"{caller_info['class']}.{caller_info['function']}" if caller_info['class'] != 'N/A' else caller_info['function']
                caller_text = f" {cls.COLORS['DIM']}({caller_info['module']}::{caller_display}){cls.COLORS['RESET']}"
                
                print(f"{callback_color}{cls.COLORS['BOLD']}{header}{cls.COLORS['RESET']}"
                      f"{caller_text} {cls.COLORS['DIM']}@ {timestamp}{cls.COLORS['RESET']}")
                
                # Status indicator
                if status != "INFO":
                    print(f"{status_color}[{status}]{cls.COLORS['RESET']}")
                
                # Inputs section
                print(f"{cls.COLORS['HEADER']}Inputs:{cls.COLORS['RESET']}")
                for line in cls._format_key_value_pairs(cleaned_inputs):
                    print(line)
                
                # States section
                if cleaned_states:
                    print(f"{cls.COLORS['HEADER']}States:{cls.COLORS['RESET']}")
                    for line in cls._format_key_value_pairs(cleaned_states):
                        print(line)
                
                print(cls._create_separator())
            
        except Exception as e:
            # Fallback to simple logging if color formatting fails
            print(f"\n{'=' * 80}")
            print(f"[CB] {name} (logging error: {e})")
            print(f"Inputs: {inputs}")
            print(f"States: {states or {}}")
            print('=' * 80)
    
    @classmethod
    def log_api_call(cls, operation: str, details: Dict[str, Any], status: str = "INFO"):
        """Log API calls with consistent formatting"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            status_color = cls.COLORS.get(status, cls.COLORS['INFO'])
            execution_id = cls._get_execution_id()
            
            with cls._print_lock:
                print(f"\n{cls.COLORS['SEPARATOR']}{'─' * 80}{cls.COLORS['RESET']}")
                print(f"{cls.COLORS['INFO']}{cls.COLORS['BOLD']}[API:{execution_id}] {operation}{cls.COLORS['RESET']} "
                      f"{cls.COLORS['DIM']}@ {timestamp}{cls.COLORS['RESET']}")
                
                if status != "INFO":
                    print(f"{status_color}[{status}]{cls.COLORS['RESET']}")
                
                for line in cls._format_key_value_pairs(details):
                    print(line)
                
                print(f"{cls.COLORS['SEPARATOR']}{'─' * 80}{cls.COLORS['RESET']}")
            
        except Exception as e:
            print(f"[API] {operation} (logging error: {e}) - {details}")
    
    @classmethod
    def log_cache_operation(cls, operation: str, key: str, hit: bool = None, details: Optional[Dict] = None):
        """Log cache operations with consistent formatting"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            execution_id = cls._get_execution_id()
            
            # Determine status color based on cache hit/miss
            if hit is True:
                status_color = cls.COLORS['SUCCESS']
                status_text = "HIT"
            elif hit is False:
                status_color = cls.COLORS['WARNING']
                status_text = "MISS"
            else:
                status_color = cls.COLORS['INFO']
                status_text = "INFO"
            
            with cls._print_lock:
                print(f"\n{cls.COLORS['SEPARATOR']}{'·' * 80}{cls.COLORS['RESET']}")
                print(f"{cls.COLORS['INFO']}{cls.COLORS['BOLD']}[CACHE:{execution_id}] {operation}{cls.COLORS['RESET']} "
                      f"{status_color}[{status_text}]{cls.COLORS['RESET']} "
                      f"{cls.COLORS['DIM']}@ {timestamp}{cls.COLORS['RESET']}")
                
                # Show cache key
                print(f"  {cls.COLORS['KEY']}key{cls.COLORS['RESET']}: {cls.COLORS['VALUE']}{cls._short_str(key, 50)}{cls.COLORS['RESET']}")
                
                # Show additional details if provided
                if details:
                    for line in cls._format_key_value_pairs(details):
                        print(line)
                
                print(f"{cls.COLORS['SEPARATOR']}{'·' * 80}{cls.COLORS['RESET']}")
            
        except Exception as e:
            print(f"[CACHE] {operation} - {key} (logging error: {e})")


# Convenience functions for backward compatibility
def log_callback(name: str, inputs: Dict[str, Any], states: Optional[Dict[str, Any]] = None):
    """Backward compatible callback logging function"""
    CallbackLogger.log_callback(name, inputs, states)

def log_api_call(operation: str, details: Dict[str, Any], status: str = "INFO"):
    """Log API calls"""
    CallbackLogger.log_api_call(operation, details, status)

def log_cache_operation(operation: str, key: str, hit: bool = None, details: Optional[Dict] = None):
    """Log cache operations"""
    CallbackLogger.log_cache_operation(operation, key, hit, details)
