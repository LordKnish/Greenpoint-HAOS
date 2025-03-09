# Greenpoint Logo

Place the Greenpoint logo files in this directory:

1. `icon.png` - A square PNG logo (recommended size: 256x256 pixels)
2. `logo.png` - A rectangular logo for documentation (recommended size: 600x200 pixels)

These logos will be used in the Home Assistant UI and documentation.

## Requirements

- The logo should be in PNG format with a transparent background
- The icon should be square and recognizable at small sizes
- The logo should follow the Greenpoint brand guidelines

## Usage

Once the logo files are added, update the `manifest.json` file to include the icon:

```json
{
  "domain": "greenpoint",
  "name": "Greenpoint IGH Compact",
  "documentation": "https://github.com/username/ha-greenpoint",
  "issue_tracker": "https://github.com/username/ha-greenpoint/issues",
  "dependencies": [],
  "config_flow": true,
  "codeowners": ["@username"],
  "requirements": ["aiohttp>=3.8.1"],
  "iot_class": "local_polling",
  "version": "0.1.0",
  "icon": "mdi:home-automation"
}
```

Replace `"icon": "mdi:home-automation"` with the path to your icon if you want to use a custom icon instead of a Material Design icon.
