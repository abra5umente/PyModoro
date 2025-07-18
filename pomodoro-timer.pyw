def resource_path(filename):
    """Get absolute path to resource, works for dev and for PyInstaller .exe."""
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.abspath(filename)

import time
import threading
import tkinter as tk
from tkinter import ttk
import winsound
import os
import logging
import pyperclip
import json
import pystray
from PIL import Image
from plyer import notification

# --- Default Settings ---
DEFAULT_SETTINGS = {
    "pomodoro_duration_minutes": 25,
    "short_break_duration_minutes": 5,
    "long_break_duration_minutes": 15,
    "pomodoro_threshold": 4,
}

# --- Global State Variables ---
settings = DEFAULT_SETTINGS.copy()
current_duration_seconds = settings["pomodoro_duration_minutes"] * 60
pomodoros_completed = 0
timer_running = False
current_timer_thread = None
break_prompted = False  # Ensures only one break prompt per Pomodoro
break_modal = None      # Reference to the break modal, if open

# GUI elements
root = None
timer_label = None
pomodoro_count_label = None
message_label = None

# Core functions #

def show_notification(title, message):
    """Show a system notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="PyModoro",
            timeout=5  # seconds
        )
    except Exception as e:
        print(f"Notification error: {e}")

def load_settings():
    """Loads settings from settings.json, creating it if it doesn't exist."""
    global settings
    try:
        with open("settings.json", "r") as f:
            settings.update(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        save_settings()  # Create the file with default settings

def save_settings():
    """Saves the current settings to settings.json."""
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)
    show_gui_message("Settings saved.", "green")

def edit_settings():
    """Opens a simple settings editor."""
    settings_window = tk.Toplevel(root)
    settings_window.title("Edit Settings")
    settings_window.geometry("350x350")
    settings_window.grab_set()
    settings_window.transient(root)
    settings_window.focus_set()
    settings_window.configure(bg="#2C3E50")

    def save_and_close(event=None):
        global settings, current_duration_seconds
        try:
            new_settings = {
                "pomodoro_duration_minutes": float(pomodoro_entry.get()),
                "short_break_duration_minutes": float(short_break_entry.get()),
                "long_break_duration_minutes": float(long_break_entry.get()),
                "pomodoro_threshold": int(threshold_entry.get()),
            }
            if any(v <= 0 for k, v in new_settings.items() if k != "pomodoro_threshold") or new_settings["pomodoro_threshold"] <= 0:
                show_gui_message("Durations and threshold must be positive.", "red")
                return

            settings.update(new_settings)
            save_settings()
            load_settings()
            if not timer_running:
                current_duration_seconds = int(settings["pomodoro_duration_minutes"] * 60)
                update_gui_timer()
            settings_window.destroy()
        except ValueError:
            show_gui_message("Invalid input. Please enter numbers for durations and integer for threshold.", "red")

    labels = ["Pomodoro Duration (min):", "Short Break Duration (min):", "Long Break Duration (min):", "Pomodoro Threshold:"]
    entries = []
    default_values = [settings["pomodoro_duration_minutes"], settings["short_break_duration_minutes"],
                      settings["long_break_duration_minutes"], settings["pomodoro_threshold"]]

    for i, label_text in enumerate(labels):
        ttk.Label(settings_window, text=label_text, background="#2C3E50", foreground="white", font=("Helvetica", 10)).pack(pady=(10, 2))
        entry = ttk.Entry(settings_window, width=20, font=("Helvetica", 10))
        entry.insert(0, str(default_values[i]))
        entry.bind('<Return>', save_and_close)
        entry.pack(pady=(0, 5))
        entries.append(entry)

    pomodoro_entry, short_break_entry, long_break_entry, threshold_entry = entries

    save_button = ttk.Button(settings_window, text="Save Settings", command=save_and_close, style="TButton")
    save_button.pack(pady=20)

# Update all uses of settings[..._duration_minutes] * 60 to int(settings[..._duration_minutes] * 60)
def reset_timer():
    global current_duration_seconds, timer_running, break_prompted, break_modal
    break_prompted = False
    break_modal = None
    if timer_running:
        stop_timer()
    current_duration_seconds = int(settings["pomodoro_duration_minutes"] * 60)
    show_gui_message("Timer reset.", "white")
    update_gui_timer()

