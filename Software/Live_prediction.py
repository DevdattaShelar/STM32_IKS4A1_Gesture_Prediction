import serial
import numpy as np
from collections import deque
import tensorflow as tf
import joblib
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf.runtime_version')


# --- CONFIGURATION ---
COM_PORT = 'COM21'  # Replace with your COM port
BAUD_RATE = 115200
SENSOR_HZ = 67
WINDOW_SIZE = 50
THRESHOLD = 0.85  # Confidence threshold

gesture_labels = ['idle', 'shake', 'up-down']

# --- Load Scaler ---
scaler = joblib.load("scaler.pkl")  # Load the saved StandardScaler

# --- Load TFLite Model ---
interpreter = tf.lite.Interpreter(model_path="converted_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# --- Sliding window buffer ---
buffer = deque(maxlen=WINDOW_SIZE)

def preprocess_window(window):
    window = np.array(window)
    window = scaler.transform(window)
    return np.expand_dims(window, axis=0).astype(np.float32)

def predict_gesture(window):
    input_data = preprocess_window(window)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])[0]
    confidence = np.max(output_data)
    predicted_idx = np.argmax(output_data)
    if confidence >= THRESHOLD:
        return gesture_labels[predicted_idx], confidence
    else:
        return "unknown", confidence

def live_predict():
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
        print(f"[INFO] Listening on {COM_PORT}...")
        last_prediction = None  # To store the previous gesture

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue
            try:
                values = list(map(int, line.split(',')))
                if len(values) != 6:
                    continue
                buffer.append(values)
                if len(buffer) == WINDOW_SIZE:
                    gesture, conf = predict_gesture(list(buffer))
                    if gesture != last_prediction:
                        print(f"Gesture: {gesture} ({conf:.2f})")
                        last_prediction = gesture
            except Exception:
                pass  # Skip bad lines silently
    except serial.SerialException as e:
        print(f"[ERROR] Could not open port: {e}")

if __name__ == "__main__":
    live_predict()
