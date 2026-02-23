import subprocess
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivymd.uix.dialog import MDDialog
import psutil
import os
import sys
from threading import Thread
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty
import ctypes

Window.size = (430, 330)
kv = """
MDScreen:
    HomeScreen:
        name: "home"

<HomeScreen>:
    MDTextField:
        id: detected_drive
        hint_text: "Detected Drive"
        text: "See Detected_drive here!"
        y: root.height * 0.30
        readonly: True
        size_hint_x: 0.8
        pos_hint: {"x": 0.03, "y": 0.28}
    
    Image:
        id: img
        allow_stretch: True
        keep_ratio: True
        size_hint: 0.46, 0.50
        pos_hint: {"center_x": 0.75, "center_y": 0.50}

    Widget:
        y:root.height * 0.73
        canvas.before:
            Color:
                rgba: 0.7, 0.7, 0.7, 3
            Rectangle:
                pos: self.pos
                size: self.size

    Widget:
        size_hint_y: None
        height: "70dp"
        y: 0 

        canvas.before:
            Color:
                rgba: 0.7, 0.7, 0.7, 5
            Rectangle:
                pos: self.pos
                size: self.size

    MDProgressBar:
        id: P_Bar
        value: 100
        size_hint_x: 0.44
        size_hint_y: 0.1
        y: root.height * 0.60 
        pos_hint: {"x": 0.03, "y": 0.60}
        
    MDLabel:
        id: move_text
        text: "insert your usb drive to recover deleted files"
        size_hint: 0.9, 0.5
        theme_text_color: "Custom"
        text_color: 0.05, 0.1, 0.3, 1 
        bold: True

    MDRaisedButton:
        id: refresh
        text: "Refresh"
        size_hint: 0.20, 0.10
        pos_hint: {"center_x": 0.13, "center_y": 0.5}
        on_release: root.refresh_drive()

    MDRaisedButton:
        id: recover_btn
        text: "start"
        size_hint: 0.20, 0.10
        pos_hint: {"center_x": 0.37, "center_y": 0.5}
        on_release: root.start_recovery()

    MDFlatButton:
        id: about_dev
        text: "About Developer"
        size_hint: 0.20, 0.10
        pos_hint: {"x": 0.10, "y": 0.24}
        on_release: root.about_dev()
        

"""

def get_resource_path(relative_path):
        try:
            base_path = sys._MEIPASS 
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

Window.set_icon(get_resource_path("icon.png"))

class HomeScreen(MDScreen):
    images = ListProperty([])
    index = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.images = [
            get_resource_path("insert2.JPG"),
            get_resource_path("insert1.JPG")
        ]
        Clock.schedule_once(self.text_amination, 1)
        self.dialog = None
        Clock.schedule_once(self.auto_detect)

    def on_kv_post(self, base_widget):
        self.ids.img.source = self.images[self.index]
        Clock.schedule_interval(self.change_image, 5)


    def change_image(self, dt):
        self.index = (self.index + 1) % len(self.images)
        self.ids.img.source = self.images[self.index]

    
    def text_amination(self, dt):
        self.label = self.ids.move_text
        self.label.x = self.width
        Clock.schedule_interval(self.move_text, 1/60)

    def move_text(self, dt):
        speed = 100
        self.label.x -= speed * dt  
        if self.label.right < 0:
            self.label.x = self.width
            
    @mainthread
    def show_dialog(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title = title,
            text = text,
            size_hint = (0.9, None),
            buttons = [MDFlatButton(text="ok", on_release = lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()
    
    def detect_drive(self):
        drive = []
        for part in psutil.disk_partitions(all = False):
            if "removable" in part.opts or "/media" in part.mountpoint or "usb" in part.device.lower():
                drive.append(part.device if os.name != "nt" else part.mountpoint)
            self.ids.detected_drive.text = drive[0] if drive else "No drive detected"
    
    def refresh_drive(self):
        self.detect_drive()
        self.show_dialog("Info", "Program refreshes successfully.")


    def auto_detect(self, dt):
        self.detect_drive()

    def recover_drive(self, device):
        try:
            base_dir = os.path.dirname(sys.executable)
            photorec_path = os.path.join(base_dir, "tools", "photorec_win.exe")

            if not os.path.exists(photorec_path):
                self.show_dialog("Error", f"PhotoRec not found:\n{photorec_path}")
                return

            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                photorec_path,
                None,
                None,
                1
            )

            self.show_dialog(
                "Info",
                "PhotoRec started successfully."
            )

        except Exception as e:
            self.show_dialog("Error", str(e))

        finally:
            self.ids.recover_btn.disabled = False

    def start_recovery(self):
        detected = self.ids.detected_drive.text.strip()
        if not detected or detected == "No drive detected":
            self.show_dialog("No drive", "No USB drive detected. Connect a drive and press Refresh.")
            return

        self.ids.recover_btn.disabled = True
        Thread(target=self.recover_drive, args=(detected,), daemon=True).start()

    def about_dev(self):
        self.show_dialog(
            "About Developer", 
            "This application was developed by Joseph Aiah Gbonia, a passionate software developer\n"
            "dedicated to creating smart, reliable, and user-friendly digital solutions. With a strong\n"
            "focus on innovation and efficiency.\n\n "
            "Email: josephgbonia123@gmail.com\n"
            " Phone: +232-79-17-47-63/+232-77-78-86-51"
        )

class MDApp(MDApp):
    def build(self):
        self.title = "USB Recovery Tool"
        self.icon = get_resource_path("icon.ico")
        return Builder.load_string(kv)
MDApp().run()