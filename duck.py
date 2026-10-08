import os
import signal
import sys
import json

if sys.platform.startswith("linux"):
    os.environ["QT_QPA_PLATFORM"] = "xcb"  # Ensure X11 is used on Linux

from PySide6.QtCore import Qt, QTimer, QRect, QTime, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QRegion, QPolygon, QIcon 
from PySide6.QtWidgets import (
    QApplication, QWidget, QMenu, QDialog, QFormLayout, QTimeEdit, QLineEdit, QSpinBox, QDialogButtonBox, QFrame, QVBoxLayout, QLabel,
) 
from datetime import datetime, time, timedelta
from pathlib import Path

signal.signal(signal.SIGINT, signal.SIG_DFL)

YELLOW = QColor(255, 255, 0)
ORANGE = QColor(255, 165, 0)
PASTEL_WHITE = QColor(255, 255, 255, 200)
TEXT_COLOR = QColor(0, 0, 0)
SETTINGS_FILE = Path.home() / ".ducky_clock.json"
DEFAULT_SETTINGS = {
    "work_start": "08:30",
    "work_end": "17:00",
    "work_message": "Work!",
    "off_message": "Rest!",
    "break_minutes": 15,
    "break_message": "Break!",
    "lunch_message": "Lunch!",
}

def load_settings():
    settings = DEFAULT_SETTINGS.copy()
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            settings.update(json.load(f))
    save_settings(settings)  # Ensure the file is created if it doesn't exist
    return settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def make_cute(menu):
    menu.setAttribute(Qt.WA_TranslucentBackground)
    menu.setStyleSheet(MENU_STYLE)
    
APP_NAME = "Ducky Clock"
LINUX_AUTOSTART = Path.home() / ".config" / "autostart" / "ducky-clock.desktop"

def launch_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    script = os.path.abspath(__file__)
    return f'"{sys.executable}" "{script}"'

def autostart_enabled():
    if sys.platform == "win32":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run")
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    return LINUX_AUTOSTART.exists()

def set_autostart(enabled):
    if sys.platform == "win32":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, launch_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    return

    if enabled:
        LINUX_AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
        LINUX_AUTOSTART.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Ducky Clock\n"
            f"Exec={launch_command()}\n"
            "X-GNOME-Autostart-enabled=true\n"
        )
    else:
        LINUX_AUTOSTART.unlink(missing_ok=True)

MENU_STYLE = """
QMenu {
    background-color: #FFF6B0;
    border: 3px solid #FFA500;
    border-radius: 14px;
    padding: 6px;
}
QMenu::item {
    color: #5A4628;
    font-weight: bold;
    padding: 6px 24px 6px 14px;
    border-radius: 8px;
}
QMenu::item:selected {
    background-color: #FFA500;
    color: white;
}
"""

