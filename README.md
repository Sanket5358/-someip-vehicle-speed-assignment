# Introduction to SOME/IP Using Python and someipy

## 1. Project Overview

This project demonstrates the implementation of **Scalable Service-Oriented Middleware over IP (SOME/IP)** communication using Python and the `someipy` library on Ubuntu Linux.

The project simulates communication between two automotive Electronic Control Units (ECUs):

1. **Vehicle ECU (Provider):** Provides vehicle speed information through a SOME/IP service.
2. **Instrument Cluster ECU (Consumer):** Discovers the Vehicle ECU service, requests vehicle speed, and receives speed updates through event subscription.

The implementation demonstrates the fundamental concepts of SOME/IP communication, including service discovery, method request-response communication, event-based communication, and packet analysis using Wireshark.

---

## 2. Project Objectives

The main objectives of this project are:

- To understand the fundamentals of SOME/IP communication.
- To implement a SOME/IP service provider and consumer using Python.
- To configure and use the someipy library.
- To understand SOME/IP Service Discovery (SD).
- To implement method-based request-response communication.
- To implement event-based publish-subscribe communication.
- To simulate communication between automotive ECUs.
- To capture and analyze SOME/IP network traffic using Wireshark.
- To study service availability and communication behavior through practical experiments.

---

## 3. System Architecture

The project consists of three main components:

### 3.1 SOME/IP Daemon

The SOME/IP daemon manages communication and service discovery between the provider and consumer.

### 3.2 Vehicle ECU – Provider

The Vehicle ECU acts as a SOME/IP service provider.

Its responsibilities include:

- Offering the VehicleSpeedService.
- Handling GetSpeed method requests.
- Sending vehicle speed responses.
- Publishing SpeedChanged events.

### 3.3 Instrument Cluster ECU – Consumer

The Instrument Cluster ECU acts as a SOME/IP service consumer.

Its responsibilities include:

- Discovering the VehicleSpeedService.
- Sending GetSpeed method requests.
- Receiving vehicle speed responses.
- Subscribing to SpeedChanged events.
- Receiving speed updates from the provider.

### Communication Flow

```text
              SOME/IP Communication

       +---------------------------+
       |     SOME/IP Daemon        |
       |                           |
       |   Service Discovery (SD)  |
       +-------------+-------------+
                     |
          +----------+----------+
          |                     |
          |                     |
+---------v---------+  +--------v----------+
|   Vehicle ECU     |  | Instrument Cluster|
|                   |  |       ECU         |
|    Provider       |  |     Consumer      |
|                   |  |                   |
| GetSpeed Method   |  | GetSpeed Request  |
| SpeedChanged Event|  | Event Subscription|
+-------------------+  +-------------------+
          |
          |
    Vehicle Speed Data
```

---

## 4. SOME/IP Service Configuration

The following service configuration is used in this project.

| Parameter | Configuration |
|---|---|
| Service Name | VehicleSpeedService |
| Service ID | 0x1234 |
| Instance ID | 0x5678 |
| Major Version | 1 |
| Minor Version | 0 |
| Provider IP Address | 127.0.0.1 |
| Provider Port | 3000 |
| Consumer IP Address | 127.0.0.1 |
| Consumer Port | 3002 |
| Transport Protocol | UDP |
| SD Multicast Address | 224.224.224.245 |
| SD UDP Port | 30490 |

### Method Configuration

| Parameter | Value |
|---|---|
| Method Name | GetSpeed |
| Method ID | 0x0001 |
| Request Payload | Empty |
| Response Payload | uint16 |
| Purpose | Retrieve vehicle speed |

### Event Configuration

| Parameter | Value |
|---|---|
| Event Name | SpeedChanged |
| Event ID | 0x8001 |
| Event Group ID | 0x0001 |
| Payload | uint16 |
| Event Interval | 2 seconds |
| Purpose | Publish vehicle speed updates |

---

