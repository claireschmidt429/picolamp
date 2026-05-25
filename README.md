# Pico W RGB Lamp

## Wiring
| Pico W Pin | Connection |
|------------|------------|
| GP0 (pin 1) | R (Monster PCB) |
| GP1 (pin 2) | G (Monster PCB) |
| GP2 (pin 4) | B (Monster PCB) |
| GND (pin 38) | GND |
| VSYS (pin 39) | Power bank 5V |

Lamp USB-A → power bank USB-A (powers the strip)

## Modes (send via Bluetooth)
| Command | Effect |
|---------|--------|
| MODE:0 | Off |
| MODE:1 | Solid color |
| MODE:2 | Slow fade |
| MODE:3 | Fast fade |
| MODE:4 | Pulse/breathe |
| MODE:5 | Strobe |
| MODE:6 | Rainbow |
| MODE:7 | Brightness cycle |
| BRIGHT:0-100 | Set brightness % |
| SPEED:1-10 | Set speed |
| COLOR:R,G,B | Set solid color (e.g. COLOR:255,0,128) |

## Bluetooth
Device name: **PicoLamp**
Connect with any BLE UART app (e.g. "Serial Bluetooth Terminal" on Android)

## Flash
```bash
bash flash.sh
```
Or tell Claude in VS Code: "run flash.sh"
