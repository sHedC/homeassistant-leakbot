# Leakbot
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]
[![Leakbot Forum][leakbot-forum-shield]][leakbot-forum]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

Stable -
[![GitHub Release][stable-release-shield]][releases]
[![workflow-release]][workflows-release]
[![codecov][codecov-shield]][codecov-link]

Latest -
[![GitHub Release][latest-release-shield]][releases]
[![workflow-lastest]][workflows]
[![issues][issues-shield]][issues-link]

## Please Read

> :warning: **Leakbot Only Allows One Login:**: If you use this integration the token your mobile app is connected to becomes invalid and you get logged out. This happens also if you re-log back into the app it invalidates the token for the integration, however the integration should automatically re-authenticate.

## About the Integration
![leakbot][leakbotimg]

An integration for homeassistant (via HACS) to connect to Leakbot via the leakbot cloud api.

The Water Usage Events sensor does not have a current value, this sensor imports the history which is always 2 days out of date. For each 30 min duration if Leakbot detects water usage the value is incremented by 1, there are a total of 48 detectable units in a day which are recorded as night/ morning/ afternoon and evening.

![][waterusageimg]

Water Usage Events is used only for showing in the history.

NOTES:
- For a new install of the Leakbot device it can take 24 hours before the API will start returning data, before that you will see invalid values.
- The integration updates every four hours at this time, it is not currently changable, it only updates once a day as normal, not sure if a leak forces update.
- There are three sensors: battery status, leak status and leak free days. There is also a device tracker but might remove that as seems pointless.
- Water Usage Events status does not show in the energy dashboard as this requires a volume unit of measure which we do not have.
- Some translation is done as don't know what other options there are, example goodbattery not seen other states to setup.
- Diagnotic download is not yet available.

## Installation
The preferred and easiest way to install this is from the Home Assistant Community Store (HACS).  Follow the link in the badge above for details on HACS.

Go to HACS and integraitons, then select to download Leakbot from HACS.

## Configuration
Go to the Home Assistant UI, go to "Configuration" -> "Integrations" click "+" and search for "Leakbot" follow the configuration screen.

#### Beta Versions
If you want to see Beta versions open the Leakbot in HACS, after download, and click the three dots on the top right and select re-download. Here you will se an option to see beta versions.

#### Debugging
It is possible to show the info and debug logs for the Leakbot integration, to do this you need to enable logging in the configuration.yaml, example below:

Logs do not remove sensitive information so careful what you share, check what you are about to share and blank identifying information.  Note the diagnostic info attempts to redact sensitive information.

```
logger:
  default: warning
  logs:
    # Log for Leakbot
    custom_components.leakbot: info
```

#### Manual Install
To install manually, if you really want to: I won't support this.
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `leakbot`.
4. Download _all_ the files from the `custom_components/leakbot/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Leakbot"

## Development Environment
I have set this up to be able to run development or testing using Visual Studio Code with Docker or Podman in line with the integration blueprint.

To setup just copy the .devcontainer-template.json to .devcontainer.json

If using podman uncomment the section runArgs to avoid permission issues.
Update BUILD_TYPE to "run" to run an instance of Home Assistant and "dev" to do development with pytest.

Debugging in Pythong 3.12 seems slow to startup:
To enable vscode debugging a sample /.vscode/launch.json is:
```
{
  // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
  "version": "0.2.0",
  "configurations": [
    {
      // Example of Debugging Tests.
      "name": "Python: Debug Tests",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "purpose": [
        "debug-test"
      ],
      "console": "integratedTerminal",
      "justMyCode": true,
      "env": {
        "PYTEST_ADDOPTS": "--no-cov"
      }
    },
    {
      // Example of attaching to local debug server
      "name": "Python: Attach Local",
      "type": "debugpy",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "."
        }
      ],
    }
  ]
}
```


## Contributions are welcome!
If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

Or just raise a feature request, would be useful to have a use-case, what system you have and what you want to get done.

***

[waterusageimg]: https://github.com/home-assistant/brands/blob/master/custom_integrations/leakbot/logo.png
[leakbotimg]: https://github.com/home-assistant/brands/blob/master/custom_integrations/leakbot/logo.png
[leakbot]: https://github.com/sHedC/homeassistant-leakbot
[commits-shield]: https://img.shields.io/github/commit-activity/y/sHedC/homeassistant-leakbot?style=for-the-badge
[commits]: https://github.com/shedc/homeassistant-leakbot/commits/main
[license-shield]: https://img.shields.io/github/license/sHedC/homeassistant-leakbot.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Richard%20Holmes%20%40shedc-blue.svg?style=for-the-badge

[buymecoffee]: https://www.buymeacoffee.com/sHedC
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge

[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/

[leakbot-forum-shield]: https://img.shields.io/badge/leakbot-forum-brightgreen.svg?style=for-the-badge
[leakbot-forum]: https://community.home-assistant.io/t/leakbot-integration

[codecov-shield]: https://codecov.io/gh/sHedC/homeassistant-leakbot/branch/main/graph/badge.svg?token=Z7VVO035GY
[codecov-link]: https://codecov.io/gh/sHedC/homeassistant-leakbot

[issues-shield]: https://img.shields.io/github/issues/shedc/homeassistant-leakbot?style=flat
[issues-link]: https://github.com/sHedC/homeassistant-leakbot/issues

[releases]: https://github.com/shedc/homeassistant-leakbot/releases
[stable-release-shield]: https://img.shields.io/github/v/release/shedc/homeassistant-leakbot?style=flat
[latest-release-shield]: https://img.shields.io/github/v/release/shedc/homeassistant-leakbot?include_prereleases&style=flat

[workflows]: https://github.com/sHedC/homeassistant-leakbot/actions/workflows/validate.yml/badge.svg
[workflow-lastest]: https://github.com/sHedC/homeassistant-leakbot/actions/workflows/validate.yml/badge.svg
[workflows-release]: https://github.com/sHedC/homeassistant-leakbot/actions/workflows/release.yml/badge.svg
[workflow-release]: https://github.com/sHedC/homeassistant-leakbot/actions/workflows/release.yml/badge.svg