SETTINGS_STYLE = """
#card {
    background-color: #FFF6B0;
    border: 3px solid #FFA500;
    border-radius: 24px;
}
QLabel {
    color: #5A4628;
    font-weight: bold;
    min-height: 30px;
}
#title {
    font-size: 18px;
}
QLineEdit, QSpinBox, QTimeEdit {
    background: #FFFAF0;
    border: 2px solid #FFA500;
    border-radius: 10px;
    padding: 4px 8px;
}
QTimeEdit::up-button, QTimeEdit::down-button {
    width: 0px;
}
QPushButton {
    background-color: #FFA500;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 6px 18px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #FF8C00;
}
"""

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ducky Clock Settings")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(SETTINGS_STYLE)
        self.work_start = QTimeEdit(QTime.fromString(settings["work_start"], "HH:mm"))
        self.work_start.setDisplayFormat("h:mm AP")
        self.work_end = QTimeEdit(QTime.fromString(settings["work_end"], "HH:mm"))
        self.work_end.setDisplayFormat("h:mm AP")
        self.work_message = QLineEdit(settings["work_message"])
        self.off_message = QLineEdit(settings["off_message"])
        
        self.break_minutes = QSpinBox()
        self.break_minutes.setRange(1, 120)
        self.break_minutes.setSuffix(" min")
        self.break_minutes.setValue(settings["break_minutes"])
        self.break_message = QLineEdit(settings["break_message"])
        self.lunch_message = QLineEdit(settings["lunch_message"])
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        for button in buttons.buttons():
            button.setIcon(QIcon())  # Remove icons from buttons
        
        card = QFrame(self)
        card.setObjectName("card")
        outer = QVBoxLayout(self)
        outer.addWidget(card)
        
        title = QLabel("Ducky Settings", self)
        title.setObjectName("title")
        
        layout = QFormLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        layout.addRow(title)
        layout.addRow("Work Starts:", self.work_start)
        layout.addRow("Work Ends:", self.work_end)
        layout.addRow("Work Message:", self.work_message)
        layout.addRow("After-hours Message:", self.off_message)
        layout.addRow("Break Length:", self.break_minutes)
        layout.addRow("Break Message:", self.break_message)
        layout.addRow("Lunch Message:", self.lunch_message)
        layout.addRow(buttons)
        
    def get_settings(self):
            return {
                "work_start": self.work_start.time().toString("HH:mm"),
                "work_end": self.work_end.time().toString("HH:mm"),
                "work_message": self.work_message.text(),
                "off_message": self.off_message.text(),
                "break_minutes": self.break_minutes.value(),
                "break_message": self.break_message.text(),
                "lunch_message": self.lunch_message.text(),
            }

