# Greenpoint IGH Compact Integration

<p align="center">
  <img src="custom_components/greenpoint/icons/logo.png" alt="Greenpoint Logo" width="600"/>
</p>

This integration allows you to control and monitor your Greenpoint IGH Compact devices in Home Assistant.

## Features

- Auto-discovery of all devices in your Greenpoint system
- Device categorization into appropriate entity types (sensors, switches, lights)
- Real-time updates of device states
- Control capabilities through Home Assistant UI
- Scenario support for device control

## Configuration

1. Go to Configuration > Integrations
2. Click the "+ Add Integration" button
3. Search for "Greenpoint IGH Compact"
4. Enter your server IP and API token

### Getting Your API Token

1. Inside the IGH Compact app, on the left upper bar, click the menu icon and navigate to Manage Users
2. On the tabs on the top center, navigate to Api Keys
3. Click the plus icon on the top right and a new key is created
4. Copy the key and use it as the token parameter

## Supported Devices

- Temperature sensors
- Motion sensors
- Switches
- Lights
