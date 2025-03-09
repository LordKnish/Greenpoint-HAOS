# GitHub Repository Setup for HACS Validation

To pass the HACS validation checks, you need to make the following changes to your GitHub repository:

## 1. Add Repository Description

1. Go to your GitHub repository: https://github.com/LordKnish/Greenpoint-HAOS
2. Click on the "Settings" tab
3. In the "General" section, find the "Description" field
4. Add a description for your repository, for example:
   ```
   Home Assistant integration for Greenpoint IGH Compact devices - control and monitor your smart home devices
   ```
5. Click "Save changes"

## 2. Add Repository Topics

1. Go to your GitHub repository: https://github.com/LordKnish/Greenpoint-HAOS
2. On the right side of the repository page, find the "About" section
3. Click on the gear icon (⚙️) to edit
4. In the "Topics" field, add the following topics:
   ```
   home-assistant, homeassistant, hacs, integration, greenpoint, igh-compact
   ```
5. Click "Save changes"

## 3. Add to Brands Repository (Optional)

For the "brands" check to pass, you need to add your custom domain to the Home Assistant brands repository:

1. Fork the [Home Assistant brands repository](https://github.com/home-assistant/brands)
2. Add your brand files to the appropriate directories:
   - Add a logo to `custom_integrations/greenpoint/icon.png` (256x256px)
   - Add a logo to `custom_integrations/greenpoint/logo.png` (512x512px)
3. Create a pull request to the Home Assistant brands repository

Note: This step is optional for HACS, but it will improve the appearance of your integration in Home Assistant.

## After Making These Changes

After making these changes, the HACS validation should pass successfully. You can re-run the validation workflow in your GitHub repository to verify.
