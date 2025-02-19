from miio import Device, DeviceException, DeviceFactory, cloud
import gradio as gr
import os

# Global device storage
DEVICE_STORE = []

# Base controller class
class BaseController:
    @classmethod
    def create(cls, model, ip, token):
        if "xiaomi.light.lamp30" in model:
            return DaluLampController(ip, token)
        elif "huayi" in model.lower():
            return HuayiLampController(ip, token)
        raise ValueError(f"Unsupported device model: {model}")

# Dalu Lamp Controller
class DaluLampController:
    def __init__(self, ip, token):
        self.device = DeviceFactory.create(ip, token)
    
    def toggle(self):
        return self.device.call_action("light_toggle_2_1")
    
    def set_brightness(self, value):
        return self.device.call_action("light_brightness_2_2", [value])
    
    def set_color_temp(self, value):
        return self.device.call_action("light_color_temp_2_3", [value])

# Huayi Lamp Controller
class HuayiLampController(Device):
    def __init__(self, ip, token):
        super().__init__(ip, token)
    
    def toggle(self):
        current = self.get_properties([{"siid": 2, "piid": 1}])[0]["value"]
        return self.send("set_properties", [{"siid": 2, "piid": 1, "value": not current}])
    
    def set_brightness(self, value):
        return self.send("set_properties", [{"siid": 2, "piid": 2, "value": value}])
    
    def set_color_temp(self, value):
        return self.send("set_properties", [{"siid": 2, "piid": 3, "value": value}])

# Query devices
def query_devices(username, password):
    global DEVICE_STORE
    try:
        ci = cloud.CloudInterface(
            username=username,
            password=password,
        )
        devices = ci.get_devices()
        
        formatted = []
        DEVICE_STORE.clear()
        
        for did, dev in devices.items():
            info = {
                "name": dev.name if hasattr(dev, "name") else f"Device {did}",
                "ip": dev.ip if hasattr(dev, "ip") else "N/A",
                "token": dev.token if hasattr(dev, "token") else "N/A",
                "model": dev.model if hasattr(dev, "model") else "Unknown"
            }
            DEVICE_STORE.append(info)
            
            formatted.append(
                f"Name: {info['name']}\n"
                f"Model: {info['model']}\n"
                f"IP: {info['ip']}\n"
                "--------------------------"
            )
        
        choices = [d["name"] for d in DEVICE_STORE]
        return "\n".join(formatted), gr.Dropdown(choices=choices)
    except Exception as e:
        return f"Query failed: {str(e)}"

# Control device
def control_device(device_name, action, value=None):
    device = next((d for d in DEVICE_STORE if d["name"] == device_name), None)
    if not device:
        return "Device not found"
    
    try:
        controller = BaseController.create(device["model"], device["ip"], device["token"])
        
        if action == "toggle":
            controller.toggle()
            return "Toggled switch"
        elif action == "brightness":
            controller.set_brightness(value)
            return f"Brightness set to {value}%"
        elif action == "color_temp":
            controller.set_color_temp(value)
            return f"Color temperature set to {value}K"
        return "Unknown operation"
    except DeviceException as e:
        return f"Device communication failed: {str(e)}"
    except Exception as e:
        return f"Operation failed: {str(e)}"

# Create UI
with gr.Blocks(title="Smart Home Control Center", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🏠 Smart Home Control Center")
    
    with gr.Row():
        # Left panel: Device query
        with gr.Column(scale=1):
            gr.Markdown("## Device Query")
            username = gr.Textbox(label="Xiaomi Account")
            password = gr.Textbox(label="Password", type="password")
            query_btn = gr.Button("Query Devices", variant="primary")
            query_result = gr.Textbox(label="Query Results", lines=10)
        
        # Right panel: Device control
        with gr.Column(scale=2):
            gr.Markdown("## Device Control")
            device_selector = gr.Dropdown(label="Select Device")
            
            with gr.Row():
                toggle_btn = gr.Button("🔘 Toggle Switch")
                brightness_slider = gr.Slider(1, 100, step=1, label="Brightness (%)")
                temp_slider = gr.Slider(3000, 6400, step=100, label="Color Temperature (K)")
            
            control_output = gr.Textbox(label="Operation Feedback")

    # Event bindings
    query_btn.click(
        query_devices,
        [username, password],
        [query_result, device_selector]
    )
    
    toggle_btn.click(
        lambda name: control_device(name, "toggle"),
        [device_selector],
        [control_output]
    )
    
    brightness_slider.change(
        lambda val, name: control_device(name, "brightness", val),
        [brightness_slider, device_selector],
        [control_output]
    )
    
    temp_slider.change(
        lambda val, name: control_device(name, "color_temp", val),
        [temp_slider, device_selector],
        [control_output]
    )

if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860, share=True)