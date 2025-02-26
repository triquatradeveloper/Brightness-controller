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
        self.page.window.visible = False
        self.page.window.width = 300
        self.page.window.height = 150

        # Get the list of monitors as indices. If list_monitors() returns a list of identifiers,
        # we use its length to generate indices.
        try:
            monitors = sbc.list_monitors()
            self.monitors = list(range(len(monitors)))
        except Exception:
            self.monitors = [0]

        # Create a brightness controller for each monitor using its index
        self.controllers = []
        for i in self.monitors:
            try:
                brightness = sbc.get_brightness(display=i)[0]
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
                on_change=lambda e, idx=i: self.slider_changed(e, idx)
            )
            dial = ft.ProgressRing(
                value=brightness / 100,
                width=50,
                height=50
            )
            self.controllers.append({
                'index': i,
                'text': text,
                'slider': slider,
                'dial': dial
            })

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

    def slider_changed(self, e: ft.ControlEvent, idx: int):
        level = int(e.control.value)
        self.update_brightness(level, idx)

    def update_brightness(self, level: int, idx: int):
        try:
            sbc.set_brightness(level, display=idx)
        except Exception as ex:
            print(f"Error setting brightness on monitor {idx}: {ex}")
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
    center = (size // 2, size // 2)
    radius = 20
    draw.ellipse(
        (center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius),
        fill="yellow"
    )
    for angle in range(0, 360, 45):
        x = center[0] + int(radius * 1.5 * math.cos(math.radians(angle)))
        y = center[1] + int(radius * 1.5 * math.sin(math.radians(angle)))
        draw.line((center, (x, y)), fill="yellow", width=2)
    return image

def run_tray_icon(controller: BrightnessController):
    def on_open(icon, item):
        # Get screen dimensions (Windows-specific)
        try:
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
        except Exception:
            screen_width = 1920
            screen_height = 1080

        controller.page.window.width = 300
        controller.page.window.height = 150
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
    threading.Thread(target=run_tray_icon, args=(controller,), daemon=True).start()

ft.app(target=main)
