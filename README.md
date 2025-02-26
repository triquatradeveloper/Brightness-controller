# 🌞 Stylish Brightness Controller

A sleek, cross-platform brightness controller built with [Flet](https://flet.dev), [screen_brightness_control](https://github.com/AlJohri/screen_brightness_control), and [pystray](https://github.com/moses-palmer/pystray). This tool lets you easily adjust the brightness of your monitors via a modern popup interface and a system tray icon with a sun motif.

![Sun Icon](https://img.shields.io/badge/Icon-Sun-yellow?style=flat-square)
![Flet](https://img.shields.io/badge/Flet-%23dark-blue?style=flat-square)
![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

---

## ✨ Features

- **Modern UI:** Enjoy a sleek dark-themed interface built with Flet.
- **System Tray Integration:** Minimize to the tray and use a custom sun icon for quick access.
- **Multi-Monitor Support:** Automatically detects multiple monitors and provides independent brightness control.
- **Popup Positioning:** The controller window pops up near the system tray for quick adjustments.
- **Lightweight & Easy to Use:** Minimal dependencies ensure fast startup and smooth operation.

---

## 🚀 Installation

### Prerequisites
- **Python 3.7+**  
- **Windows** (for system tray positioning; other OS may require adjustments)

### Required Packages
Install the necessary dependencies using pip:

```bash
pip install flet screen_brightness_control pystray pillow
