import cv2
import time
import threading
from collections import defaultdict
from ultralytics import YOLO
import firebase_admin
from firebase_admin import credentials, db

# --- CONFIGURATION ---
MODEL_PATH = "best.pt"
FIREBASE_CREDENTIALS_PATH = "serviceAccountKey.json"
FIREBASE_DATABASE_URL = "https://stem-53cdc-default-rtdb.firebaseio.com/"

# Settings
CONFIDENCE_THRESHOLD = 0.4
FRAME_SKIP = 3                # Skip fewer frames for smoother detection if possible
EMERGENCY_CLASS_NAME = "Emergency" 
EMERGENCY_EXIT_DELAY = 10 
TRAFFIC_CYCLE_INTERVAL = 30   # Change lights every 30 seconds

# Global Status for Threading
current_traffic_light = "100"
current_lane_light = 0

def init_firebase():
    """Initialize Firebase connection"""
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DATABASE_URL})
        print("✓ Firebase connected")
        return True
    except Exception as e:
        print(f"✗ Firebase error: {e}")
        return False

def send_firebase_update(traffic_val, lane_val):
    """Function to run in a separate thread to prevent lag"""
    try:
        updates = {
            '/traffic_lights': traffic_val,
            '/lane_light': lane_val
        }
        db.reference().update(updates)
        # print(f"-> Sent: T={traffic_val}, L={lane_val}") # Uncomment to debug
    except Exception as e:
        print(f"✗ Send Error: {e}")

def update_hardware_async(traffic_val, lane_val):
    """Starts a background thread to send data"""
    t = threading.Thread(target=send_firebase_update, args=(traffic_val, lane_val))
    t.daemon = True # Thread dies when main program dies
    t.start()

def draw_info(frame, count, fps, status, time_left, lane_status):
    """Draws the dashboard"""
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 230), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Text Settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    white = (255, 255, 255)
    green = (0, 255, 0)
    red = (0, 0, 255)
    
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40), font, 0.6, green, 2)
    cv2.putText(frame, f"Total Vehicles: {count}", (20, 75), font, 0.7, white, 2)
    
    # Timer Status
    color = red if "RED" in status else green
    if "EMERGENCY" in status: color = (0, 0, 255)
    cv2.putText(frame, f"Main Light: {status}", (20, 115), font, 0.6, color, 2)
    
    # Timer Countdown
    if time_left > 0:
        cv2.putText(frame, f"Switch in: {time_left:.0f}s", (20, 145), font, 0.6, (0, 255, 255), 2)
    else:
        cv2.putText(frame, f"Switch in: --", (20, 145), font, 0.6, (0, 255, 255), 2)

    # Lane Status
    lane_text = "OPEN (Low Traffic)" if lane_status == 1 else "CLOSED (High Traffic)"
    if "EMERGENCY" in status: lane_text = "OPEN (EMERGENCY)"
    l_color = green if lane_status == 1 else red
    cv2.putText(frame, f"Gate: {lane_text}", (20, 185), font, 0.5, l_color, 2)

    return frame

