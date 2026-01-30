# aggressive_anti_debug.py
import sys
import threading
import time
import ctypes
import os
import builtins
import traceback

# Known debugger modules
DEBUGGER_MODULES = (
    "pdb",
    "ipdb",
    "rpdb",
    "winpdb",
    "pyringe",
    "pydevd",
    "pydevd_tracing",
    "pydevd_frame_eval",
    "pydev_ipython",
)

def detect_sys_trace():
    """Detect debugger via sys.gettrace()"""
    if sys.gettrace() is not None:
        terminate("Debugger detected: sys.gettrace active")

def detect_debugger_modules():
    """Detect known debugger modules"""
    for mod in DEBUGGER_MODULES:
        if mod in sys.modules:
            terminate(f"Debugger detected via module: {mod}")

def detect_ptrace():
    """Detect ptrace-based debugger on Linux"""
    if sys.platform.startswith("linux"):
        try:
            with open("/proc/self/status") as f:
                for line in f:
                    if line.startswith("TracerPid"):
                        if int(line.split(":")[1].strip()) != 0:
                            terminate("Debugger detected: ptrace active")
        except Exception:
            pass

def detect_windows_debugger():
    """Detect debugger on Windows using IsDebuggerPresent"""
    if sys.platform == "win32":
        if ctypes.windll.kernel32.IsDebuggerPresent():
            terminate("Debugger detected: Windows debugger attached")

def terminate(message):
    """Terminate immediately with minimal info"""
    try:
        # Overwrite stdout and stderr to prevent stack trace leaks
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        # Optionally log to a file instead
        # with open("anti_debug.log", "a") as f: f.write(message+"\n")
    finally:
        os._exit(1)  # Immediate termination

def run_anti_debug_checks():
    """Run all anti-debug checks"""
    detect_sys_trace()
    detect_debugger_modules()
    detect_ptrace()
    detect_windows_debugger()

def start_self_defending_thread(interval=2.0):
    """Start background thread that checks periodically"""
    def monitor():
        while True:
            run_anti_debug_checks()
            time.sleep(interval)
    t = threading.Thread(target=monitor, daemon=True)
    t.start()
    return t

# Optional: override exception printing to hide stack traces
def disable_stack_traces():
    def fake_excepthook(exc_type, exc_value, exc_traceback):
        # Only print a generic message
        print("Application terminated due to security policy.")
        os._exit(1)
    sys.excepthook = fake_excepthook

# Initialize aggressive protection immediately
run_anti_debug_checks()
disable_stack_traces()
start_self_defending_thread()
