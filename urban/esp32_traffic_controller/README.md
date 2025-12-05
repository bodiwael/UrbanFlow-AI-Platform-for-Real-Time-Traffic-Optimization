# ESP32 Traffic Controller with Firebase

ESP32 code that receives commands from Firebase Realtime Database to control lane lights and traffic lights in real-time.

## 🔌 Hardware Setup

### GPIO Pin Configuration

The GPIOs are arranged consecutively on the ESP32 board:

| Function | GPIO Pin | Description |
|----------|----------|-------------|
| **Lane Light** | GPIO 2 | Road/Street lighting (0=OFF, 1=ON) |
| **Traffic Red** | GPIO 4 | Traffic light - Red LED |
| **Traffic Yellow** | GPIO 5 | Traffic light - Yellow LED |
| **Traffic Green** | GPIO 18 | Traffic light - Green LED |

### Wiring Diagram

```
ESP32 Board                      Components
+-----------+
|    GND    |----+
|    GPIO 2 |----|--> Lane Light (+ via 220Ω resistor)
|    GPIO 4 |----|--> Traffic Red LED (+ via 220Ω resistor)
|    GPIO 5 |----|--> Traffic Yellow LED (+ via 220Ω resistor)
|   GPIO 18 |----|--> Traffic Green LED (+ via 220Ω resistor)
+-----------+    |
                 +-> All LED/Light cathodes (-) to GND
```

**Note:** Add 220Ω resistors in series with each LED to limit current.

## 📦 Required Libraries

Install these libraries via Arduino IDE Library Manager:

1. **Firebase ESP Client** by Mobizt
   - Arduino IDE: Tools > Manage Libraries > Search "Firebase ESP Client"
   - Version: 4.3.0 or newer

2. **WiFi** (Built-in with ESP32 board package)

### Install ESP32 Board Support

1. Arduino IDE > File > Preferences
2. Add to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Tools > Board > Boards Manager > Search "ESP32" > Install

## 🔥 Firebase Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add Project"
3. Enter project name (e.g., "UrbanFlowTraffic")
4. Complete the setup wizard

### 2. Enable Realtime Database

1. In Firebase Console, go to **Realtime Database**
2. Click "Create Database"
3. Choose location (closest to your device)
4. Start in **Test Mode** (for development)

### 3. Initialize Database Structure

In Realtime Database, create this structure:

```json
{
  "urban": {
    "lane_light": 0,
    "traffic_light": "O"
  }
}
```

### 4. Get Firebase Credentials

#### API Key:
- Go to: Project Settings > General
- Copy the "Web API Key"

#### Database URL:
- In Realtime Database, click the 📋 icon next to your database URL
- Format: `https://your-project-default-rtdb.firebaseio.com/`

### 5. Create Firebase User

1. Go to **Authentication** > **Sign-in method**
2. Enable "Email/Password"
3. Go to **Users** tab > Click "Add User"
4. Create user (e.g., `esp32@yourproject.com`)
5. Set a secure password

### 6. Set Database Rules (Development)

In Realtime Database > Rules, set:

```json
{
  "rules": {
    ".read": "auth != null",
    ".write": "auth != null"
  }
}
```

**⚠️ For Production:** Implement proper security rules!

## 💻 Arduino IDE Setup

### 1. Open the Project

1. Open `esp32_traffic_controller.ino` in Arduino IDE

### 2. Configure Credentials

At the top of the `.ino` file, replace these values:

```cpp
// WiFi credentials
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// Firebase credentials
#define API_KEY "YOUR_FIREBASE_API_KEY"
#define DATABASE_URL "YOUR_FIREBASE_DATABASE_URL"
#define USER_EMAIL "YOUR_FIREBASE_USER_EMAIL"
#define USER_PASSWORD "YOUR_FIREBASE_USER_PASSWORD"
```

### 3. Select Board and Port

1. Tools > Board > ESP32 Arduino > **ESP32 Dev Module**
2. Tools > Port > Select your ESP32's COM port

### 4. Upload

1. Click **Upload** button
2. Wait for "Done uploading"

### 5. Monitor Serial Output