def main():
    print("="*70)
    print("TRAFFIC CONTROL: THREADED + TOTAL COUNT")
    print("="*70)
    
    if not init_firebase(): return
    
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"✗ Model error: {e}")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): return

    # ROI Setup
    ret, first_frame = cap.read()
    if ret:
        first_frame = cv2.resize(first_frame, (640, 480))
        roi = cv2.selectROI("Select Area", first_frame, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select Area")
        roi_x, roi_y, roi_w, roi_h = roi
        if roi_w == 0: roi_x, roi_y, roi_w, roi_h = 0, 0, 640, 480
    else: return

    # Variables
    frame_count = 0
    fps_time = time.time()
    fps_counter = 0
    current_fps = 0
    
    # Timer & Logic
    last_cycle_switch = time.time()
    is_green_light = False
    
    emergency_active = False
    last_emergency_time = 0
    
    total_vehicles = 0
    predictions = []
    
    # Optimization: Don't send duplicate data to Firebase
    last_sent_traffic = ""
    last_sent_lane = -1
    last_firebase_time = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.resize(frame, (640, 480))
            
            # Draw ROI box
            cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), (255,0,0), 1)

            frame_count += 1
            fps_counter += 1
            now = time.time()
            
            # Update FPS
            if now - fps_time >= 1.0:
                current_fps = fps_counter / (now - fps_time)
                fps_counter = 0
                fps_time = now

            # --- 1. DETECTION (Run every FRAME_SKIP frames) ---
            if frame_count % FRAME_SKIP == 0:
                predictions = []
                roi_frame = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
                
                # Inference
                results = model(roi_frame, conf=CONFIDENCE_THRESHOLD, verbose=False)[0]
                
                class_counts = defaultdict(int)
                for box in results.boxes:
                    bx, by, bw, bh = box.xywh[0].tolist()
                    cls_id = int(box.cls[0])
                    name = model.names[cls_id]
                    conf = float(box.conf[0])
                    
                    predictions.append({'x': bx, 'y': by, 'w': bw, 'h': bh, 'class': name, 'conf': conf})
                    class_counts[name] += 1
                
                # --- FIXED COUNTING LOGIC ---
                # Total = Cars + Emergency Vehicles
                car_num = class_counts.get('Car', 0)
                emerg_num = class_counts.get(EMERGENCY_CLASS_NAME, 0)
                total_vehicles = car_num + emerg_num
                
                # Check for immediate emergency presence
                if emerg_num > 0:
                    emergency_active = True
                    last_emergency_time = now

            # --- 2. LOGIC UPDATES (Run every frame) ---
            
            # Check if emergency is "cooling down"
            if emergency_active:
                if now - last_emergency_time > EMERGENCY_EXIT_DELAY:
                    emergency_active = False
                    # Reset timer so we don't switch immediately after emergency
                    last_cycle_switch = now 

            # Traffic Light Timer (30s Cycle)
            # Only count time if NOT in emergency
            if not emergency_active:
                time_in_cycle = now - last_cycle_switch
                if time_in_cycle > TRAFFIC_CYCLE_INTERVAL:
                    is_green_light = not is_green_light
                    last_cycle_switch = now
                    time_in_cycle = 0
                
                # Set Main Light Status
                if is_green_light:
                    current_traffic_light = "001" # Green
                    status_text = "GREEN"
                else:
                    current_traffic_light = "100" # Red
                    status_text = "RED"
                
                # Calculate time left
                time_display = TRAFFIC_CYCLE_INTERVAL - time_in_cycle

                # Lane Light Logic (Gate)
                # Open if cars <= 6 (using total_vehicles now)
                if total_vehicles <= 6:
                    current_lane_light = 1
                else:
                    current_lane_light = 0

            else:
                # EMERGENCY OVERRIDE
                current_traffic_light = "100" # Force Red on main road
                current_lane_light = 1        # Force Gate Open
                status_text = "EMERGENCY"
                time_display = 0

            # --- 3. FIREBASE UPDATE (Threaded) ---
            # Update if state changed OR every 2 seconds to keep connection alive
            if (current_traffic_light != last_sent_traffic or 
                current_lane_light != last_sent_lane or 
                now - last_firebase_time > 2.0):
                
                update_hardware_async(current_traffic_light, current_lane_light)
                
                last_sent_traffic = current_traffic_light
                last_sent_lane = current_lane_light
                last_firebase_time = now

            # --- 4. DRAWING ---
            # Draw Boxes
            for p in predictions:
                x = int(p['x'] + roi_x - p['w']/2)
                y = int(p['y'] + roi_y - p['h']/2)
                
                if p['class'] == EMERGENCY_CLASS_NAME: color = (0,0,255)
                elif p['class'] == 'car': color = (0,255,0)
                else: color = (255,0,255)
                
                cv2.rectangle(frame, (x,y), (x+int(p['w']), y+int(p['h'])), color, 2)
                
                # --- EDIT HERE: Create label with confidence ---
                label = f"{p['class']} {p['conf']:.2f}"
                cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            frame = draw_info(frame, total_vehicles, current_fps, status_text, time_display, current_lane_light)
            
            cv2.imshow('Smart Traffic', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✓ System Shutdown")

if __name__ == "__main__":
    main()