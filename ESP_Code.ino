#include <WiFi.h>
#include <FirebaseESP32.h>

// ===== WiFi Credentials =====
#define WIFI_SSID "Urban"
#define WIFI_PASSWORD "urban1234"

// ===== Firebase Configuration =====
#define FIREBASE_HOST "https://stem-53cdc-default-rtdb.firebaseio.com/"
#define FIREBASE_AUTH "UlqdAaYSCRjTcqFBRVW0df1Y513SLgoJ2vuZ2lZO"

// ===== GPIO Pins =====
#define LANE_LIGHT_PIN 2       // Single light
#define TRAFFIC_RED_PIN 4      // Traffic lights
#define TRAFFIC_YELLOW_PIN 5
#define TRAFFIC_GREEN_PIN 18

// Firebase object
FirebaseData firebaseData;

// Current states
int currentLaneState = -1;
String currentTrafficState = "";

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== ESP32 Simple Traffic Controller ===");

  // Setup GPIO pins
  pinMode(LANE_LIGHT_PIN, OUTPUT);
  pinMode(TRAFFIC_RED_PIN, OUTPUT);
  pinMode(TRAFFIC_YELLOW_PIN, OUTPUT);
  pinMode(TRAFFIC_GREEN_PIN, OUTPUT);

  // Initialize all LOW
  digitalWrite(LANE_LIGHT_PIN, LOW);
  digitalWrite(TRAFFIC_RED_PIN, LOW);
  digitalWrite(TRAFFIC_YELLOW_PIN, LOW);
  digitalWrite(TRAFFIC_GREEN_PIN, LOW);

  Serial.println("GPIOs initialized - All LOW");

  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Connect to Firebase
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);

  Serial.println("Firebase connected!");
  Serial.println("Ready!\n");
}

void loop() {
  // Read lane light command (single GPIO)
  if (Firebase.getInt(firebaseData, "/lane_light")) {
    int laneState = firebaseData.intData();

    if (laneState != currentLaneState) {
      currentLaneState = laneState;

      if (laneState == 1) {
        digitalWrite(LANE_LIGHT_PIN, HIGH);
        Serial.println("Lane Light: HIGH");
      } else {
        digitalWrite(LANE_LIGHT_PIN, LOW);
        Serial.println("Lane Light: LOW");
      }
    }
  }

  // Read traffic lights command (3 GPIOs)
  if (Firebase.getString(firebaseData, "/traffic_lights")) {
    String trafficState = firebaseData.stringData();

    if (trafficState != currentTrafficState && trafficState.length() >= 3) {
      currentTrafficState = trafficState;

      // Set each GPIO based on command string
      // Format: "RYG" where each is '0' or '1'
      digitalWrite(TRAFFIC_RED_PIN, trafficState.charAt(0) == '1' ? HIGH : LOW);
      digitalWrite(TRAFFIC_YELLOW_PIN, trafficState.charAt(1) == '1' ? HIGH : LOW);
      digitalWrite(TRAFFIC_GREEN_PIN, trafficState.charAt(2) == '1' ? HIGH : LOW);

      Serial.print("Traffic Lights: ");
      Serial.print(trafficState.charAt(0) == '1' ? "RED " : "--- ");
      Serial.print(trafficState.charAt(1) == '1' ? "YELLOW " : "--- ");
      Serial.println(trafficState.charAt(2) == '1' ? "GREEN" : "---");
    }
  }

  delay(500);  // Check every 500ms
}
