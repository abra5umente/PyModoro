
# Simple Pomodoro Timer

PyModoro is a focused, modern Pomodoro timer for Windows, built with Python and Tkinter. It helps you stay productive by breaking your work into intervals, with short and long breaks in between. The app features a clean dark UI, sound notifications, and session logging.

## Features

- Customizable Pomodoro, short break, and long break durations
- Modern, distraction-free dark interface
- Keeps track of completed Pomodoros
- Sound notifications for work and break sessions
- Settings editor for easy configuration
- Session log file (copied to clipboard on exit)
- Button to clear/reset session
- Open and copy log file from the app

## Requirements

- Python 3.8 or newer
- The following Python packages:
  - `pyperclip`
  - `pyinstaller` - Only required to create .exe

## How to Run

1. Install the required package:

   ```sh
   pip install pyperclip
   ```

2. Double-click `pomodoro-timer.pyw` to run, or launch from the command line:

   ```sh
   pythonw pomodoro-timer.pyw
   ```

## Usage

- Click **Start** to begin a Pomodoro session.
- **Stop** pauses the timer.
- **Reset** sets the timer back to the start of the current Pomodoro.
- **Take Break** lets you skip straight to a break.
- **Edit Settings** lets you change durations and the Pomodoro threshold.
- **Clear Session** resets all counters and timers.
- **Open Log** opens the session log in your default text editor.
- **Copy Log** copies the session log to your clipboard.
- When a break or Pomodoro ends, you'll get a sound and a message.
- When you close the app, your session log is copied to your clipboard.

## Building a Standalone Windows Executable

You can package PyModoro as a standalone `.exe` for Windows using [PyInstaller](https://pyinstaller.org/). This will let you run the app on any Windows machine without needing Python installed.

### Steps

1. **Install PyInstaller:**

   ```sh
   pip install pyinstaller
   ```

2. **Build the executable:**


   Run this command in the folder containing `pomodoro-timer.pyw`, `pymodoro.ico`, `start_work.wav`, and `start_break.wav`:

   ```sh
   pyinstaller --onefile --windowed --icon=pymodoro.ico \
     --add-data "pymodoro.ico;." \
     --add-data "start_work.wav;." \
     --add-data "start_break.wav;." \
     pomodoro-timer.pyw
   ```

   - `--onefile`: Bundle everything into a single `.exe` file.
   - `--windowed`: No console window (for GUI apps).
   - `--icon=...`: Sets the icon for the window and taskbar.
   - `--add-data`: Ensures each data file is available at runtime.

3. **Find your `.exe`:**

   The executable will be in the `dist` folder (e.g., `dist/pomodoro-timer.exe`).

4. **Distribute or use:**

   You can now run or share the `.exe`—no Python required!

**Note:** If you change the icon or code, rerun the build command.

## Customization

- You can edit durations and the Pomodoro threshold in the app, or by editing `settings.json` (created after first run).
- To use your own sounds, replace `start_work.wav` and `start_break.wav` with your own `.wav` files in the same folder.

## Notes

- This app is designed for Windows.
- All session logs are saved to `pomodoro.log` in the app folder.
- `pomodoro.log` is wiped upon each application startup.

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


