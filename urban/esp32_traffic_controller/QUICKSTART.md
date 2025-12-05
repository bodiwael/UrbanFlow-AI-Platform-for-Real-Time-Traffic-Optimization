# Quick Start Guide

## 1️⃣ Hardware (5 minutes)

Connect to ESP32:
```
GND     → All LED cathodes (-)
GPIO 2  → Lane Light (+) via 220Ω resistor
GPIO 4  → Red LED (+) via 220Ω resistor
GPIO 5  → Yellow LED (+) via 220Ω resistor
GPIO 18 → Green LED (+) via 220Ω resistor
```

## 2️⃣ Software (10 minutes)

### Install Arduino IDE
1. Download from https://www.arduino.cc/en/software
2. Install ESP32 board support
3. Install "Firebase ESP Client" library (by Mobizt)

### Setup Firebase
1. Create project at https://console.firebase.google.com/
2. Enable Realtime Database
3. Enable Email/Password authentication
4. Create a user (e.g., esp32@project.com)
5. Add this data structure:
```json
{
  "urban": {
    "lane_light": 0,
    "traffic_light": "O"
  }
}
```

## 3️⃣ Configure Code (2 minutes)

Edit `esp32_traffic_controller.ino`:

```cpp
#define WIFI_SSID "YourWiFi"
#define WIFI_PASSWORD "YourPassword"
#define API_KEY "Your-Firebase-API-Key"
#define DATABASE_URL "https://your-project.firebaseio.com/"
#define USER_EMAIL "esp32@project.com"
#define USER_PASSWORD "your-password"
```

## 4️⃣ Upload & Test (3 minutes)

1. Connect ESP32 via USB
2. Select: Tools > Board > ESP32 Dev Module
3. Select your COM port
4. Click Upload ⬆️
5. Open Serial Monitor (115200 baud)

## 5️⃣ Control It! (1 minute)

In Firebase Console:

**Turn on lane light:**
- Change `urban/lane_light` to `1`

**Change traffic light to RED:**
- Change `urban/traffic_light` to `"R"`

**Other commands:**
- `"Y"` = Yellow
- `"G"` = Green
- `"O"` = Off

## ✅ Expected Output

Serial Monitor should show:
```
=== ESP32 Traffic Controller ===
WiFi connected!
Firebase connected successfully!
System ready!
Lane Light updated: ON
→ Lane Light: ON
Traffic Light updated: R
→ Traffic Light: RED
```

## 🆘 Common Issues

| Problem | Solution |
|---------|----------|
| WiFi won't connect | Check SSID/password, use 2.4GHz WiFi |
| Firebase error | Verify API key and database URL |
| LEDs don't light | Check wiring and resistors (220Ω) |
| Upload failed | Select correct COM port, press BOOT button during upload |

## 📚 Need More Help?

See the full README.md for detailed instructions!
