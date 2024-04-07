# Leakbot
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

# [![hacs][hacsbadge]][hacs]
[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

Stable -
[![GitHub Release][stable-release-shield]][releases]
[![workflow-release]][workflows-release]
[![codecov][codecov-shield]][codecov-link]

Latest -
[![GitHub Release][latest-release-shield]][releases]
[![workflow-lastest]][workflows]
[![issues][issues-shield]][issues-link]


> :warning: **Leakbot Not Ready:** Leakbot integraiton is not ready will not work, come back for further updates or watch the forum: https://community.home-assistant.io/t/leakbot-integration/256340/9

## About the Integration
![leakbot][leakbotimg]

An integration for homeassistant (via HACS) to connect to Leakbot via the leakbot cloud api.

NOTES:
- TBC

## Installation
The preferred and easiest way to install this is from the Home Assistant Community Store (HACS).  Follow the link in the badge above for details on HACS.

Go to HACS and integraitons, then select to download Leakbot from HACS.

## Configuration
Go to the Home Assistant UI, go to "Configuration" -> "Integrations" click "+" and search for "Leakbot"
- Select the correct login version, if not sure try online directly to see which server you use.
- Once connected you can change the refresh time in the options

TBC

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

## Example HASS View
TBCDefaultgs to avoid permission issues.
- Update BUILD_TYPE to "run" to run an instance of Home Assistant and "dev" to do development with pytest.

## Contributions are welcome!
If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

Or just raise a feature request, would be useful to have a use-case, what system you have and what you want to get done.

***

[leakbotimg]: https://github.com/sHedC/homeassistant-leakbot/raw/main/leakbot.png
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
