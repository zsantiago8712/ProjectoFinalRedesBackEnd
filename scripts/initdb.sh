#!/bin/bash
# init_db.sh

# Crear base de datos SQLite
sqlite3 network_monitor.db << 'END_SQL'
CREATE TABLE IF NOT EXISTS networks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    alias TEXT NOT NULL,
    location TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS network_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    network_id INTEGER,
    upload_speed REAL,
    download_speed REAL,
    latency REAL,
    packet_loss REAL,
    connection_type INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (network_id) REFERENCES networks(id)
);

CREATE TABLE IF NOT EXISTS route_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    network_id INTEGER,
    old_route TEXT,
    new_route TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (network_id) REFERENCES networks(id)
);
END_SQL