def clear_session():
    """Resets all session variables to their initial state."""
    global current_duration_seconds, pomodoros_completed, timer_running
    current_duration_seconds = settings["pomodoro_duration_minutes"] * 60
    pomodoros_completed = 0
    timer_running = False
    update_gui_timer()
    update_gui_pomodoro_count()
    show_gui_message("Session cleared.", "white")
    log_session("Session cleared.")

def open_log_file(log_file):
    """Opens the log file in the default text editor."""
    try:
        os.startfile(log_file)
    except Exception as e:
        show_gui_message(f"Error opening log file: {e}", "red")
        log_session(f"Error opening log file: {e}")

def setup_logging():
    """Configures logging to a file, wiping it on each run."""
    logging.basicConfig(
        filename='pomodoro.log',
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def copy_log_to_clipboard():
    """Reads the log file and copies its content to the clipboard."""
    try:
        with open('pomodoro.log', 'r') as log_file:
            log_content = log_file.read()
            pyperclip.copy(log_content)
            log_session("Log copied to clipboard.")
            show_gui_message("Log copied to clipboard!", "green")
    except FileNotFoundError:
        log_session("Log file not found, nothing to copy.")
        show_gui_message("Log file not found, nothing to copy.", "red")
    except Exception as e:
        log_session(f"Error copying log to clipboard: {e}")
        show_gui_message(f"Error copying log: {e}", "red")

def format_time(seconds):
    """Format time in seconds to MM:SS, with negative sign if needed"""
    sign = "" if seconds >= 0 else "-"
    abs_seconds = int(abs(seconds))
    minutes = abs_seconds // 60
    secs = abs_seconds % 60
    return f"{sign}{minutes:02d}:{secs:02d}"

def update_gui_timer():
    """Updates the GUI timer label with the current time."""
    if timer_label:
        timer_label.config(text=format_time(current_duration_seconds))

def update_gui_pomodoro_count():
    """Updates the GUI pomodoro count label."""
    if pomodoro_count_label:
        pomodoro_count_label.config(text=f"Pomodoros Completed: {pomodoros_completed}")

def show_gui_message(message, color="white"):
    """Display a message in the GUI."""
    if message_label:
        message_label.config(text=message, foreground=color)
        root.after(5000, lambda: message_label.config(text=""))

def play_sound(sound_file):
    """Plays a sound file if it exists."""
    path = resource_path(sound_file)
    if not os.path.exists(path):
        show_gui_message(f"Sound file not found: {sound_file}", "red")
        return
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        show_gui_message(f"Error playing sound: {e}", "red")

def countdown_timer_threaded():
    """Manages the countdown timer in a separate thread."""
    global current_duration_seconds, pomodoros_completed, timer_running, break_prompted
    overtime = 0
    notified = False
    while timer_running:
        root.after(0, update_gui_timer)
        time.sleep(1)
        current_duration_seconds -= 1
        if current_duration_seconds == 0 and not notified:
            show_notification("Pomodoro Complete!", "Time to take a break!")
            root.after(0, show_gui_message, "Time to take a break!", "orange")
            root.after(0, play_sound, "start_break.wav")
            notified = True
            # Prompt for break immediately at 00:00, but DO NOT stop the timer
            if not break_prompted:
                break_prompted = True
                root.after(0, prompt_start_break_while_running)
        # Only prompt once, and only if timer_running is still True
        if current_duration_seconds < 0 and not break_prompted and timer_running:
            break_prompted = True
            root.after(0, prompt_start_break_while_running)
        if current_duration_seconds < 0:
            overtime += 1
        # If timer_running was set to False by the break modal, exit loop immediately
        if not timer_running:
            break
    # Restore increment_pomodoro call for overtime handling
    if current_duration_seconds <= 0:
        root.after(0, increment_pomodoro, abs(current_duration_seconds))

def prompt_start_break_while_running():
    global timer_running, break_prompted, break_modal
    # Prevent multiple modals and prompts
    if break_prompted or (break_modal is not None and break_modal.winfo_exists()):
        return
    break_prompted = True
    if pomodoros_completed % settings["pomodoro_threshold"] == 0 and pomodoros_completed != 0:
        break_duration = settings["long_break_duration_minutes"]
    else:
        break_duration = settings["short_break_duration_minutes"]
    prompt = tk.Toplevel(root)
    break_modal = prompt
    prompt.title("Start Break?")
    prompt.geometry("350x150")
    prompt.grab_set()
    prompt.transient(root)
    prompt.focus_set()
    prompt.configure(bg="#2C3E50")
    prompt.protocol("WM_DELETE_WINDOW", lambda: None)
    msg = ttk.Label(prompt, text="Ready to start your break?", background="#2C3E50", foreground="white", font=("Helvetica", 14))
    msg.pack(pady=20)
    def start_break():
        global timer_running, pomodoros_completed, current_duration_seconds
        prompt.destroy()
        timer_running = False
        # Calculate overtime
        overtime = abs(current_duration_seconds) if current_duration_seconds < 0 else 0
        pomodoros_completed += 1
        update_gui_pomodoro_count()
        scheduled = settings["pomodoro_duration_minutes"] * 60
        overtime_min = int(overtime // 60)
        overtime_sec = int(overtime % 60)
        if overtime > 0:
            log_session(f"Pomodoro #{pomodoros_completed} completed. Overtime: {overtime_min:02d}:{overtime_sec:02d}")
        else:
            log_session(f"Pomodoro #{pomodoros_completed} completed.")
        if pomodoros_completed % settings["pomodoro_threshold"] == 0:
            message = f"🎉 Time for a long break! ({settings['long_break_duration_minutes']} min)"
            log_session(f"Long break ({settings['long_break_duration_minutes']} min)")
        else:
            message = f"Time for a short break! ({settings['short_break_duration_minutes']} min)"
            log_session(f"Short break ({settings['short_break_duration_minutes']} min)")
        show_gui_message(message, "blue")
        start_break_gui(break_duration)
    ok_btn = ttk.Button(prompt, text="Start Break", command=start_break, style="TButton")
    ok_btn.pack(pady=10)


def start_timer():
    """Start the countdown timer."""
    global timer_running, current_timer_thread, break_prompted, break_modal
    break_prompted = False
    break_modal = None
    if timer_running:
        show_gui_message("Timer is already running.", "red")
        return
    timer_running = True
    current_timer_thread = threading.Thread(target=countdown_timer_threaded)
    current_timer_thread.daemon = True
    current_timer_thread.start()
    show_gui_message("Timer started.", "green")
    play_sound("start_work.wav")

def stop_timer():
    """Stop the countdown timer."""
    global timer_running
    if not timer_running:
        show_gui_message("Timer is not running.", "red")
        return
    timer_running = False
    show_gui_message("Timer stopped.", "black")

def reset_timer():
    """Reset the timer to the initial duration."""
    global current_duration_seconds, timer_running, break_prompted, break_modal
    break_prompted = False
    break_modal = None
    if timer_running:
        stop_timer()
    current_duration_seconds = int(settings["pomodoro_duration_minutes"] * 60)
    show_gui_message("Timer reset.", "white")
    update_gui_timer()

def increment_pomodoro():
    """Increments the count of completed pomodoros."""

def increment_pomodoro(overtime_seconds=0):
    global pomodoros_completed, current_duration_seconds
    pomodoros_completed += 1
    update_gui_pomodoro_count()
    # Calculate actual work duration
    scheduled = int(settings["pomodoro_duration_minutes"] * 60)
    actual = scheduled + overtime_seconds
    overtime_min = int(overtime_seconds // 60)
    overtime_sec = int(overtime_seconds % 60)
    if overtime_seconds > 0:
        log_session(f"Pomodoro #{pomodoros_completed} completed. Overtime: {overtime_min:02d}:{overtime_sec:02d}")
    else:
        log_session(f"Pomodoro #{pomodoros_completed} completed.")
    if pomodoros_completed % settings["pomodoro_threshold"] == 0:
        message = f"🎉 Time for a long break! ({settings['long_break_duration_minutes']} min)"
        break_duration = settings["long_break_duration_minutes"]
        log_session(f"Long break ({settings['long_break_duration_minutes']} min)")
    else:
        message = f"Time for a short break! ({settings['short_break_duration_minutes']} min)"
        break_duration = settings["short_break_duration_minutes"]
        log_session(f"Short break ({settings['short_break_duration_minutes']} min)")

    show_gui_message(message, "blue")
    prompt_start_break(break_duration)
    # Don't reset timer here; will be reset when user starts next Pomodoro

def prompt_start_break(duration_minutes):
    """Prompt the user to start the break, only then start the break timer."""
    prompt = tk.Toplevel(root)
    prompt.title("Start Break?")
    prompt.geometry("350x150")
    prompt.grab_set()
    prompt.transient(root)
    prompt.focus_set()
    prompt.configure(bg="#2C3E50")

    msg = ttk.Label(prompt, text="Ready to start your break?", background="#2C3E50", foreground="white", font=("Helvetica", 14))
    msg.pack(pady=20)

    def start_break():
        prompt.destroy()
        start_break_gui(duration_minutes)

    ok_btn = ttk.Button(prompt, text="Start Break", command=start_break, style="TButton")
    ok_btn.pack(pady=10)

def start_break_gui(duration_minutes):
    """Starts a break countdown and shows a message box"""
    break_seconds = int(duration_minutes * 60)

    break_window = tk.Toplevel(root)
    break_window.title("Break Time!")
    break_window.geometry("350x200")
    break_window.grab_set()
    break_window.transient(root)
    break_window.focus_set()
    break_window.configure(bg="#2C3E50")

    break_time_label = ttk.Label(
        break_window,
        text=f"Break: {format_time(break_seconds)}",
        font=("Helvetica", 36, "bold"),
        background="#2C3E50",
        foreground="#ECF0F1",
    )
    break_time_label.pack(pady=20)

    def update_break_timer(rem_seconds):
        if rem_seconds > 0:
            break_time_label.config(text=f"Break {format_time(rem_seconds)}")
            break_window.after(1000, update_break_timer, rem_seconds - 1)
        else:
            break_window.destroy()
            show_notification("Break Ended", "Ready for next Pomodoro!")
            show_gui_message("Break ended. Ready for next Pomodoro!", "green")
            log_session("Break ended.")
            prompt_start_work()
            play_sound("work_reminder.mp3")

    ok_button = ttk.Button(break_window, text="Dismiss", command=break_window.destroy, style="TButton")
    ok_button.pack(pady=10)

    update_break_timer(break_seconds)

def prompt_start_work():
    prompt = tk.Toplevel(root)
    prompt.title("Start Pomodoro?")
    prompt.geometry("350x150")
    prompt.grab_set()
    prompt.transient(root)
    prompt.focus_set()
    prompt.configure(bg="#2C3E50")

    msg = ttk.Label(prompt, text="Ready to start your next Pomodoro?", background="#2C3E50", foreground="white", font=("Helvetica", 14))
    msg.pack(pady=20)


    def start_work():
        global current_duration_seconds, timer_running
        current_duration_seconds = settings["pomodoro_duration_minutes"] * 60
        update_gui_timer()
        prompt.destroy()
        start_timer()

    ok_btn = ttk.Button(prompt, text="Start Work", command=start_work, style="TButton")
    ok_btn.pack(pady=10)

def take_break_now():
    """Allows the user to take a break immediately."""
    global timer_running
    if timer_running:
        stop_timer()
    increment_pomodoro()
    update_gui_timer()

def log_session(event_description):
    """Logs session events with a timestamp."""
    logging.info(event_description)

def create_tray_icon(root):
    # Use your .ico file for the tray icon
    icon_path = resource_path("pymodoro.ico")
    image = Image.open(icon_path)

    def on_restore(icon, item):
        root.after(0, show_window)
        icon.stop()

    def on_exit(icon, item):
        root.after(0, on_closing)
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Restore", on_restore),
        pystray.MenuItem("Exit", on_exit)
    )
    tray_icon = pystray.Icon("PyModoro", image, "PyModoro", menu)
    return tray_icon

def show_window():
    root.deiconify()
    root.after(0, root.lift)

def hide_window_to_tray():
    root.withdraw()
    tray_icon = create_tray_icon(root)
    threading.Thread(target=tray_icon.run, daemon=True).start()


# main GUI setup #
def setup_gui():
    global root, timer_label, pomodoro_count_label, message_label

    import sys
    root = tk.Tk()
    # Robust icon path for PyInstaller and normal run
    icon_path = "pymodoro.ico"
    if hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, "pymodoro.ico")
    try:
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Warning: Could not set window icon: {e}")
    root.title("PyModoro")
    root.geometry("450x450")
    root.resizable(True, True)
    root.minsize(450, 450)
    root.bind("<Unmap>", on_minimize)
    reset_timer()
    
    # Add the style configuration
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TFrame", background="#2C3E50")
    style.configure("TLabel", background="#2C3E50", foreground="white", font=("Helvetica", 10))
    style.configure("TButton", background="#3498DB", foreground="white", font=("Helvetica", 10, "bold"), borderwidth=0)
    style.map("TButton", background=[('active', '#217DBB')])

    root.configure(bg="#2C3E50")

    timer_label = ttk.Label(
        root,
        text=format_time(current_duration_seconds),
        font=("Helvetica", 64, "bold"),
        background="#34495E",
        foreground="#ECF0F1",
        padding=(20, 10),
        relief="raised",
    )
    timer_label.pack(pady=25)

    pomodoro_count_label = ttk.Label(
        root, text=f"Pomodoros: {pomodoros_completed}",
        font=("Helvetica", 16),
        background="#2C3E50",
        foreground="#BDC3C7"
    )
    pomodoro_count_label.pack()

    message_label = ttk.Label(root, text="", font=("Helvetica", 12, "italic"), background="#2C3E50", foreground="white")
    message_label.pack(pady=10)

    button_frame = ttk.Frame(root, style="TFrame")
    button_frame.pack(pady=15)

    for i in range(4):
        button_frame.grid_columnconfigure(i, weight=1)

    start_btn = ttk.Button(button_frame, text="Start", command=start_timer, style="TButton")
    start_btn.grid(row=0, column=0, padx=7, pady=7)

    stop_btn = ttk.Button(button_frame, text="Stop", command=stop_timer, style="TButton")
    stop_btn.grid(row=0, column=1, padx=7, pady=7)

    reset_btn = ttk.Button(button_frame, text="Reset", command=reset_timer, style="TButton")
    reset_btn.grid(row=0, column=2, padx=7, pady=7)

    break_btn = ttk.Button(button_frame, text="Take Break", command=take_break_now, style="TButton")
    break_btn.grid(row=0, column=3, padx=7, pady=7)

    settings_btn = ttk.Button(button_frame, text="Edit Settings", command=edit_settings, style="TButton")
    settings_btn.grid(row=1, column=0, padx=7, pady=7)

    clear_btn = ttk.Button(button_frame, text="Clear Session", command=clear_session, style="TButton")
    clear_btn.grid(row=1, column=1, padx=7, pady=7)

    log_btn = ttk.Button(button_frame, text="Open Log", command=lambda: open_log_file('pomodoro.log'), style="TButton")
    log_btn.grid(row=1, column=2, padx=7, pady=7)

    copy_log_btn = ttk.Button(button_frame, text="Copy Log", command=copy_log_to_clipboard, style="TButton")
    copy_log_btn.grid(row=1, column=3, padx=7, pady=7)


    update_gui_timer()
    update_gui_pomodoro_count()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

def on_closing():
    """Handles window closing event."""
    copy_log_to_clipboard()
    root.destroy()

def on_minimize(event):
    if root.state() == 'iconic':
        hide_window_to_tray()


if __name__ == "__main__":
    load_settings()
    setup_logging()
    setup_gui()
