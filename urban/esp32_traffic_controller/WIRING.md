# ESP32 Wiring Guide

## GPIO Pin Layout

The ESP32 pins are arranged to be consecutive and easy to wire:

```
ESP32 Dev Board Layout (Top View)
================================

                [USB Port]

    3V3  [ ]            [ ] GND
    EN   [ ]            [ ] GPIO 23
    VP   [ ]            [ ] GPIO 22
    VN   [ ]            [ ] TX
    GPIO34[ ]           [ ] RX
    GPIO35[ ]           [ ] GPIO 21
    GPIO32[ ]           [ ] GND
    GPIO33[ ]           [ ] GPIO 19
    GPIO25[ ]           [ ] GPIO 18 ◄── Traffic GREEN
    GPIO26[ ]           [ ] GPIO 5  ◄── Traffic YELLOW
    GPIO27[ ]           [ ] GPIO 17
    GPIO14[ ]           [ ] GPIO 16
    GPIO12[ ]           [ ] GPIO 4  ◄── Traffic RED
    GND   [ ]           [ ] GPIO 0
    GPIO13[ ]           [ ] GPIO 2  ◄── Lane Light
    D2   [ ]            [ ] GPIO 15
    D3   [ ]            [ ] D1
    CMD  [ ]            [ ] D0
    5V   [ ]            [ ] CLK
```

## Component Connections

### Lane Light (Road Lighting)
```
ESP32 GPIO 2 ──────[ 220Ω ]───── (+) LED (-) ──── GND
```

### Traffic Light Module

#### Red LED
```
ESP32 GPIO 4 ──────[ 220Ω ]───── (+) Red LED (-) ──── GND
```

#### Yellow LED
```
ESP32 GPIO 5 ──────[ 220Ω ]───── (+) Yellow LED (-) ──── GND
```

#### Green LED
```
ESP32 GPIO 18 ──────[ 220Ω ]───── (+) Green LED (-) ──── GND
```

## Complete Schematic

```
                    ESP32
                  ┌─────────┐
                  │         │
        Lane ─────┤ GPIO 2  │
     (Road Light) │         │
                  │         │
     Traffic ─────┤ GPIO 4  │ (Red)
       Red        │         │
                  │         │
     Traffic ─────┤ GPIO 5  │ (Yellow)
      Yellow      │         │
                  │         │
     Traffic ─────┤ GPIO 18 │ (Green)
      Green       │         │
                  │         │
        GND ──────┤ GND     │
                  └─────────┘

Each LED:
   GPIO ──[ 220Ω resistor ]── LED Anode (+)
                               LED Cathode (-) ── GND
```

## Breadboard Layout

```
   ESP32         Breadboard               LEDs
   ═════         ══════════              ═════

   GPIO 2 ────── Row 1 ─── 220Ω ──── Lane Light
                                            │
   GPIO 4 ────── Row 2 ─── 220Ω ──── Red LED
                                            │
   GPIO 5 ────── Row 3 ─── 220Ω ──── Yellow LED
                                            │
   GPIO 18 ───── Row 4 ─── 220Ω ──── Green LED
                                            │
   GND ───────── Ground Rail ───────────────┘
```

## Parts List

| Qty | Component | Specification |
|-----|-----------|---------------|
| 1 | ESP32 Development Board | Any ESP32 Dev Kit |
| 1 | LED (White/Warm White) | Lane light - 5mm, 20mA |
| 1 | LED (Red) | Traffic light - 5mm, 20mA |
| 1 | LED (Yellow) | Traffic light - 5mm, 20mA |
| 1 | LED (Green) | Traffic light - 5mm, 20mA |
| 4 | Resistor | 220Ω, 1/4W |
| 1 | Breadboard | 830 points (optional) |
| - | Jumper wires | Male-to-Male |
| 1 | USB Cable | Micro-USB or USB-C (depends on ESP32) |

## LED Polarity

**Important:** LEDs are polarized!

```
     LED Symbol:
         │
        ─┤├─  ← Longer leg (Anode +)
         │
         └──  ← Shorter leg (Cathode -)
```

- **Anode (+)**: Longer leg → Connect to GPIO (via resistor)
- **Cathode (-)**: Shorter leg → Connect to GND

## Resistor Calculation

For standard 5mm LEDs at 20mA:

```
R = (Vcc - Vled) / I
R = (3.3V - 2.0V) / 0.02A
R = 65Ω (minimum)
```

**We use 220Ω** for:
- Extra safety margin
- Lower current (~6mA)
- Longer LED lifespan

## Testing Individual Components

Before running the full code, test each LED:

```cpp
void setup() {
  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH);  // Should light up lane light
}
```

Test each GPIO: 2, 4, 5, 18

## Troubleshooting

| Problem | Solution |
|---------|----------|
| LED doesn't light | Check polarity, check resistor, check connection |
| LED very dim | Check resistor value (should be 220Ω) |
| LED very bright/hot | Add/increase resistor value |
| GPIO not working | Try different GPIO, some are restricted |

## Alternative GPIO Options

If you need to use different pins:

**Good alternatives:**
- GPIO 15, 16, 17, 21, 22, 23

**Avoid using:**
- GPIO 6-11 (connected to flash)
- GPIO 0 (boot button)
- GPIO 1, 3 (TX/RX - used for serial)

## Safety Notes

⚠️ **Important:**
- Never exceed 12mA per GPIO pin
- Total current for all GPIOs: 200mA max
- Always use current-limiting resistors
- Don't connect motors/relays directly to GPIO
- For high-power loads, use transistors or relay modules
