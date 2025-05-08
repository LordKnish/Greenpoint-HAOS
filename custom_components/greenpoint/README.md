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

### Setting Up Scenarios

The IGH Compact system requires scenarios to be set up for device control. For each device you want to control, you need to create two scenarios:

1. A scenario named '{device_name} On' to turn the device on
2. A scenario named '{device_name} Off' to turn the device off

For example, if you have a light named 'Living Room Light', you need to create:
- 'Living Room Light On'
- 'Living Room Light Off'

To set up scenarios:
1. In the IGH Compact app, go to Scenarios
2. Click the "+" button to create a new scenario
3. Name the scenario exactly as shown above (including the "On" or "Off" suffix)
4. Configure the scenario to control the appropriate device
5. Save the scenario
6. Repeat for all devices you want to control

Note: The scenario names must match exactly, including spaces and capitalization. The integration will look for scenarios with these exact names when controlling devices.

## Supported Devices 