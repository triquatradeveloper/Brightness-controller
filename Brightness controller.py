import math
import flet as ft
import screen_brightness_control as sbc
import threading
import pystray
from PIL import Image, ImageDraw
import ctypes

class BrightnessController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Brightness Controller"
        self.page.theme_mode = "dark"
        self.page.bgcolor = "#121212"
        # Start hidden using the new property
        self.page.window.visible = False
        # Set default popup window size (will be adjusted on open)
        self.page.window.width = 300
        self.page.window.height = 150

        # Get available monitors; if error, default to one monitor (0)
        try:
            self.monitors = sbc.list_monitors()
        except Exception:
            self.monitors = [0]

        # Create a brightness control for each monitor
        self.controllers = []  # Each item: dict with monitor, slider, dial, text
        for i, monitor in enumerate(self.monitors):
            try:
                brightness = sbc.get_brightness(display=monitor)[0]
            except Exception:
                brightness = 50
            text = ft.Text(
                value=f"Monitor {i+1}: {brightness}%",
                color="white",
                size=16
            )
            slider = ft.Slider(
                min=0,
                max=100,
                value=brightness,
                on_change=lambda e, m=monitor, idx=i: self.slider_changed(e, m, idx)
            )
            dial = ft.ProgressRing(
                value=brightness / 100,
                width=50,
                height=50
            )
            self.controllers.append({
                'monitor': monitor,
                'text': text,
                'slider': slider,
                'dial': dial
            })

        # Build the UI: one row per monitor plus a Hide button
        controls = []
        for ctrl in self.controllers:
            controls.append(
                ft.Row(
                    [
                        ctrl['text'],
                        ctrl['slider'],
                        ctrl['dial']
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )

        hide_button = ft.ElevatedButton(text="Hide", on_click=self.hide_window)

        self.page.add(
            ft.Column(
                [ft.Text("Brightness Controller", size=24, weight="bold", color="white")]
                + controls +
                [hide_button],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def slider_changed(self, e: ft.ControlEvent, monitor, idx):
        level = int(e.control.value)
        self.update_brightness(level, monitor, idx)

    def update_brightness(self, level: int, monitor, idx):
        try:
            sbc.set_brightness(level, display=monitor)
        except Exception as ex:
            print(f"Error setting brightness on monitor {monitor}: {ex}")
        ctrl = self.controllers[idx]
        ctrl['dial'].value = level / 100
        ctrl['text'].value = f"Monitor {idx+1}: {level}%"
        self.page.update()

    def hide_window(self, e: ft.ControlEvent):
        self.page.window.visible = False
        self.page.update()

def create_image():
    # Create a sun icon image (64x64) with a transparent background.
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Draw a yellow circle (sun)
    center = (size // 2, size // 2)
    radius = 20
    draw.ellipse((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius), fill="yellow")
    # Add rays around the sun
    for angle in range(0, 360, 45):
        x = center[0] + int(radius * 1.5 * math.cos(math.radians(angle)))
        y = center[1] + int(radius * 1.5 * math.sin(math.radians(angle)))
        draw.line((center, (x, y)), fill="yellow", width=2)
    return image

def run_tray_icon(controller: BrightnessController):
    # Callback for the tray icon "Open" menu item.
    def on_open(icon, item):
        # Get screen dimensions using ctypes (Windows-specific)
        try:
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
        except Exception:
            screen_width = 1920
            screen_height = 1080

        # Set window size (if desired, you can adjust these values)
        controller.page.window.width = 300
        controller.page.window.height = 150

        # Position the window near the bottom-right (approximate tray icon location)
        controller.page.window.left = screen_width - controller.page.window.width - 10
        controller.page.window.top = screen_height - controller.page.window.height - 40

        controller.page.window.visible = True
        controller.page.update()

    def on_exit(icon, item):
        icon.stop()
        controller.page.window_close()

    tray_menu = pystray.Menu(
        pystray.MenuItem("Open", on_open, default=True),
        pystray.MenuItem("Exit", on_exit)
    )
    icon = pystray.Icon("brightness_controller", create_image(), "Brightness Controller", tray_menu)
    icon.run()

def main(page: ft.Page):
    controller = BrightnessController(page)
    # Start the system tray icon in a separate thread so it doesn't block the UI
    threading.Thread(target=run_tray_icon, args=(controller,), daemon=True).start()

ft.app(target=main)
