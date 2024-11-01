import sqlite3
from contextlib import contextmanager
from typing import Generator
from fastapi import HTTPException
from typing import Tuple

@contextmanager
def _get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect('network_monitor.db')
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with _get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS hosts
                     (id INTEGER PRIMARY KEY, address TEXT UNIQUE, dns TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS daily_metrics
                     (id INTEGER PRIMARY KEY,
                      host_id INTEGER,
                      date TEXT,
                      avg_latency REAL,
                      min_latency REAL,
                      max_latency REAL,
                      packet_loss_percent REAL,
                      FOREIGN KEY (host_id) REFERENCES hosts (id))''')
        conn.commit()
        
        
def add_host(address: str) -> int:
    with _get_db() as conn:
        try:
            c = conn.cursor()
            c.execute('INSERT INTO hosts (address) VALUES (?)', (address))
            conn.commit()
            return c.lastrowid
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Host ya existe")
        
def get_hosts(host_id: int) -> list[Tuple[str, int, str | None]]:
    with _get_db() as conn:
        try:
            c = conn.cursor()
            c.execute('SELECT id, address, dns FROM hosts WHERE id = ?', (host_id,))
            row = c.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Host no encontrado")
            return [Tuple(row[0], row[1], row[2]) 
                    for row in c.fetchall()]
            
        except ValueError:
            raise HTTPException(status_code=400, detail="Host no encontrado")


def  get_host(adress: str) -> Tuple[int, str, str] | None:
    with _get_db() as conn:
        try:
            c = conn.cursor()
            c.execute('SELECT id, address, dns FROM hosts WHERE address = ?', (adress,))
            row = c.fetchone()
           
            if not row:
                return None
            return Tuple(row[0], row[1], row[2])
            
        except ValueError:
            raise HTTPException(status_code=400, detail="Host no encontrado")