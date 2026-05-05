# Smart Fan Gateway

This project implements a Python-based gateway that connects a server to an Arduino-controlled fan using serial communication.

##  Architecture

  
Server (REST API)  
↓  
Python Gateway  
↓  
Arduino Fan (Serial via Bluetooth/USB)

---

## ⚙️ Requirements

- Python 3.x
- pyserial
- requests
- flask (only required for mock server)

Install dependencies:

```bash
pip install -r requirements.txt