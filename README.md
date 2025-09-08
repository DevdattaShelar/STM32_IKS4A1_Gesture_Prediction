## Gesture Prediction using IKS4A1 Sensor and STM32L412RB-P

---

## Table of Contents

* [1. Introduction](#1-introduction)
* [2. Hardware Used](#2-hardware-used)
* [3. Software Used](#3-software-used)
* [4. Project Overview](#4-project-overview)
    * [4.1. Data Acquisition](#41-data-acquisition)
    * [4.2. Dataset Creation](#42-dataset-creation)
    * [4.3. Machine Learning Model](#43-machine-learning-model)
    * [4.4. Embedded Implementation](#44-embedded-implementation)
* [5. Setup and Installation](#5-setup-and-installation)
    * [5.1. Hardware Connections](#51-hardware-connections)
    * [5.2. Software Setup](#52-software-setup)
    * [5.3. Flashing the STM32](#53-flashing-the-stm32)
* [6. Usage](#6-usage)
* [7. Results](#7-results)
* [8. Future Work](#8-future-work)
* [9. Contributing](#9-contributing)


---

## 1. Introduction


This project demonstrates a real-time gesture prediction system leveraging the **STMicroelectronics IKS4A1 Sensor X-NUCLEO-IKS01A4 expansion board** and an **STM32L412RB-P microcontroller board**. We collected a custom dataset of various gestures, trained our own machine learning model to recognize these gestures. The system aims to provide an intuitive and efficient way to interact with devices or applications through hand gestures.

## 2. Hardware Used

List all the hardware components used in your project. Be specific with model numbers where possible.

* **STM32L412RB-P Nucleo Board:** The main microcontroller board.
* **IKS4A1 (X-NUCLEO-IKS01A4) Sensor Expansion Board:** This board integrates multiple sensors, including (Accelerometer, Gyroscope from the LSM6DSV16X ).
    * *Specifically, for gesture recognition, we primarily utilized the data from the [Accelerometer/Gyroscope] of the [LSM6DSV16X] sensor on the IKS4A1 board.*
* **USB Cable:** For power and programming the STM32 board.

## 3. Software Used

List all the software tools, IDEs, libraries, and frameworks.

* **STM32CubeIDE:** For embedded code development, compilation, and flashing.
* **STM32CubeMX:** For configuring the STM32 microcontroller peripherals (often integrated into STM32CubeIDE).
* **Python [Version, e.g., 3.8+]**: For data collection, processing, and ML model development.
    * **Libraries:**
        * `pandas`: For data manipulation.
        * `numpy`: For numerical operations.
        * `scikit-learn`: For machine learning model training and evaluation.
        * `tensorflow` / `keras`: If you used a neural network (specify if TensorFlow Lite for Microcontrollers was used).
        * `matplotlib` / `seaborn`: For data visualization.
        * `pyserial`: For serial communication with the STM32 during data collection.
        * `[Any other specific Python libraries you used]`
* **Jupyter Notebook / Google Colab:** For developing and documenting the ML pipeline.

## 4. Project Overview

### 4.1. Data Acquisition

We developed a firmware for the STM32L412RB-P to read raw accelerometer and gyroscope data from the IKS4A1 sensor at a high sampling rate. This data was then streamed over a serial (UART) connection to a host PC. A Python script on the PC was used to capture and log this incoming sensor data.

### 4.2. Dataset Creation

Explain how you processed the raw data to create your custom dataset for gesture recognition.

After collecting raw data for each intended gesture, the data was pre-processed. This involved:
* **Segmentation:** Isolating individual gesture instances from continuous data streams.
* **Labeling:** Assigning the correct gesture label to each segment.
* **Normalization/Scaling:** Applying techniques like Min-Max scaling or Standardization to the sensor readings.
* **Feature Extraction:** used raw time-series data.
The resulting dataset, containing features/raw data and corresponding labels, was stored in a CSV file.

### 4.3. Machine Learning Model


We developed a custom machine learning model for gesture prediction.
* **Model Type:**  1D-Convolutional Neural Network (CNN).
* **Training:** The model was trained using the custom dataset created in the previous step. We employed standard machine learning practices, including data splitting (training, validation, test sets), hyperparameter tuning, and cross-validation to optimize model performance.
* **Framework:** [e.g., `scikit-learn`, `TensorFlow`/`Keras`].

### 4.4. Embedded Implementation

Explain how the trained model was deployed onto the STM32.

The trained machine learning model was converted into a format suitable for deployment on the STM32L412RB-P. This typically involves:
* **Model Conversion:** (If using neural networks) Converting the model to TensorFlow Lite for Microcontrollers (`.tflite`) format.
* **Code Generation:** Using tools like X-CUBE-AI (for STM32CubeIDE) or custom C code to integrate the model's inference engine into the embedded firmware.
* **Real-time Inference:** The STM32 firmware now continuously reads sensor data, performs the same pre-processing steps as during training, feeds the processed data to the embedded ML model, and outputs the predicted gesture.

## 5. Setup and Installation

### 5.1. Hardware Connections

The IKS4A1 (X-NUCLEO-IKS01A4) expansion board can be directly stacked onto the STM32L412RB-P Nucleo board using the Arduino Uno-compatible connectors. Ensure proper alignment before pushing down firmly.

### 5.2. Software Setup

Instructions for installing necessary software and Python libraries.
I have given th complete project zip in repo, just have to download , unzip it ,bulid it and change the app_mems.c file with i have given file.
1.  **STM32CubeIDE:** Download and install STM32CubeIDE from the STMicroelectronics website.
2.  **Python:** Install Python [11.3.0] from [python.org](https://www.python.org/).
3.  **Python Libraries:** Open a terminal or command prompt and install the required Python libraries:
    ```bash
    pip install pandas numpy scikit-learn tensorflow pyserial matplotlib seaborn
    # Add any other specific libraries
    `
    
4.  **[Optional] Jupyter Notebook/Google Colab:**
    * For Jupyter: `pip install jupyter` and then `jupyter notebook` to launch.
    * For Google Colab: Access through your Google account.

### 5.3. Flashing the STM32

How to compile and flash the firmware to the STM32.

1.  **Open Project in STM32CubeIDE:**
    * Navigate to `[Path to your STM32CubeIDE project folder]/[Project Name]`.
    * Open the project in STM32CubeIDE.
2.  **Build Project:**
    * Go to `Project` -> `Build Project` (or click the hammer icon).
3.  **Flash to Board:**
    * Connect the STM32L412RB-P board to your computer via USB.
    * Go to `Run` -> `Debug` (green bug icon) or `Run` -> `Run` (green play icon). This will typically build and flash the firmware. Ensure the correct ST-Link programmer is selected in the debug configuration.

## 6. Usage

Once the STM32 firmware is flashed and running:

1.  ** The STM32 will start acquiring sensor data and performing gesture inference.
2.  **[How to see the output]:**
    * If using serial output: Open a serial terminal (e.g., PuTTY, Termite,TeraTerm) connected to the STM32's virtual COM port (check Device Manager for the COM port number, usually `STMicroelectronics STLink Virtual COM Port`). Set the baud rate to `[Your Baud Rate, e.g., 115200]`. You should see predicted gestures being printed.
    * If using LEDs/display: Observe the LEDs or the connected display for gesture indications.
3.  **Perform Gestures:** Perform the gestures you trained the model on (e.g. idle,shake and Up-down). Observe the system's response.

## 7. Results

project's performance.

* **Model Accuracy:** 99%.
* **Real-time Performance:** Model is recognizing Gestures quickly and accurately.
* **Challenges and Successes:** The Main challenge that i faced while doing this project was about the dataset, what are the correct methods to capture the gesture data, how to perform gesture correctly,
  in the end when the dataset was finished, it was to clean so model was tending to overfit.
## 8. Future Work

Ideas for improving or expanding the project.

* Integrate more gestures.
* Improve model accuracy and robustness.
* Optimize embedded code for lower power consumption.
* Develop a user interface (UI) to interact with the system.
* Connect to a specific application (e.g., control a smart home device, play games).
* Explore different sensor fusion techniques.
* Implement over-the-air (OTA) updates for the firmware.

## 9. Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
5.  Push to the branch (`git push origin feature/AmazingFeature`).
6.  Open a Pull Request.

## 10. Acknowledgments

* STMicroelectronics for the excellent STM32 and sensor documentation/tools.
* Thanks to My intership Guide Shripad Govekar for guidance 
* Thanks to Avinash Mane Sir for giving me this Opportuinity.
---
