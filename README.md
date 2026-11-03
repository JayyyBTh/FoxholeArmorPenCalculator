# FoxholeArmorPenCalculator

Discord bot and C++ CLI for Foxhole vehicle combat maths.

- `/calculate` — shots needed to kill a vehicle and the kill chance after each shot (runs `calc_cli`).
- `/progress` — reads a progress bar's fill percentage from a cropped screenshot (`barlen.py`; also usable standalone: `python barlen.py shot.png`).

The bot reads its token from the `DISCORD_TOKEN` environment variable.

## CLI

```
calc_cli <tankName> <weaponName> <armorFrac> <rangeMeters> <angleDeg> <velocity>
```

Example: `./calc_cli SHT_Ares 68mm 1.0 20 90 1.0`

## Penetration formula

```
P = clamp(penMod * min(S0, max(P0, 1 - armorFrac)) + rangeBonus + angleBonus, 0, 1)
```

- **Range bonus**: `40 × max(0, 1 − (distance + 5) / 40)^1.5` % — +32.74 % at 0 m, 0 at 35 m and beyond. Each metre closer is worth more than the last.
- **Angle bonus**: `40 × cos(angle)` % — +40 % at 0°, 0 at 90°. Here **0° means a shot square to the target's side** and 90° means head-on. The wiki's vehicle pen-chance table labels these the other way round (its 90° is our 0°).

Data lives in `tanks.txt` (`name,health,armor,P0,S0`) and `weapons.txt` (`name,damageHealth,damageArmor,penMod`).

## Build

```
g++ -std=c++17 -O2 main_console.cpp calculator.cpp tanksnshells.cpp -o calc_cli
```

Pushing to `main` builds a Linux `calc_cli` release; `start.sh` downloads the latest one and starts the bot.