1. Tools > Serial Monitor
2. Set baud rate to **115200**
3. You should see:
   ```
   === ESP32 Traffic Controller ===
   Setting up GPIOs...
   GPIOs initialized - All lights OFF
   Connecting to WiFi........
   WiFi connected!
   IP address: 192.168.x.x
   Setting up Firebase...
   Firebase connected successfully!
   System ready!
   Listening for commands from Firebase...
   ```

## 🚦 Usage & Testing

### Control Lane Light

Update in Firebase Realtime Database:

```json
"urban/lane_light": 0  // OFF
"urban/lane_light": 1  // ON
```

**Serial Monitor Output:**
```
Lane Light updated: ON
→ Lane Light: ON
```

### Control Traffic Light

Update in Firebase Realtime Database:

```json
"urban/traffic_light": "R"  // Red light
"urban/traffic_light": "Y"  // Yellow light
"urban/traffic_light": "G"  // Green light
"urban/traffic_light": "O"  // All OFF
```

**Serial Monitor Output:**
```
Traffic Light updated: R
→ Traffic Light: RED
```

### Commands Summary

| Command | Database Path | Value | Result |
|---------|---------------|-------|--------|
| Lane Light OFF | `/urban/lane_light` | `0` | GPIO 2 LOW |
| Lane Light ON | `/urban/lane_light` | `1` | GPIO 2 HIGH |
| Red Traffic Light | `/urban/traffic_light` | `"R"` | GPIO 4 HIGH, others LOW |
| Yellow Traffic Light | `/urban/traffic_light` | `"Y"` | GPIO 5 HIGH, others LOW |
| Green Traffic Light | `/urban/traffic_light` | `"G"` | GPIO 18 HIGH, others LOW |
| All Lights OFF | `/urban/traffic_light` | `"O"` | All traffic GPIOs LOW |

### Testing from Firebase Console

1. Go to Realtime Database in Firebase Console
2. Navigate to `urban/lane_light`
3. Click the value and change between `0` and `1`
4. Watch the LED light up on your ESP32!
5. Navigate to `urban/traffic_light`
6. Change between `"R"`, `"Y"`, `"G"`, `"O"`
7. Watch the traffic lights change!

## 🔍 Troubleshooting

### WiFi Connection Failed
- Verify SSID and password are correct
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Check WiFi signal strength

### Firebase Connection Failed
- Verify API Key, Database URL, and user credentials
- Check that Email/Password authentication is enabled
- Ensure database rules allow authenticated users
- Verify internet connection

### LEDs Not Lighting Up
- Check GPIO connections
- Verify LED polarity (long leg = positive)
- Check resistor values (220Ω recommended)
- Use Serial Monitor to confirm commands are received

### Serial Monitor Shows Errors
- Check baud rate is set to 115200
- Look for specific error messages in Firebase output
- Verify database paths exist in Firebase

## 📡 Integration with Your System

To integrate with your traffic optimization platform:

### Using REST API (Python example)

```python
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project-default-rtdb.firebaseio.com/'
})

# Control lane light
ref = db.reference('urban/lane_light')
ref.set(1)  # Turn ON

# Control traffic light
ref = db.reference('urban/traffic_light')
ref.set('R')  # Set to RED
```

### Using Firebase JavaScript SDK

```javascript
import { getDatabase, ref, set } from "firebase/database";

const db = getDatabase();

// Turn on lane light
set(ref(db, 'urban/lane_light'), 1);

// Set traffic light to green
set(ref(db, 'urban/traffic_light'), 'G');
```

## 🛠️ Customization

### Change GPIO Pins

Modify these constants at the top of the `.ino` file:

```cpp
#define LANE_LIGHT_PIN 2
#define TRAFFIC_RED_PIN 4
#define TRAFFIC_YELLOW_PIN 5
#define TRAFFIC_GREEN_PIN 18
```

### Change Firebase Paths

Modify these paths in the code:

```cpp
String laneLightPath = "/urban/lane_light";
String trafficLightPath = "/urban/traffic_light";
```

### Adjust Polling Rate

Change the delay at the end of `loop()`:

```cpp
delay(100);  // Poll every 100ms
```

## 📝 License

This code is part of the UrbanFlow AI Platform for Real-Time Traffic Optimization.

## 🤝 Support

For issues or questions, please check:
- Firebase documentation: https://firebase.google.com/docs
- ESP32 documentation: https://docs.espressif.com/
