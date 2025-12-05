#!/usr/bin/env python3
"""
ESP32 Traffic Controller - Python Control Example

This script demonstrates how to control the ESP32 traffic lights
from a Python application using Firebase Admin SDK.

Usage:
    python control_example.py

Requirements:
    pip install firebase-admin
"""

import firebase_admin
from firebase_admin import credentials, db
import time

# ===== CONFIGURATION =====
# Download your serviceAccountKey.json from:
# Firebase Console > Project Settings > Service Accounts > Generate New Private Key
SERVICE_ACCOUNT_KEY = "serviceAccountKey.json"
DATABASE_URL = "https://your-project-default-rtdb.firebaseio.com/"

# Firebase paths
LANE_LIGHT_PATH = "urban/lane_light"
TRAFFIC_LIGHT_PATH = "urban/traffic_light"


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL
        })
        print("✅ Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        return False


def set_lane_light(state):
    """
    Control the lane light (road lighting)

    Args:
        state (int): 0 for OFF, 1 for ON
    """
    try:
        ref = db.reference(LANE_LIGHT_PATH)
        ref.set(state)
        status = "ON" if state == 1 else "OFF"
        print(f"💡 Lane Light: {status}")
        return True
    except Exception as e:
        print(f"❌ Error setting lane light: {e}")
        return False


def set_traffic_light(state):
    """
    Control the traffic light

    Args:
        state (str): 'R' for Red, 'Y' for Yellow, 'G' for Green, 'O' for Off
    """
    valid_states = ['R', 'Y', 'G', 'O']
    state = state.upper()

    if state not in valid_states:
        print(f"❌ Invalid state: {state}. Use R, Y, G, or O")
        return False

    try:
        ref = db.reference(TRAFFIC_LIGHT_PATH)
        ref.set(state)

        state_names = {'R': 'RED', 'Y': 'YELLOW', 'G': 'GREEN', 'O': 'OFF'}
        print(f"🚦 Traffic Light: {state_names[state]}")
        return True
    except Exception as e:
        print(f"❌ Error setting traffic light: {e}")
        return False


def get_current_status():
    """Get current status of all lights"""
    try:
        lane_ref = db.reference(LANE_LIGHT_PATH)
        traffic_ref = db.reference(TRAFFIC_LIGHT_PATH)

        lane_state = lane_ref.get()
        traffic_state = traffic_ref.get()

        print("\n📊 Current Status:")
        print(f"   Lane Light: {'ON' if lane_state == 1 else 'OFF'}")
        print(f"   Traffic Light: {traffic_state}")
        return True
    except Exception as e:
        print(f"❌ Error getting status: {e}")
        return False


def demo_sequence():
    """Run a demo sequence of traffic light changes"""
    print("\n🎬 Starting demo sequence...\n")

    # Turn on lane light
    print("Step 1: Turn on lane lighting")
    set_lane_light(1)
    time.sleep(2)

    # Traffic light sequence: Red -> Yellow -> Green
    print("\nStep 2: Traffic light RED")
    set_traffic_light('R')
    time.sleep(3)

    print("\nStep 3: Traffic light YELLOW")
    set_traffic_light('Y')
    time.sleep(2)

    print("\nStep 4: Traffic light GREEN")
    set_traffic_light('G')
    time.sleep(3)

    # Turn everything off
    print("\nStep 5: Turn off all lights")
    set_traffic_light('O')
    time.sleep(1)
    set_lane_light(0)

    print("\n✅ Demo sequence complete!")


def interactive_mode():
    """Interactive mode for manual control"""
    print("\n🎮 Interactive Control Mode")
    print("=" * 50)
    print("Lane Light Commands:")
    print("  0 - Turn OFF")
    print("  1 - Turn ON")
    print("\nTraffic Light Commands:")
    print("  R - Red")
    print("  Y - Yellow")
    print("  G - Green")
    print("  O - Off")
    print("\nOther Commands:")
    print("  status - Show current status")
    print("  demo   - Run demo sequence")
    print("  quit   - Exit")
    print("=" * 50)

    while True:
        try:
            command = input("\nEnter command: ").strip().upper()

            if command == "QUIT":
                print("👋 Goodbye!")
                break
            elif command == "STATUS":
                get_current_status()
            elif command == "DEMO":
                demo_sequence()
            elif command in ["0", "1"]:
                set_lane_light(int(command))
            elif command in ["R", "Y", "G", "O"]:
                set_traffic_light(command)
            else:
                print("❌ Unknown command. Try: 0, 1, R, Y, G, O, status, demo, or quit")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main function"""
    print("=" * 50)
    print("ESP32 Traffic Controller - Python Control")
    print("=" * 50)

    # Initialize Firebase
    if not initialize_firebase():
        print("\n⚠️  Please configure your Firebase credentials:")
        print("1. Download serviceAccountKey.json from Firebase Console")
        print("2. Update DATABASE_URL in this script")
        return

    # Show current status
    get_current_status()

    # Run interactive mode
    interactive_mode()


if __name__ == "__main__":
    main()