## 5. Technologies and Tools Used

| Technology / Tool | Purpose |
|---|---|
| Python | Application development |
| someipy | SOME/IP implementation |
| SOME/IP | Automotive service-oriented communication |
| SOME/IP Service Discovery | Service discovery and availability |
| UDP/IP | Network communication |
| Ubuntu Linux | Development environment |
| Wireshark | Network packet capture and analysis |
| TShark | Command-line packet analysis |
| Git | Version control |
| GitHub | Project hosting and documentation |

---

## 6. Project Directory Structure

```text
someip-vehicle-speed-assignment/
│
├── captures/
│   └── assignment1-someip.pcapng
│
├── config/
│   └── someipyd.json
│
├── docs/
│   └── Task_10_SOMEIP_Experiments_Observation_Report_WITH_SCREENSHOTS.docx
│
├── screenshots/
│   ├── 01_someipy_daemon_logs.png
│   ├── 02_vehicle_ecu_provider.png
│   ├── 03_instrument_cluster_consumer.png
│   ├── experiment_10_3_consumer.png
│   ├── experiment_10_4_provider.png
│   └── Additional experiment screenshots
│
├── src/
│   ├── cluster_client.py
│   ├── vehicle_speed_interface.py
│   └── vehicle_speed_service.py
│
├── .gitignore
└── README.md
```

**Directory description:**

- `src/` – Contains the Python source code.
- `config/` – Contains the SOME/IP daemon configuration.
- `captures/` – Contains captured network traffic.
- `screenshots/` – Contains practical experiment screenshots.
- `docs/` – Contains the experiment observation report.
- `.gitignore` – Excludes unnecessary files from Git tracking.

---

## 7. Installation and Setup

### Step 1: Install Python and Git

Update the Ubuntu package list:

```bash
sudo apt update
```

Install Python, pip, virtual environment support, and Git:

```bash
sudo apt install python3 python3-pip python3-venv git -y
```

### Step 2: Clone the Repository

After uploading this project to GitHub, clone it using:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Navigate to the project directory:

```bash
cd someip-vehicle-speed-assignment
```

### Step 3: Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

### Step 4: Install someipy

```bash
pip install someipy
```

Verify the installation:

```bash
pip show someipy
```

---

## 8. SOME/IP Daemon Configuration

The daemon configuration is stored in:

`config/someipyd.json`

Configuration:

```json
{
    "sd_address": "224.224.224.245",
    "sd_port": 30490,
    "log_level": "DEBUG",
    "interface": "127.0.0.1",
    "use_tcp": false
}
```

The configuration uses:

- Multicast address: `224.224.224.245`
- Service Discovery port: `30490`
- Network interface: `127.0.0.1`
- Transport: UDP
- Logging level: DEBUG

---

## 9. Running the Project

The application uses three separate terminal windows.

### Terminal 1: Start SOME/IP Daemon

Open the first terminal:

```bash
cd ~/someip-vehicle-speed-assignment
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Start the daemon:

```bash
someipyd
```

Keep this terminal running.

### Terminal 2: Start Vehicle ECU Provider

Open the second terminal:

```bash
cd ~/someip-vehicle-speed-assignment
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the Vehicle ECU provider:

```bash
python src/vehicle_speed_service.py
```

The provider offers the VehicleSpeedService and handles incoming method requests and event publication.

### Terminal 3: Start Instrument Cluster Consumer

Open the third terminal:

