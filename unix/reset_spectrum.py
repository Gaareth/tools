#!/usr/bin/python
from openrazer.client import DeviceManager

device_manager = DeviceManager()

def reset_brightness():
    value=100
    for device in device_manager.devices:
        if device.type == "mouse":
            device.fx.misc.logo.brightness = int(value)
            device.fx.misc.scroll_wheel.brightness = int(value)
        else:
            device.brightness = int(value)

def reset_fx():
    for device in device_manager.devices:
        if device.type == "mouse":
            device.fx.misc.logo.spectrum()
        else:
            device.fx.spectrum()

if __name__ == "__main__":
    print("> Reset Spectrum")
    reset_fx()
    reset_brightness()