# Greenpoint IGH Compact Integration for Home Assistant

<p align="center">
  <img src="custom_components/greenpoint/icons/logo.png" alt="Greenpoint Logo" width="600"/>
</p>

This is a custom integration for Home Assistant that allows you to control and monitor your Greenpoint IGH Compact devices.

## Features

- Auto-discovery of all devices in your Greenpoint system
- Device categorization into appropriate entity types (sensors, switches, lights)
- Real-time updates of device states
- Control capabilities through Home Assistant UI
- Scenario support for device control

## Installation

### HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Add this repository as a custom repository in HACS:
   - Go to HACS > Integrations
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add the URL of this repository
   - Select "Integration" as the category
3. Click "Install" on the Greenpoint IGH Compact integration
4. Restart Home Assistant

### Manual Installation

1. Download the latest release from the GitHub repository
2. Extract the `custom_components/greenpoint` directory to your Home Assistant `custom_components` directory
3. Restart Home Assistant

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

This integration supports all devices that can be controlled through the IGH Compact API:

- Temperature sensors
- Motion sensors
- Switches
- Lights

## Troubleshooting

### Common Issues

- **Cannot connect to API**: Make sure your server IP is correct and that Home Assistant can reach it
- **Invalid authentication**: Check that your API token is correct
- **Devices not showing up**: Make sure your devices are properly set up in the IGH Compact app

### Logs

To get more detailed logs, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.greenpoint: debug
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
