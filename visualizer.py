import sys
import re
import time
import shutil
import threading
import socket
import select
import subprocess

# --- Configuration ---
print_lock = threading.Lock()
# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

BG_BLACK = "\033[40m"

# Backend Colors mapping
BACKEND_COLORS = [GREEN, CYAN, MAGENTA, BLUE, YELLOW]

# State
counts = {} # "port": count
total_requests = 0
success_requests = 0
failed_requests = 0
start_time = time.time()
last_activity_time = time.time()
last_rps_time = time.time()
last_request_count = 0
current_rps = 0.0
recent_logs = []
MAX_LOGS = 5
max_req_str = "N/A"
min_req_str = "N/A"

# System Stats State
cpu_usage = "..."
load_avg = "..."

def clear_screen():
    sys.stdout.write("\033[2J\033[H")

def move_cursor(y, x):
    sys.stdout.write(f"\033[{y};{x}H")

def draw_box(title, y, x, height, width, color=WHITE):
    # Top border
    move_cursor(y, x)
    sys.stdout.write(color + "┌" + "─" * (width - 2) + "┐" + RESET)
    
    # Title
    if title:
        move_cursor(y, x + 2)
        sys.stdout.write(color + BOLD + f" {title} " + RESET)

    # Side borders
    for i in range(1, height - 1):
        move_cursor(y + i, x)
        sys.stdout.write(color + "│" + RESET)
        move_cursor(y + i, x + width - 1)
        sys.stdout.write(color + "│" + RESET)
    
    # Bottom border
    move_cursor(y + height - 1, x)
    sys.stdout.write(color + "└" + "─" * (width - 2) + "┘" + RESET)

def get_system_stats():
    global cpu_usage, load_avg
    try:
        # Get Load Avg
        load = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode().strip()
        load_avg = load.split(" ")[1] # 1 min avg usually follows '{ '

        # Get CPU Usage (rough estimate from top)
        # top -l 1 -n 0 | grep "CPU usage"
        out = subprocess.check_output("top -l 1 -n 0 | grep 'CPU usage'", shell=True).decode().strip()
        # Format: CPU usage: 10.5% user, 20.0% sys, 69.5% idle
        parts = out.split(",")
        user = parts[0].split(":")[1].strip().split("%")[0]
        sys_val = parts[1].strip().split("%")[0]
        cpu_usage = f"{float(user) + float(sys_val):.1f}%"
    except:
        cpu_usage = "N/A"
        load_avg = "N/A"

def print_dashboard():
    global current_rps, last_rps_time, last_request_count
    with print_lock:
        _print_dashboard_internal()

def _print_dashboard_internal():
    global current_rps, last_rps_time, last_request_count
    # Force default if not a tty or too small
    try:
        w, h = shutil.get_terminal_size((80, 24))
        if w < 40 or h < 10: 
             width, height = 80, 24
        else:
             width, height = w, h
    except:
        width, height = 80, 24
    
    # Ensure minimum size
    if width < 60 or height < 20:
         width, height = 80, 24 

    # Hide cursor
    sys.stdout.write("\033[?25l")
    
    # Draw Main Border
    draw_box("Load Balancer Dashboard", 1, 1, height, width, BLUE)
    
    # --- Stats Section ---
    # Calculate Instant RPS
    now = time.time()
    dt = now - last_rps_time
    if dt >= 0.5: # Update if enough time passed
        current_rps = (total_requests - last_request_count) / dt
        last_rps_time = now
        last_request_count = total_requests

    move_cursor(3, 4)
    sys.stdout.write(f"{BOLD}Total Requests:{RESET} {total_requests}")
    
    move_cursor(3, 25)
    sys.stdout.write(f"{GREEN}{BOLD}Success:{RESET} {success_requests}")
    
    move_cursor(3, 40)
    sys.stdout.write(f"{RED}{BOLD}Failed:{RESET} {failed_requests}")
    
    move_cursor(3, 55)
    sys.stdout.write(f"{YELLOW}{BOLD}RPS:{RESET} {current_rps:.1f}")

    # Separator
    move_cursor(5, 2)
    sys.stdout.write(BLUE + "─" * (width - 2) + RESET)
    
    # --- System Stats Section ---
    move_cursor(6, 4)
    sys.stdout.write(f"{BOLD}System Load:{RESET} {load_avg}  {BOLD}CPU:{RESET} {cpu_usage}")

    move_cursor(7, 4)
    sys.stdout.write(f"{BOLD}Max Req:{RESET} {max_req_str}  {BOLD}Min Req:{RESET} {min_req_str}")

    # --- Backend Distribution ---
    move_cursor(9, 4)
    sys.stdout.write(f"{BOLD}Backend Distribution:{RESET}")
    
    y_offset = 11
    max_val = max(counts.values()) if counts.values() else 1
    # max bar width available
    bar_width_area = width - 20 
    
    idx = 0
    for port in sorted(counts.keys()):
        count = counts[port]
        color = BACKEND_COLORS[idx % len(BACKEND_COLORS)]
        
        # Calculate bar length
        bar_len = int((count / max_val) * bar_width_area) if max_val > 0 else 0
        bar_char = "█"
        bar = color + (bar_char * bar_len) + RESET
        
        move_cursor(y_offset + idx, 4)
        sys.stdout.write(f"Port {port}: {bar} {count}")
        idx += 1

    # Separator
    log_start_y = height - MAX_LOGS - 2
    move_cursor(log_start_y - 1, 2)
    sys.stdout.write(BLUE + "─" * (width - 2) + RESET)

    # --- Recent Logs ---
    move_cursor(log_start_y, 4)
    sys.stdout.write(f"{BOLD}Recent Activity:{RESET}")
    
    for i, log in enumerate(recent_logs[-MAX_LOGS:]):
        move_cursor(log_start_y + 1 + i, 4)
        # Truncate log to fit
        display_log = (log[:width-6] + '..') if len(log) > width-6 else log
        sys.stdout.write(DIM + display_log + RESET)
        
    sys.stdout.flush()

