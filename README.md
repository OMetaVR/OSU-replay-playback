# OSU Replay Player

A simple, Python-based osu! replay player with basic mod support.

## Description

This project is a proof-of-concept experiment to create a functional osu! replay player within a limited timeframe (under an hour). It demonstrates the ability to parse and play osu! replay files (.osr) along with their corresponding beatmaps, including support for various game mods.

**Note**: This is an experimental project created as a rapid prototype. It contains many bugs, is not optimized, and will not be actively maintained. Use at your own risk and for educational purposes only.

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Dependencies](#dependencies)
5. [Known Issues](#known-issues)
6. [Disclaimer](#disclaimer)

## Features

- Load and parse .osr replay files
- Automatic beatmap finding based on replay hash
- Basic mod support, including:
  - Easy (EZ)
  - Hard Rock (HR)
  - Hidden (HD)
  - Double Time (DT) / Nightcore (NC)
  - Half Time (HT)
  - Flashlight (FL)
  - Mirror (MR)
- Simple GUI replay playback using Pygame
- Debug information display during playback
- Beatmap caching for faster loading

## Installation

1. Clone this repository
2. Install the required dependencies (see [Dependencies](#dependencies))
3. Run `python osr_player.py`

## Usage

1. Run the script
2. Select a replay file from your osu! replays folder
3. The player will attempt to find the corresponding beatmap
4. Watch the replay playback in the Pygame window

Controls:
- DELETE: Pause/Resume playback
- ESC: Stop playback and close the window

## Dependencies

- Python 3.7+
- pygame
- osrparse
- fuzzywuzzy

Install dependencies using pip:

```
pip install pygame osrparse fuzzywuzzy
```

## Known Issues

- Timing may not be 100% accurate
- Some mod effects may not be perfectly implemented
- Sliders and spinners are not fully supported
- Performance may be suboptimal for longer replays

## Disclaimer

This project is not affiliated with or endorsed by osu! or ppy Pty Ltd. It is an unofficial, fan-made tool created for educational and experimental purposes only. Use of this tool may violate the osu! terms of service. Use at your own risk.
