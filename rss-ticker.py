import tkinter as tk
import feedparser
import threading
import time
import itertools
import webbrowser
import json, sys, os
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, QMenu, QAction,
                             QSystemTrayIcon, QStyle, QDialog, QFormLayout, QLineEdit, 
                             QSpinBox, QColorDialog, QFontDialog, QPushButton
                             )
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QCursor, QFont, QColor

def resource_path(relative_path):
    """Get absolute path to resource (works for dev and PyInstaller .exe)."""
    if getattr(sys, 'frozen', False):
        # running in a bundle (.exe)
        base_path = os.path.dirname(sys.executable)
    else:
        # running as script
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

SETTINGS_FILE = resource_path("ticker_settings.json")

RSS_FEEDS = ["https://www.ncaa.com/news/volleyball-women/d1/rss.xml",
             "https://www.mlb.com/mariners/feeds/news/rss.xml",
             "https://www.espn.com/espn/rss/news",
             "https://www.espn.com/espn/rss/mlb/news",
             "https://www.pff.com/feed/teams/29", # Seahawks
             #"https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
             "https://www.espn.com/espn/rss/nfl/news",
             "https://soundofhockey.com/feed/",
             "https://www.mlb.com/feeds/news/rss.xml",
             "https://www.espn.com/espn/rss/soccer/news",
             "https://www.nytimes.com/athletic/rss/nfl/",
             #"https://www.espn.com/espn/rss/ncaa/news",
             "https://www.espn.com/espn/rss/ncf/news",
             # "https://www.ncaa.com/news/football/fbs/rss.xml",
             # "https://www.ncaa.com/news/soccer-men/d1/rss.xml",
             # "https://www.ncaa.com/news/soccer-women/d1/rss.xml",
             #"https://www.ncaa.com/news/tennis-women/d1/rss.xml",
             # "https://www.ncaa.com/news/waterpolo-men/nc/rss.xml",
             # "https://www.ncaa.com/news/ncaa/d1/rss.xml", #NCAA
             "https://www.espn.com/espn/rss/nhl/news",
             ]
SCROLL_SPEED = 10  # ms per movement
STEP = 1            # pixels per step
HEIGHT = 80
FEED_LEN = 10

