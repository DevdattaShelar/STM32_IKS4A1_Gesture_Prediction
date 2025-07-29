import serial
import time
import numpy as np
import tensorflow as tf
from collections import deque
import joblib # Import joblib for loading scaler and label_encoder

# --- Configuration for Live Prediction ---
COM_PORT = 'COM21'  # *** IMPORTANT: Replace with your actual COM port (e.g., 'COM3' or '/dev/ttyUSB0') ***
BAUD_RATE = 115200 # *** IMPORTANT: Replace with your actual Baud Rate ***
SENSOR_HZ = 67  # Your sensor's sampling rate in Hz

# Ensure TIME_STEPS and N_FEATURES match those used during training
TIME_STEPS = int(SENSOR_HZ * 0.75) # Must match the TIME_STEPS used during training
if TIME_STEPS == 0:
    TIME_STEPS = 1
print(f"Live prediction TIME_STEPS: {TIME_STEPS}")

N_FEATURES = 6     # Must match the N_FEATURES used during training (accel_x,y,z, gyro_x,y,z)

# Load the trained model, label encoder, and scaler
try:
    model = tf.keras.models.load_model('SIMPLE/simple_gesture_recognition_model.h5') # type: ignore
    label_encoder = joblib.load('SIMPLE/simple_label_encoder.pkl')  # Load the label encoder
    scaler = joblib.load('SIMPLE/simple_scaler.pkl')  # Load the scaler
    print("Model, label encoder, and scaler loaded successfully.")
    # Verify the number of classes loaded from the encoder matches model's output layer
    if model.output_shape[-1] != len(label_encoder.classes_):
        print("Warning: Mismatch between model output units and label encoder classes. This might lead to incorrect predictions.")
except Exception as e:
    print(f"Error loading model or preprocessors: {e}")
    print("Please ensure you have trained and saved the model by running 'train_gesture_model.py' first.")
    exit()

# Initialize a deque (double-ended queue) to store the sensor readings for a window
sensor_data_buffer = deque(maxlen=TIME_STEPS)

# --- Function to process incoming serial data ---
def process_serial_data(line):
    try:
        # Split the line by comma and convert to float
        # Ensure the order of values matches your N_FEATURES and training data
        # Example line from COM port: "0.12,0.34,9.81,0.01,-0.05,0.02"
        values = [float(x) for x in line.strip().split(',')]
        if len(values) == N_FEATURES:
            return np.array(values)
        else:
            print(f"Warning: Unexpected number of features ({len(values)}) in line: '{line.strip()}' Expected: {N_FEATURES}")
            return None
    except ValueError as e:
        print(f"Error parsing serial data (non-float or empty?): '{line.strip()}' - {e}")
        return None
    except IndexError as e:
        print(f"Error parsing serial data (not enough values?): '{line.strip()}' - {e}")
        return None


# --- Main loop for live prediction ---
def live_predict():
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1) # timeout=1 is important
        print(f"Connected to COM port: {COM_PORT} at {BAUD_RATE} baud rate.")
        print("Waiting for sensor data...")

        last_prediction_time = time.time()
        # You might want to predict less frequently than every single incoming data point.
        # For example, if TIME_STEPS is 50 (0.75 seconds of data), you could predict every 0.1 seconds.
        PREDICTION_INTERVAL = 0.1 # seconds, determines how often a prediction is made

        while True:
            # Read all available lines in the buffer to keep up with the sensor data
            while ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    processed_data = process_serial_data(line)

                    if processed_data is not None:
                        sensor_data_buffer.append(processed_data)
                except UnicodeDecodeError:
                    print(f"Decoding error, skipping line: {ser.readline()}")
                    continue # Skip current problematic line and try next

            # Make a prediction only if the buffer is full and enough time has passed
            current_time = time.time()
            if len(sensor_data_buffer) == TIME_STEPS and (current_time - last_prediction_time) >= PREDICTION_INTERVAL:
                # Convert deque to numpy array
                # Use np.copy() to ensure the array is contiguous in memory if needed by scaler
                current_window = np.array(sensor_data_buffer)

                # Scale the current window using the loaded scaler
                # Reshape for scaler if it was fitted on 2D data (samples, features)
                scaled_window = scaler.transform(current_window.reshape(-1, N_FEATURES)).reshape(TIME_STEPS, N_FEATURES)

                # Reshape for model prediction (1 sample, TIME_STEPS, N_FEATURES)
                model_input = scaled_window.reshape(1, TIME_STEPS, N_FEATURES)

                # Make prediction
                predictions = model.predict(model_input, verbose=0) # verbose=0 to suppress prediction output
                predicted_class_index = np.argmax(predictions)
                
                # Check if the predicted_class_index is within the bounds of label_encoder
                if predicted_class_index < len(label_encoder.classes_):
                    predicted_gesture = label_encoder.inverse_transform([predicted_class_index])[0]
                    confidence = predictions[0][predicted_class_index] * 100
                    print(f"Detected Gesture: {predicted_gesture} (Confidence: {confidence:.2f}%)")
                else:
                    print(f"Warning: Predicted class index {predicted_class_index} out of bounds for label encoder.")
                    print(f"Raw predictions: {predictions}")
                
                last_prediction_time = current_time
            
            time.sleep(0.005) # Small delay to prevent busy-waiting, adjust if needed

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
        print(f"Please check if {COM_PORT} is correct, the device is connected, and the port is not in use.")
    except KeyboardInterrupt:
        print("\nExiting live prediction.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == '__main__':
    live_predict()
