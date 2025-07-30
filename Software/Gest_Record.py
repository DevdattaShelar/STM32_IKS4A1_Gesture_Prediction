import serial
import time
import csv
import os

# --- Configuration ---
DEFAULT_COM_PORT = 'COM21'  # Change this as needed
BAUD_RATE = 115200
CSV_FILENAME = 'gesture_data.csv'

# --- Ensure CSV file exists ---
if not os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z', 'label'])

try:
    ser = serial.Serial(DEFAULT_COM_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Serial connected on {DEFAULT_COM_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"❌ Could not open serial port: {e}")
    ser = None

while True:
    print("\n=== Record New Gesture ===")
    gesture_label = input("👉 Enter gesture name (or 'q' to quit): ").strip()
    if gesture_label.lower() == 'q':
        break

    try:
        num_samples = int(input("🧮 Enter number of samples to record: "))
        sample_rate_hz = float(input("⏱️ Enter sampling rate (Hz): "))
    except ValueError:
        print("❌ Invalid input. Try again.")
        continue

    interval = 1.0 / sample_rate_hz

    print(f"\n🎬 Recording '{gesture_label}' for {num_samples} samples at {sample_rate_hz} Hz...")
    time.sleep(1.5)

    samples = []

    if ser is None or not ser.is_open:
        print("❌ Serial not available. Skipping.")
        continue

    count = 0
    while count < num_samples:
        line = ser.readline().decode('utf-8').strip()
        try:
            values = list(map(float, line.split(',')))
            if len(values) == 6:
                values.append(gesture_label)
                samples.append(values)
                print(f"[{count+1}] {values}")
                count += 1
                time.sleep(interval)
            else:
                print(f"⚠️ Invalid data format: {line}")
        except:
            print(f"⚠️ Parse error: {line}")
            continue

    # Append to CSV
    with open(CSV_FILENAME, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(samples)

    print(f"✅ {num_samples} samples of '{gesture_label}' recorded.")

# --- Cleanup ---
if 'ser' in locals() and ser and ser.is_open:
    ser.close()
print("👋 Done recording. CSV saved to:", CSV_FILENAME)
