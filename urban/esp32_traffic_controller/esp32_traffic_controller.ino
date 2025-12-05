/*
 * ESP32 Traffic Controller with Firebase
 *
 * Controls:
 * - Lane Light (Road Lighting): GPIO 2
 * - Traffic Red Light: GPIO 4
 * - Traffic Yellow Light: GPIO 5
 * - Traffic Green Light: GPIO 18
 *
 * Firebase Commands:
 * - urban/lane_light: 0 (off) or 1 (on)
 * - urban/traffic_light: 'R' (Red), 'Y' (Yellow), 'G' (Green), 'O' (Off)
 */

#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

// WiFi credentials
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// Firebase credentials
#define API_KEY "YOUR_FIREBASE_API_KEY"
#define DATABASE_URL "YOUR_FIREBASE_DATABASE_URL"  // e.g., "https://your-project.firebaseio.com/"
#define USER_EMAIL "YOUR_FIREBASE_USER_EMAIL"
#define USER_PASSWORD "YOUR_FIREBASE_USER_PASSWORD"

// GPIO Pin Definitions (consecutive pins)
#define LANE_LIGHT_PIN 2      // Road lighting
#define TRAFFIC_RED_PIN 4     // Traffic light - Red
#define TRAFFIC_YELLOW_PIN 5  // Traffic light - Yellow
#define TRAFFIC_GREEN_PIN 18  // Traffic light - Green

// Firebase objects
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// Firebase database paths
String laneLightPath = "/urban/lane_light";
String trafficLightPath = "/urban/traffic_light";

// Variables
unsigned long sendDataPrevMillis = 0;
bool signupOK = false;
int currentLaneState = 0;
char currentTrafficState = 'O';

// Function prototypes
void connectWiFi();
void setupFirebase();
void setupGPIOs();
void setLaneLight(int state);
void setTrafficLight(char state);
void listenFirebase();

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== ESP32 Traffic Controller ===");

  // Setup GPIOs
  setupGPIOs();

  // Connect to WiFi
  connectWiFi();

  // Setup Firebase
  setupFirebase();

  Serial.println("System ready!");
  Serial.println("Listening for commands from Firebase...\n");
}

void loop() {
  if (Firebase.ready() && signupOK) {
    listenFirebase();
  }

  delay(100);  // Small delay to prevent excessive polling
}

void setupGPIOs() {
  Serial.println("Setting up GPIOs...");

  // Configure pins as outputs
  pinMode(LANE_LIGHT_PIN, OUTPUT);
  pinMode(TRAFFIC_RED_PIN, OUTPUT);
  pinMode(TRAFFIC_YELLOW_PIN, OUTPUT);
  pinMode(TRAFFIC_GREEN_PIN, OUTPUT);

  // Initialize all lights to OFF
  digitalWrite(LANE_LIGHT_PIN, LOW);
  digitalWrite(TRAFFIC_RED_PIN, LOW);
  digitalWrite(TRAFFIC_YELLOW_PIN, LOW);
  digitalWrite(TRAFFIC_GREEN_PIN, LOW);

  Serial.println("GPIOs initialized - All lights OFF");
}

void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed!");
    Serial.println("Please check credentials and restart.");
    while(1) delay(1000);
  }
}

void setupFirebase() {
  Serial.println("Setting up Firebase...");

  // Assign the API key
  config.api_key = API_KEY;

  // Assign the user sign in credentials
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  // Assign the RTDB URL
  config.database_url = DATABASE_URL;

  // Assign the callback function for the long running token generation task
  config.token_status_callback = tokenStatusCallback;

  // Initialize Firebase
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  // Wait for authentication
  Serial.print("Authenticating with Firebase");
  int attempts = 0;
  while (!Firebase.ready() && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (Firebase.ready()) {
    Serial.println("\nFirebase connected successfully!");
    signupOK = true;

    // Initialize database paths if they don't exist
    Firebase.RTDB.setInt(&fbdo, laneLightPath.c_str(), 0);
    Firebase.RTDB.setString(&fbdo, trafficLightPath.c_str(), "O");
  } else {
    Serial.println("\nFirebase connection failed!");
    Serial.println("Please check credentials and restart.");
    while(1) delay(1000);
  }
}

void listenFirebase() {
  // Read lane light status
  if (Firebase.RTDB.getInt(&fbdo, laneLightPath.c_str())) {
    if (fbdo.dataType() == "int") {
      int laneState = fbdo.intData();

      // Only update if state changed
      if (laneState != currentLaneState) {
        currentLaneState = laneState;
        setLaneLight(laneState);
        Serial.print("Lane Light updated: ");
        Serial.println(laneState ? "ON" : "OFF");
      }
    }
  } else {
    Serial.println("Failed to read lane light data");
    Serial.println("Reason: " + fbdo.errorReason());
  }

  // Read traffic light status
  if (Firebase.RTDB.getString(&fbdo, trafficLightPath.c_str())) {
    if (fbdo.dataType() == "string") {
      String trafficState = fbdo.stringData();
      char state = trafficState.charAt(0);

      // Only update if state changed
      if (state != currentTrafficState) {
        currentTrafficState = state;
        setTrafficLight(state);
        Serial.print("Traffic Light updated: ");
        Serial.println(state);
      }
    }
  } else {
    Serial.println("Failed to read traffic light data");
    Serial.println("Reason: " + fbdo.errorReason());
  }
}

void setLaneLight(int state) {
  // state: 0 = OFF, 1 = ON
  if (state == 1) {
    digitalWrite(LANE_LIGHT_PIN, HIGH);
    Serial.println("→ Lane Light: ON");
  } else {
    digitalWrite(LANE_LIGHT_PIN, LOW);
    Serial.println("→ Lane Light: OFF");
  }
}

void setTrafficLight(char state) {
  // Turn off all traffic lights first
  digitalWrite(TRAFFIC_RED_PIN, LOW);
  digitalWrite(TRAFFIC_YELLOW_PIN, LOW);
  digitalWrite(TRAFFIC_GREEN_PIN, LOW);

  // Set the requested light
  switch (state) {
    case 'R':
    case 'r':
      digitalWrite(TRAFFIC_RED_PIN, HIGH);
      Serial.println("→ Traffic Light: RED");
      break;

    case 'Y':
    case 'y':
      digitalWrite(TRAFFIC_YELLOW_PIN, HIGH);
      Serial.println("→ Traffic Light: YELLOW");
      break;

    case 'G':
    case 'g':
      digitalWrite(TRAFFIC_GREEN_PIN, HIGH);
      Serial.println("→ Traffic Light: GREEN");
      break;

    case 'O':
    case 'o':
      // All lights already off
      Serial.println("→ Traffic Light: OFF");
      break;

    default:
      Serial.print("→ Unknown traffic light command: ");
      Serial.println(state);
      break;
  }
}
