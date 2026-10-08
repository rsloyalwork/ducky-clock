# Ducky Clock
This is a little Duck that lives on your desktop and tells you when to work and when to rest. It is based off of the duck clock in Cass Wizard's bedroom in the show "Bee and PuppyCat". It'll float above your windows, running in place, and flashes it's message in time as it runs.

## Features
- Shows **Work!** during your working hours and **Rest!** outside of them.
- Right-Click to start a break, or pick a lunch length.
- Settings window for work hours, break length, and every message.
- Drag it anywhere on screen; clicks pass through empty space around it.
- Remembers your settings in between runs.
- Works on Linux and Windows.

## Download

Builds for Linux and Windows are made automatically on every update.

1. Go to the [Actions tab](https://github.com/YOUR-USERNAME/ducky-clock/actions)
2. Click the most recent successful run (green check)
3. Scroll to **Artifacts** and download `ducky-clock-Linux` or `ducky-clock-Windows`
4. Unzip it and run `ducky-clock` (Linux) or `ducky-clock.exe` (Windows)

You need to be signed in to GitHub to download from Actions.

On Linux, you may need to make the file runnable first:

```bash
chmod +x ducky-clock
```

### Heads up

These builds aren't code-signed. Windows will show "Windows protected your PC". Click **More info**, then **Run anyway**.
Some antivirus tools may also flag it, because of how the app unpacks itself when it starts.

## Using it

- **Drag** the duck to move it
- **Right-click** for break, lunch, settings, start at login, and quit
- Settings are saved in `~/.ducky_clock.json` on Linux, or `C:\Users\<you>\.ducky_clock.json` on Windows

## Running from source

Requires Python 3.10 or newer.

```bash
git clone https://github.com/YOUR-USERNAME/ducky-clock.git
cd ducky-clock
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python duck.py
```

## Building it yourself

```bash
pyinstaller --onefile --windowed --name ducky-clock duck.py
```

The app ends up in the `dist` folder.

## Notes

- On Linux under Wayland, the duck runs through XWayland so it can stay on top and remember where it is. Most Wayland desktops include XWayland by default.
- Fullscreen apps (games, videos) cover the duck, on purpose.
