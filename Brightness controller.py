import flet as ft
import screen_brightness_control as sbc
import threading
import pystray
from PIL import Image, ImageDraw

class BrightnessController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Stylish Brightness Controller"
        self.page.theme_mode = "dark"
        self.page.bgcolor = "#121212"
        # Start hidden in the background
        self.page.window_visible = False

        # Try to get the current brightness; if fails, fallback to 50
        try:
            self.brightness = sbc.get_brightness(display=0)[0]
        except Exception:
            self.brightness = 50

        # Notification text for brightness percentage
        self.brightness_text = ft.Text(
            value=f"Brightness: {self.brightness}%",
            color="white",
            size=16
        )

        # Brightness Slider; on_change passes an event containing the new value
        self.slider = ft.Slider(
            min=0,
            max=100,
            value=self.brightness,
            on_change=self.slider_changed
        )

        # Dial visual feedback using ProgressRing
        self.dial = ft.ProgressRing(
            value=self.brightness / 100,
            width=100,
            height=100
        )

        # Preset Buttons for quick brightness settings
        self.presets = {
            "Reading": 70,
            "Night": 30,
            "Gaming": 90,
            "Movie": 50
        }
        self.preset_buttons = [
            ft.ElevatedButton(text=mode, on_click=lambda e, m=mode: self.set_preset(m))
            for mode in self.presets
        ]

        # Battery Saver Mode Switch (sets brightness to 20 when on)
        self.battery_mode = ft.Switch(
            label="Battery Saver Mode",
            on_change=self.battery_saver
        )

        # Multi-Monitor Dropdown for selecting which monitor to adjust
        monitors = sbc.list_monitors()
        self.monitor_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(str(m)) for m in monitors],
            value=str(monitors[0]) if monitors else "0",
            on_change=self.monitor_changed,
            width=150
        )

        # Layout: Added a "Hide" button to let the user hide the window again
        self.page.add(
            ft.Column(
                [
                    ft.Text("Brightness Controller", size=24, weight="bold", color="white"),
                    self.brightness_text,
                    self.slider,
                    self.dial,
                    ft.Row(self.preset_buttons, alignment=ft.MainAxisAlignment.CENTER),
                    self.battery_mode,
                    ft.Row(
                        [ft.Text("Select Monitor:", color="white"), self.monitor_dropdown],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.ElevatedButton(text="Hide", on_click=self.hide_window)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        # Setup keyboard shortcuts: Ctrl+ArrowUp and Ctrl+ArrowDown
        self.page.on_keyboard_event = self.handle_keyboard_event

    def slider_changed(self, e: ft.ControlEvent):
        level = int(e.control.value)
        self.update_brightness(level)

    def update_brightness(self, level: int):
        monitor = self.monitor_dropdown.value
        try:
            sbc.set_brightness(level, display=monitor)
        except Exception as ex:
            print(f"Error setting brightness: {ex}")
        self.dial.value = level / 100
        self.brightness_text.value = f"Brightness: {level}%"
        self.page.update()

    def set_preset(self, mode):
        level = self.presets[mode]
        self.slider.value = level
        self.update_brightness(level)

    def battery_saver(self, e: ft.ControlEvent):
        if e.control.value:
            self.slider.value = 20
            self.update_brightness(20)
        else:
            # When battery saver is turned off, reset to a default value (e.g., 50)
            self.slider.value = 50
            self.update_brightness(50)

    def monitor_changed(self, e: ft.ControlEvent):
        # When the monitor selection changes, update brightness on the new monitor
        self.update_brightness(int(self.slider.value))

    def handle_keyboard_event(self, e: ft.KeyboardEvent):
        if e.key == "ArrowUp" and e.ctrl:
            new_value = min(100, int(self.slider.value) + 5)
            self.slider.value = new_value
            self.update_brightness(new_value)
        elif e.key == "ArrowDown" and e.ctrl:
            new_value = max(0, int(self.slider.value) - 5)
            self.slider.value = new_value
            self.update_brightness(new_value)

    def hide_window(self, e: ft.ControlEvent):
        self.page.window_visible = False
        self.page.update()

def create_image():
    # Create a simple icon image (64x64) for the system tray
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), "black")
    draw = ImageDraw.Draw(image)
    # Draw a simple white rectangle (you can customize this as needed)
    draw.rectangle((0, 0, width, height), fill="white")
    return image

def run_tray_icon(controller: BrightnessController):
    # Callback to show the window when "Open" is clicked in the tray
    def on_open(icon, item):
        controller.page.window_visible = True
        controller.page.update()
    # Callback to exit the app when "Exit" is clicked
    def on_exit(icon, item):
        icon.stop()
        # Close the Flet app; this may vary depending on your deployment
        controller.page.window_close()
    tray_menu = pystray.Menu(
        pystray.MenuItem("Open", on_open),
        pystray.MenuItem("Exit", on_exit)
    )
    icon = pystray.Icon("brightness_controller", create_image(), "Brightness Controller", tray_menu)
    icon.run()

def main(page: ft.Page):
    controller = BrightnessController(page)
    # Start the system tray icon in a separate thread
    threading.Thread(target=run_tray_icon, args=(controller,), daemon=True).start()

ft.app(target=main)
