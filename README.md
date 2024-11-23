# Network Monitor Backend

Real-time network monitoring solution with performance tracking and route analysis.

## Features

- Network performance monitoring (upload/download times)
- Route change detection
- Network fault diagnosis
- Real-time data visualization
- Historical data access
- Multiple network management
- Location-based network monitoring

## Tech Stack

- Python 3.11+
- FastAPI
- SQLite
- Redis
- WebSockets

## Project Structure

```
network-monitor/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── websocket.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── database.py
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── network.py
│   │   └── diagnostics.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── models.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
├── scripts/
│   ├── init_db.sh
│   └── setup_redis.sh
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

```bash
# Install Python 3.9+
brew install python@3.11

# Install Redis
brew install redis
```

### Installation

```bash
# Clone repository
git clone https://github.com/user/network-monitor-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Database Setup

```bash
# Initialize SQLite
./scripts/init_db.sh

# Start Redis
brew services start redis
```

## Development

```bash
# Start development server
uvicorn app.main:app --reload
```

## Testing

```bash
# Run tests
pytest
```

## API Documentation

Once running, visit:

- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

# Database Documentation

## SQLite Structure

### Networks Table

```sql
networks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier
    name TEXT NOT NULL,                    -- Network name (e.g., "Office WiFi")
    alias TEXT NOT NULL,                   -- Custom name (e.g., "Office WiFi - Floor 3")
    location TEXT,                         -- Physical location (e.g., "Building A, Floor 3")
    created_at DATETIME                    -- Registration timestamp
)
```

### Network Metrics Table

```sql
network_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier
    network_id INTEGER,                    -- Reference to networks table
    upload_speed REAL,                     -- Upload speed in Mbps
    download_speed REAL,                   -- Download speed in Mbps
    latency REAL,                         -- Latency in ms
    packet_loss REAL,                     -- Packet loss percentage
    connection_type INTEGER,              -- 0: Ethernet, 1: WiFi
    timestamp DATETIME,                    -- Measurement timestamp
    FOREIGN KEY (network_id) REFERENCES networks(id)
)
```
