import sys
import re
import time
import shutil
import threading
import socket
import select

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

def print_dashboard():
    global current_rps, last_rps_time, last_request_count
    with print_lock:
        _print_dashboard_internal()

def _print_dashboard_internal():
    global current_rps, last_rps_time, last_request_count
    # Force default if not a tty or too small
    # shutil.get_terminal_size fallback is only used if the system call fails, 
    # but sometimes it returns (0, 0) or (80, 24) but maybe I messed up the logic?
    # Let's just hardcode a default if it looks wrong.
    try:
        w, h = shutil.get_terminal_size((80, 24))
        if w < 40 or h < 10: # Even looser check
             width, height = 80, 24
        else:
             width, height = w, h
    except:
        width, height = 80, 24
    
    # Ensure minimum size
    if width < 60 or height < 20:
         # Fallback for small screens
         # sys.stdout.write("\033[2J\033[H")
         # print("Terminal too small for dashboard.")
         # return
         width, height = 80, 24 # Just force it


    # Hide cursor
    sys.stdout.write("\033[?25l")
    
    # Background
    # sys.stdout.write(BG_BLACK) 
    
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
    
    # --- Backend Distribution ---
    move_cursor(6, 4)
    sys.stdout.write(f"{BOLD}Backend Distribution:{RESET}")
    
    y_offset = 8
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
    global counts, total_requests, success_requests, failed_requests, start_time, last_request_count
    counts = {}
    total_requests = 0
    success_requests = 0
    failed_requests = 0
    start_time = time.time()
    last_request_count = 0
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


# --- Main Loop ---
# Start Listener
listener = threading.Thread(target=remote_listener, daemon=True)
listener.start()

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

except KeyboardInterrupt:
    # Cleanup
    sys.stdout.write("\033[?25h") # Show cursor
    move_cursor(100, 1)
    print("\nVisualizer stopped.")
