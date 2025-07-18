

# PyModoro – A Pomodoro Timer That Works With You

PyModoro is a Pomodoro timer for Windows, built with Python and Tkinter. It’s designed for people who want a simple, modern timer that doesn’t get in the way. The interface is clean and dark, and you get sound notifications, system tray support, and a session log.

## What Makes PyModoro Different?

Most Pomodoro timers force you to stick to the clock. PyModoro is a little more flexible. If you keep working after the timer hits zero, the timer will keep counting down into the negatives. This way, you can see exactly how much extra time you worked past your scheduled Pomodoro—no guilt, no interruptions, just an honest record of your focus. When you’re ready, you can start your break with a click, and the overtime is logged for you.

## Features

- Set your own Pomodoro, short break, and long break durations
- Simple, distraction-free dark mode interface
- Keeps track of how many Pomodoros you’ve finished
- Sound notifications for work and break sessions (customizable)
- Edit all durations and the Pomodoro threshold in the app
- Session log file (copied to clipboard automatically when you close the app)
- Button to clear/reset your session
- Open or copy the log file from inside the app
- Minimize to system tray
- Native Windows notifications

## How the Timer Works

Start a Pomodoro and the timer counts down. If you finish early, hit **Take Break** or **Stop**. If you keep working after the timer reaches zero, the timer goes negative—so you can see exactly how much extra time you put in. When you’re ready, start your break. The overtime is recorded in the log, so you always have an honest record of your actual work, not just what the timer says you “should” do.

You’re in control: the timer is a guide, not a boss.

## Requirements

- Windows 10 or newer
- Python 3.8 or newer
- The following Python packages:
  - `pyperclip` (clipboard support)
  - `pystray` (system tray icon)
  - `plyer` (system notifications)
  - `Pillow` (for the tray icon)
  - `pyinstaller` (only if you want to build a standalone .exe)

To install all required packages:

```sh
pip install pyperclip pystray plyer Pillow
```

## How to Run

1. Make sure you’ve installed the requirements above.
2. Double-click `pomodoro-timer.pyw` to run, or launch from the command line:

   ```sh
   pythonw pomodoro-timer.pyw
   ```

## Usage

- **Start**: Begin a Pomodoro session.
- **Stop**: Pause the timer.
- **Reset**: Set the timer back to the start of the current Pomodoro.
- **Take Break**: Skip straight to a break (your Pomodoro is logged, including any overtime).
- **Edit Settings**: Change durations and the Pomodoro threshold.
- **Clear Session**: Reset all counters and timers.
- **Open Log**: Open the session log in your default text editor.
- **Copy Log**: Copy the session log to your clipboard.
- When a break or Pomodoro ends, you’ll get a sound and a message.
- When you close the app, your session log is copied to your clipboard automatically.

## Building a Standalone Windows Executable

If you want to run PyModoro on a computer without Python, you can package it as a standalone `.exe` using [PyInstaller](https://pyinstaller.org/).

1. Install PyInstaller:

   ```sh
   pip install pyinstaller
   ```

2. Build the executable:

   Run this command in the folder with `pomodoro-timer.pyw`, `pymodoro.ico`, `start_work.wav`, and `start_break.wav`:

   ```sh
   pyinstaller --onefile --windowed --icon=pymodoro.ico \
     --add-data "pymodoro.ico;." \
     --add-data "start_work.wav;." \
     --add-data "start_break.wav;." \
     pomodoro-timer.pyw
   ```

   The `.exe` will be in the `dist` folder. You can now run or share it—no Python required.

   If you change the icon or code, just rebuild with the same command.

## Customization

- You can edit durations and the Pomodoro threshold in the app, or by editing `settings.json` (created after first run).
- To use your own sounds, replace `start_work.wav` and `start_break.wav` with your own `.wav` files in the same folder.

## Notes

- PyModoro is designed for Windows.
- All session logs are saved to `pomodoro.log` in the app folder.
- The log is wiped every time you start the app.


## Roadmap

- [x] Button to reset all tasks, pomodoros, and timers to zero
- [x] Improve GUI aesthetics and styling
- [x] Add application icon
- [x] Make window resizable
- [ ] Add small text box for session tasks (write to log, clear on new session)
- [x] Native OS notifications (e.g., plyer or win10toast)
- [ ] Global hotkey support
- [x] Minimize to system tray
- [ ] User-configurable themes
- [ ] Allow user-defined/custom sound files

## License

MIT License. Do whatever you want, but no warranty.