class Duck(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint 
            | Qt.WindowStaysOnTopHint 
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(240, 240)
        self.update_mask()
        self.drag_offset = None
        self.frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(120)  # Update every 120 ms for smooth animation
        self.settings = load_settings()
        self.message = ""
        self.away_message = None
        self.away_until = None
        self.check_time()  # Initial check for the message
        
        self.clock = QTimer(self)
        self.clock.timeout.connect(self.check_time)
        self.clock.start(5000)  # Update every 5 seconds

    def start_away(self, message, duration_minutes):
        self.away_message = message
        self.away_until = datetime.now() + timedelta(minutes=duration_minutes)
        self.check_time()  # Update message immediately
        
    def end_away(self):
        self.away_message = None
        self.away_until = None
        self.check_time()  # Update message immediately
        
    def next_frame(self):
        self.frame = (self.frame + 1) % 4  # Cycle through 4 frames
        self.update()  # Trigger a repaint
        
    def check_time(self):
        now = datetime.now().time()
        start = time.fromisoformat(self.settings["work_start"])
        end = time.fromisoformat(self.settings["work_end"])

        if self.away_until is not None and datetime.now() >= self.away_until:
                self.away_message = None
                self.away_until = None
        
        if self.away_message is not None:
            self.message = self.away_message
            return  # Skip further checks if away message is active

        if start <= now < end:
            self.message = self.settings["work_message"]
        else:
            self.message = self.settings["off_message"]
        
    def draw_foot(self, painter, x, y):
        foot = QPainterPath()
        foot.moveTo(x - 2, y - 2)
        foot.lineTo(x - 7, y + 12)
        foot.lineTo(x + 2, y + 9)
        foot.lineTo(x + 8, y + 15)
        foot.lineTo(x + 13, y + 9)
        foot.lineTo(x + 22, y + 12)
        foot.lineTo(x + 3, y - 2)
        foot.closeSubpath()
        painter.drawPath(foot)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        swing = [-12, 0, 12, 0][self.frame]  # Leg swing positions
        
        # Draw the duck's legs based on the current frame
        painter.setPen(QPen(ORANGE, 6, Qt.SolidLine, Qt.RoundCap))  # Orange color for legs
        painter.drawLine(100, 175, 100 + swing, 214)
        painter.drawLine(130, 175, 130 - swing, 214)
        
        # Draw the duck's feet based on the current frame
        painter.setBrush(ORANGE)  # Orange color for feet
        self.draw_foot(painter, 100 + swing, 214)  # Left foot
        self.draw_foot(painter, 130 - swing, 214)  # Right foot
        
        # Draw the duck's tail
        tail = QPainterPath()
        tail.moveTo(85, 93)
        tail.quadTo(55, 98, 26, 82)
        tail.quadTo(28, 130, 42, 160)
        tail.closeSubpath()
        
        # Draw the duck's body and tail as one shape
        body = QPainterPath()
        body.addEllipse(30, 90, 160, 100)  # Body
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(YELLOW)  # Yellow color for body and tail
        painter.drawPath(body.united(tail))  # Combine body and tail shapes

        # Draw the duck's head
        painter.drawEllipse(130, 30, 80, 80)  # Head

        # Draw the duck's beak
        painter.setBrush(ORANGE)  # Orange color
        painter.drawEllipse(200, 60, 35, 18)  # Beak
        
        # Draw the duck's eye
        painter.setBrush(QColor(0, 0, 0))  # Black color
        painter.drawEllipse(171, 51, 14, 14)  # Eye
        
        # Display the message on a pastel white background, flashing with leg movement
        painter.setBrush(PASTEL_WHITE)  # Pastel white for text background
        painter.drawEllipse(72, 108, 68, 68)  # Background for text
        
        # Message, flashing with leg movement
        if self.frame <2:
            painter.setPen(TEXT_COLOR)
            painter.setFont(QFont("Sans", 13, QFont.Bold))
            circle = QRect(72, 108, 68, 68)
            painter.drawText(circle, Qt.AlignCenter | Qt.TextWordWrap, self.message)
    
    def update_mask(self):
        region = QRegion (28, 88, 164, 104, QRegion.Ellipse) # body
        region = region | QRegion(128, 28, 84, 84, QRegion.Ellipse) # head
        region = region | QRegion(198, 58, 40, 22, QRegion.Ellipse) # beak
        region = region | QRegion(78, 165, 90, 70) # Legs and feet
        tail = QPolygon([QPoint(85, 93), QPoint(24, 78), QPoint(20, 128), QPoint(42, 166)])
        region = region | QRegion(tail) # tail
        self.setMask(region)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
    def mouseMoveEvent(self, event):
        if self.drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        make_cute(menu)
        break_action = None
        end_action = None
        lunch_action = {}
        
        if self.away_until is None:
            break_action = menu.addAction("Take A Break")
            lunch_menu = menu.addMenu("Lunch")
            make_cute(lunch_menu)
            for minutes in [10, 15, 30, 60]:
                action = lunch_menu.addAction(f"{minutes} min")
                lunch_action[action] = minutes
        else:
            end_action = menu.addAction("Back To Work")
            
        menu.addSeparator()
        startup_action = menu.addAction("Start At Login")
        startup_action.setCheckable(True)
        startup_action.setChecked(autostart_enabled())
        settings_action = menu.addAction("Settings...")
        quit_action = menu.addAction("Quit")
        
        chosen = menu.exec(event.globalPos())
        if chosen is None:
            return
        
        if chosen == break_action:
            self.start_away(self.settings["break_message"], self.settings["break_minutes"])
        elif chosen in lunch_action:
            self.start_away(self.settings["lunch_message"], lunch_action[chosen])
        elif chosen == end_action:
            self.end_away()
        elif chosen == settings_action:
            self.open_settings()
        elif chosen == quit_action:
            QApplication.quit()
        elif chosen == startup_action:
            autostart_enabled(startup_action.isChecked())
    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.settings = dialog.get_settings()
            save_settings(self.settings)
            self.check_time()  # Update message based on new settings
                    
app = QApplication(sys.argv)
app.setStyle("Fusion")
app.styleHints().setColorScheme(Qt.ColorScheme.Light)
app.setQuitOnLastWindowClosed(False)
duck = Duck()
duck.move(200, 200) # Initial position
duck.show()
sys.exit(app.exec())       