def save_settings(data):
    """Save settings to file."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "width": 1920,
            "height": 80,
            "font_size": 24,
            "font_color": "#FFFFFF",
            "bg_color": "#000000",
            "font_family": "Arial",
            "scroll_speed": 10,
            "step": 1,
            "feeds": ["https://www.espn.com/espn/rss/news"]
        }

class RSSTicker(tk.Tk):
    def __init__(self, feeds):
        super().__init__()
        self.settings = load_settings()
        save_settings(self.settings)
        self.feeds = itertools.cycle(self.settings['feeds'])
        self.next_feed = None
        self.title("RSS Ticker")
        self.configure(bg="black")
        width = self.settings['width']
        height = self.settings['height']
        self.geometry(f"{width}x{height}+0+0") # width x height + x + y
        self.overrideredirect(True)  # removes window border
        self.attributes("-topmost", True)

        self.canvas = tk.Canvas(self, bg=self.settings["bg_color"], height=HEIGHT, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.text_id = None
        self.feed_text = ""
        self.x_pos = self.settings['width']

        # enable drag-to-move
        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)

        # right-click menu
        self.menu = tk.Menu(self, tearoff=0)
        self.links_menu = tk.Menu(self.menu, tearoff=0)

        self.menu.add_cascade(label="Links", menu=self.links_menu)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.destroy)
        self.bind("<Button-3>", self.show_menu)


        # Resizing state
        self.resizing = False
        self.resizeDir = None
        self.oldPos = None

        # background worker
        # threading.Thread(target=self.load_feed, daemon=True).start()
        self.load_feed()
        self.scroll()

    def load_feed(self):
        try:
            # while True:
            feed = None
            if self.next_feed == None:
                feed = feedparser.parse(next(self.feeds)).entries
            else:
                feed = self.next_feed
            if len(feed) > FEED_LEN:
                self.next_feed = feed[FEED_LEN:]
            else:
                self.next_feed = None
            count = min(len(feed), FEED_LEN)
            titles = "   ★   ".join([entry.title for entry in feed[:count]])
            
            self.update_links_menu(feed)
            self.feed_text = f"   {titles}   "
            if self.text_id:
                self.canvas.delete(self.text_id)
            self.text_id = self.canvas.create_text(
                self.x_pos, self.settings['height']/2, anchor="w",
                text=self.feed_text,
                font=(self.settings['font_family'], self.settings['font_size']),
                fill=self.settings['font_color']
            )
            # time.sleep(REFRESH_INTERVAL)  # refresh every 10 minutes
        except Exception as e:
            # keep the app alive and show an error briefly
            print("load_feed error:", e)

    def show_next_chunk(self):
        if self.text_id:
            try:
                self.canvas.delete(self.text_id)
            except Exception:
                pass

        self.canvas.update_idletasks()
        self.x_pos = self.settings['width']

        self.text_id = self.canvas.create_text(
            self.x_pos, self.settings['height']/2, anchor="w",
            text=text,
            font=(self.settings['font_family'], self.settings['font_size']),
            fill=self.settings['font_color']
        )

    def update_links_menu(self, feed_entries):
        """Rebuild submenu with latest links"""
        self.links_menu.delete(0, "end")
        for entry in feed_entries:
            title = entry.title[:60] + "..." if len(entry.title) > 60 else entry.title
            self.links_menu.add_command(
                label=title,
                command=lambda link=entry.link: webbrowser.open(link)
            )

    def scroll(self):
        try:
            if self.text_id:
                self.canvas.move(self.text_id, -self.settings['step'], 0)

                bbox = self.canvas.bbox(self.text_id)
                # guard against None bbox
                if bbox is None:
                    # not yet ready — try again next tick
                    self.after(self.settings['scroll_speed'], self.scroll)
                    return
                
                x1, _, x2, _ = bbox
                if x2 < 0:
                    '''if self.cindex < len(self.chunks):
                        self.cindex+=1
                    self.text_id = self.chunks[self.cindex]
                    '''
                    # self.canvas.move(self.text_id, 3840 - x1, 0)
                    self.load_feed()
        except Exception as e:
            # defensive: log and try to recover by reloading next feed
            print("scroll error:", e)
            try:
                self.load_feed()
            except Exception as e2:
                print("load_feed during recovery failed:", e2)
        finally:
            self.after(self.settings['scroll_speed'], self.scroll)

      # --- moving logic ---
    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.winfo_pointerx() - self._x
        y = self.winfo_pointery() - self._y
        self.geometry(f"+{x}+{y}")  

    # --- right-click menu ---
    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    # Resize Logic
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # existing right-click menu stuff...
            pass
        elif event.button() == Qt.LeftButton:
            margin = 5
            rect = self.rect()
            if abs(event.x() - rect.right()) <= margin:
                self.resizing = True
                self.resizeDir = "right"
            elif abs(event.y() - rect.bottom()) <= margin:
                self.resizing = True
                self.resizeDir = "bottom"
            elif abs(event.x() - rect.left()) <= margin:
                self.resizing = True
                self.resizeDir = "left"
            elif abs(event.y() - rect.top()) <= margin:
                self.resizing = True
                self.resizeDir = "top"
            else:
                self.oldPos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.resizing:
            if self.resizeDir == "right":
                self.setFixedWidth(event.x())
            elif self.resizeDir == "bottom":
                self.setFixedHeight(event.y())
            elif self.resizeDir == "left":
                geo = self.geometry()
                diff = event.globalX() - geo.x()
                self.setGeometry(geo.x() + diff, geo.y(), geo.width() - diff, geo.height())
            elif self.resizeDir == "top":
                geo = self.geometry()
                diff = event.globalY() - geo.y()
                self.setGeometry(geo.x(), geo.y() + diff, geo.width(), geo.height() - diff)
        elif self.oldPos:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resizeDir = None
        self.oldPos = None

if __name__ == "__main__":
    RSSTicker(RSS_FEEDS).mainloop()