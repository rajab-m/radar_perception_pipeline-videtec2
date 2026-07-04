# Radar Perception Pipeline

A modular radar perception framework for receiving raw radar data over UDP, decoding Range–Doppler (RD) maps and detections, preprocessing radar measurements, and running object classification using an ONNX model.

The pipeline was originally implemented inside a ROS2 node and has been refactored into a standalone modular Python application for better portability, easier to test, maintain, and deploy.

---

## Project Overview

Within the broader Videtec2 project, this radar perception pipeline is designed for intersection monitoring and roadside perception using stationary radars. The main goal is to process radar data reliably in environments where camera-based systems are less effective, such as complex traffic intersections, changing weather, varying illumination, and long-range detection scenarios.

Radar is especially valuable in Videtec2 because it provides stable measurements of moving and static objects even under challenging environmental conditions. In this project environment, stationary radar sensors are used to observe traffic participants at intersections and support protection-oriented scenarios involving VRUs. The pipeline is designed to take raw radar measurements and transform them into meaningful perception outputs that can support object understanding and downstream decision-making.

The system processes radar data that typically includes:

Range–Doppler (RD) maps
Point detections
Radar target attributes such as:
range
speed (Doppler)
magnitude (RCS)
azimuth
elevation

In this pipeline, radar measurements are received through a UDP stream, reconstructed into complete packets, decoded, and then passed through a perception workflow. The pipeline crops local RD map regions around detections, normalizes the input data, and runs neural-network inference for object classification.

The current object classes are:

pedestrian
cyclist
vehicle
truck


## Pipeline Architecture

The processing flow is:

```text
Radar Simulator / Radar Device
            │
            ▼
UDP Receiver
            │
            ▼
Packet Reconstruction
            │
            ▼
Radar Decoder
            │
            ▼
RD Map Cropping
            │
            ▼
Data Preprocessing
            │
            ▼
ONNX Inference
            │
            ▼
Predicted Object Labels
```

---

## Repository Structure

```text
radar_perception_pipeline/
│
├── main.py
├── radar_pipeline.py
│
├── network/
│   └── udp_receiver.py
│
├── decoder/
│   └── radar_decoder.py
│
├── perception/
│   ├── cropping.py
│   ├── preprocessing.py
│   └── inference.py
│
├── config/
│   ├── environment.json
│   └── model_config.json
│
├── models/
│   └── radar_east.onnx
│
├── simulator/
│   └── radar_simulator.py
│
└── utils/
    ├── io.py
    └── sync.py
```

---

## Module Description

### `main.py`

Application entry point.

Responsibilities:

* initialize the pipeline
* load configuration
* start UDP processing
* execute continuous inference loop

---

### `radar_pipeline.py`

Main orchestration logic.

Responsibilities:

* initialize all modules
* connect pipeline stages
* process incoming radar measurements
* coordinate preprocessing and inference

---

### `network/udp_receiver.py`

Handles network communication.

Responsibilities:

* create UDP socket
* receive incoming packets
* reconstruct chunked transmissions
* buffer incoming data

---

### `decoder/radar_decoder.py`

Converts received binary data into radar information.

Responsibilities:

* decode transmitted content
* parse RD maps
* parse detections
* reconstruct radar measurements

Outputs:

* full RD map
* cropped RD maps
* radar detections

---

### `perception/cropping.py`

Creates local RD windows around detections.

Responsibilities:

* crop local RD regions
* pad boundary conditions
* preserve dimensions for inference

---

### `perception/preprocessing.py`

Prepares inputs for the neural network.

Responsibilities:

* normalize RD maps
* normalize radar features
* convert inputs to float32
* format ONNX inputs

---

### `perception/inference.py`

ONNX model wrapper.

Responsibilities:

* load ONNX model
* initialize inference session
* run predictions
* return class labels

---

### `simulator/radar_simulator.py`

Radar data generator for testing.

Responsibilities:

* create synthetic RD maps
* generate random detections
* create packet structure
* transmit chunked UDP packets

The simulator follows the same communication format as the original radar sender.

---

### `utils/io.py`

Utility functions:

* JSON loading
* helper methods

---

### `utils/sync.py`

Synchronization helpers.

Responsibilities:

* locate synchronization words
* align incoming packet streams

---

## Data Format

Incoming radar data contains:

### RD Map

```text
Range Bins × Doppler Bins
```

Example:

```text
128 × 256
```

---

### Detection structure

Each detection contains:

```text
[Range,
 Speed,
 Magnitude,
 Azimuth,
 Elevation]
```

---

## Packet Structure

UDP transmission follows:

```text
MAGICWORD
+
HEADER
+
CRC
+
TIMESTAMP
+
MSGPACK DATA
```

The receiver reconstructs chunked UDP packets before decoding.

---

## Model Inputs

The ONNX model expects:

```text
Cropped_RD_map
rcs
speed
range
azimuth
```

All values are converted to:

```python
float32
```

before inference.

---

## Installation

### 1. Create environment

Using Conda:

```bash
conda create -n radar python=3.10
conda activate radar
```

---

### 2. Install dependencies

CPU version:

```bash
pip install numpy
pip install msgpack
pip install crcmod
pip install onnxruntime
pip install jupyter
```

GPU version:

```bash
pip uninstall onnxruntime
pip install onnxruntime-gpu
```

---

### 3. Verify installation

```bash
python -c "import numpy,msgpack,crcmod,onnxruntime; print('Setup OK')"
```

---

## Configuration

### `config/environment.json`

Contains:

* sensor identifiers
* radar parameters
* sensor positions
* transformations

Example:

```json
{
    "sensors":{
        "1":{
            "RadarParam":{
                "RadarCube":"East"
            }
        }
    }
}
```

---

### `config/model_config.json`

Contains:

* normalization parameters
* RD map scaling values
* cropping thresholds

---

## Running the Pipeline

Open two terminals.

### Terminal 1

Start the perception pipeline:

```bash
conda activate radar

cd radar_perception_pipeline

python main.py
```

Expected output:

```text
Starting radar pipeline
Listening for incoming radar packets...
```

---

### Terminal 2

Run the simulator:

```bash
conda activate radar

cd radar_perception_pipeline

python simulator/radar_simulator.py
```

Expected output:

```text
Sending packet 1
Sending packet 2
Sending packet 3
...
```

---

## Expected Processing Flow

```text
Simulator sends packet
        ↓
UDP receiver reconstructs stream
        ↓
Decoder extracts RD map
        ↓
Cropping extracts local regions
        ↓
Preprocessor normalizes data
        ↓
ONNX model predicts labels
        ↓
Results displayed
```

---

## Future Improvements

Potential future extensions:

* multi-radar support
* packet loss simulation
* asynchronous processing
* multi-threaded inference
* real-time visualization
* GPU optimization
* radar tracking
* sensor fusion integration
* deployment inside Docker containers

---

## Notes

The repository currently uses a standalone Python architecture and no longer depends on ROS2.

The simulator was designed to replicate the packet structure of the original radar source, allowing the complete pipeline to be tested without hardware.

---

## License

Specify project license here.