def update_counts(port):
    if port not in counts:
        counts[port] = 0
    counts[port] += 1
    global success_requests, total_requests
    success_requests += 1
    total_requests += 1

def add_log(msg):
    recent_logs.append(msg)
    if len(recent_logs) > MAX_LOGS:
        recent_logs.pop(0)

def reset_stats():
    global counts, total_requests, success_requests, failed_requests, start_time, last_request_count, max_req_str, min_req_str
    counts = {}
    total_requests = 0
    success_requests = 0
    failed_requests = 0
    start_time = time.time()
    last_request_count = 0
    max_req_str = "N/A"
    min_req_str = "N/A"
    add_log(f"{YELLOW}--- Stats Cleared ---{RESET}")
    print_dashboard()

def remote_listener():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Allow address reuse
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        udp.bind(("localhost", 9999))
    except OSError:
        add_log(f"{RED}Remote Reset Disabled (Port 9999 in use){RESET}")
        return

    while True:
        try:
            data, _ = udp.recvfrom(1024)
            if data == b"RESET":
                reset_stats()
        except:
            pass

def stats_updater():
    while True:
        get_system_stats()
        print_dashboard()
        time.sleep(2)

# --- Main Loop ---
# Start Listener
listener = threading.Thread(target=remote_listener, daemon=True)
listener.start()

# Start Stats Updater
stats_thread = threading.Thread(target=stats_updater, daemon=True)
stats_thread.start()

clear_screen()
print_dashboard()

try:
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        
        # Parse Logs
        # Case 1: "Forwarding request to localhost:8081"
        match_fwd = re.search(r"Forwarding request to localhost:(\d+)", line)
        if match_fwd:
            port = match_fwd.group(1)
            update_counts(port)
            add_log(f" -> Sent to {port}")
            print_dashboard()
            continue
            
        # Case 2: "Accepted connection from /127.0.0.1:56224"
        if "Accepted connection" in line:
            pass

        # Case 3: "No backend servers available"
        if "No backend servers available" in line:
            failed_requests += 1
            total_requests += 1
            add_log(f"{RED}No Backends!{RESET}")
            print_dashboard()
            continue
        
        # Case 4: Connection Error "Error forwarding to backend"
        if "Error forwarding to backend" in line:
            failed_requests += 1
            success_requests -= 1 
            
            add_log(f"{RED}Backend Fail!{RESET}")
            print_dashboard()
            continue
            
        # Case 5: Health Status Change
        # Log: ⚠️  Server localhost:8081 status changed to: UNHEALTHY
        if "status changed to:" in line:
            parts = line.split("status changed to:")
            status = parts[1].strip()
            # Extract server just before "status"
            # format: ... Server localhost:8081 ...
            srv_part = parts[0]
            # Simple parsing:
            if "UNHEALTHY" in status:
                add_log(f"{RED}{BOLD}Server DOWN!{RESET}")
            else:
                add_log(f"{GREEN}{BOLD}Server UP!{RESET}")
            print_dashboard()
            continue
            
        # Case 6: Stats Parsing
        # 📊 Stats - Max Requests: Port 8081 (150) | Min Requests: Port 8083 (142)
        if "📊 Stats" in line:
            match_stats = re.search(r"Max Requests: Port (\d+) \((\d+)\) \| Min Requests: Port (\d+) \((\d+)\)", line)
            if match_stats:
                max_port = match_stats.group(1)
                max_val = match_stats.group(2)
                min_port = match_stats.group(3)
                min_val = match_stats.group(4)
                
                max_req_str = f"Port {max_port} ({max_val})"
                min_req_str = f"Port {min_port} ({min_val})"
                print_dashboard()
            continue

except KeyboardInterrupt:
    # Cleanup
    sys.stdout.write("\033[?25h") # Show cursor
    move_cursor(100, 1)
    print("\nVisualizer stopped.")
