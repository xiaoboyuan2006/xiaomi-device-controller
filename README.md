# xiaomi-device-controller

## Overview

The **xiaomi-device-controller** is a Python-based application that allows you to control Xiaomi smart home devices using the `miio` library. The application provides a user-friendly interface built with Gradio, enabling you to query connected devices and control their settings such as brightness, color temperature, and power state.

## Features

- **Device Query**: Query all Xiaomi smart home devices connected to your account.
- **Device Control**: Control devices by toggling their power, adjusting brightness, and setting color temperature.
- **User-Friendly Interface**: Built with Gradio, the interface is intuitive and easy to use.
- **Extensible**: Supports multiple device models and can be extended to support more.

## Supported Devices

- **Dalu Lamp**: Model `xiaomi.light.lamp30`
- **Huayi Lamp**: Model containing `huayi` in its name

## Installation

### Prerequisites

- Python 3.7 or higher
- `miio` library
- `gradio` library

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/smart-home-control-center.git
   cd smart-home-control-center