```bash
cd ~/someip-vehicle-speed-assignment
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the Instrument Cluster consumer:

```bash
python src/cluster_client.py
```

The consumer discovers the service, sends GetSpeed requests, and subscribes to SpeedChanged events.

---

## 10. SOME/IP Communication

### 10.1 Method-Based Communication

The GetSpeed method demonstrates request-response communication.

Communication sequence:

1. The consumer discovers the VehicleSpeedService.
2. The consumer sends a GetSpeed request.
3. The provider receives the request.
4. The provider prepares the vehicle speed response.
5. The consumer receives the response.

**Method ID:** `0x0001`

### 10.2 Event-Based Communication

The SpeedChanged event demonstrates publish-subscribe communication.

Communication sequence:

1. The consumer discovers the service.
2. The consumer subscribes to the SpeedChanged event group.
3. The provider publishes vehicle speed updates.
4. The consumer receives the event notifications.

**Event ID:** `0x8001`

**Event Group ID:** `0x0001`

The configured event publishing interval is 2 seconds.

---

## 11. Wireshark Packet Analysis

Wireshark is used to capture and inspect SOME/IP network communication.

The captured packet file is available at:

```text
captures/assignment1-someip.pcapng
```

### Capture Interface

The loopback interface (`lo`) is used because the provider and consumer run on the same Ubuntu computer.

### Wireshark Display Filter

Use the following display filter:

```text
udp.port == 30490 || udp.port == 3000 || udp.port == 3002
```

### Packet Analysis Objectives

The packet capture is used to investigate:

- SOME/IP Service Discovery traffic.
- Service discovery requests.
- Communication between provider and consumer.
- UDP communication.
- SOME/IP message headers.
- Service ID and Method ID.
- Network communication behavior.

The captured packets can be inspected in Wireshark to understand the structure of SOME/IP communication.

---

## 12. Practical Experiments

The project includes practical experiments covering the following topics:

| Experiment | Description |
|---|---|
| 1 | Observe service discovery when the consumer starts before the provider. |
| 2 | Study GetSpeed method request-response communication. |
| 3 | Study SpeedChanged event subscription and notifications. |
| 4 | Observe provider behavior when the consumer is stopped. |
| 5 | Compare event publishing intervals. |
| 6 | Investigate service behavior during provider stop and restart. |

Detailed observations and available screenshots are included in the Word report under the `docs/` directory.

---

## 13. Screenshots and Documentation

The repository includes screenshots of the practical implementation.

The screenshots demonstrate:

- SOME/IP daemon execution.
- Vehicle ECU provider execution.
- Instrument Cluster consumer execution.
- Method request-response output.
- Event subscription and notifications.
- Practical experiment observations.

The experiment observation report is available at:

```text
docs/Task_10_SOMEIP_Experiments_Observation_Report_WITH_SCREENSHOTS.docx
```

---

## 14. Expected Learning Outcomes

After completing this project, the following concepts can be understood:

1. Fundamentals of automotive SOME/IP communication.
2. Difference between service providers and service consumers.
3. SOME/IP Service Discovery.
4. Method-based request-response communication.
5. Event-based publish-subscribe communication.
6. Service IDs, Instance IDs, Method IDs, and Event IDs.
7. UDP-based communication between automotive ECUs.
8. SOME/IP packet inspection using Wireshark.
9. Practical implementation of automotive service-oriented communication using Python.

---

## 15. Future Scope

The project can be extended with:

- Communication between multiple physical ECUs.
- Communication over Ethernet between separate computers.
- Integration with real automotive hardware.
- Additional vehicle signals such as engine RPM, temperature, and fuel level.
- CAN-to-SOME/IP gateway implementation.
- Advanced service discovery experiments.
- Integration with an automotive dashboard application.

These are possible future enhancements and are not claimed as completed features.

---

## 16. Author Information

**Author:** Sanket Chavan  
**Department:** Electronics and Telecommunication Engineering  
**Project:** Introduction to SOME/IP Using Python and someipy  
**Platform:** Ubuntu Linux

---

## 17. Repository Contents

This repository contains:

- Python source code.
- SOME/IP daemon configuration.
- Wireshark packet capture.
- Practical experiment screenshots.
- Experiment observation report.
- Project documentation.

**Note:** The `.venv/` directory and Python cache files are excluded from version control. Users can recreate the environment by following the installation instructions above.
