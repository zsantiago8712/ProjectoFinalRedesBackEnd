import socket
from icmplib import ping
import statistics
from datetime import datetime
from app.core.database import get_db
from app.services.redis_service import redis_service
from dataclasses import dataclass

@dataclass
class MetricsService:
    
    last_bytes_sent = 0
    last_bytes_recv = 0
    last_time = datetime.now().timestamp()

    def get_network_speed(self):
        import psutil
        net_counters = psutil.net_io_counters()
        current_time = datetime.now().timestamp()
        
        bytes_sent = net_counters.bytes_sent
        bytes_recv = net_counters.bytes_recv
        
        upload_speed = (bytes_sent - self.last_bytes_sent) / (current_time - self.last_time)
        download_speed = (bytes_recv - self.last_bytes_recv) / (current_time - self.last_time)
        
        self.last_bytes_sent = bytes_sent
        self.last_bytes_recv = bytes_recv
        self.last_time = current_time
        
        return upload_speed / 125000, download_speed / 125000

    def ping_host(self, address: str) -> dict:
        try:
            ping_result = ping(address, count=2, interval=0.2, privileged=False)
            dns_host = self.get_host_dns(address)
            return {
                "success": True,
                "dns_host": dns_host,
                "latency": ping_result.avg_rtt,
                "packets_sent": ping_result.packets_sent,
                "packets_received": ping_result.packets_received,
                "packet_loss": ping_result.packet_loss
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def aggregate_daily_metrics(self, host_id: int):
        metrics = redis_service.get_metrics(host_id, "host_metrics")
        if not metrics:
            return

        latencies = [m.get("latency", 0) for m in metrics]
        if not latencies:
            return

        daily_metrics = {
            "avg_latency": statistics.mean(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "packet_loss_percent": statistics.mean([m.get("packet_loss", 0) for m in metrics])
        }

        with get_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO daily_metrics 
                         (host_id, date, avg_latency, min_latency, max_latency, packet_loss_percent)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                     (host_id, datetime.now().date().isoformat(),
                      daily_metrics["avg_latency"],
                      daily_metrics["min_latency"],
                      daily_metrics["max_latency"],
                      daily_metrics["packet_loss_percent"]))
            conn.commit()
            
            
    def get_host_dns(self, address: str) -> str:
        # 1. Verificar si es un host conocido
        try:
            hosrtname = socket.gethostbyaddr(address)[0]
            return hosrtname
        except Exception as e:
            return "No domain name found"

metrics_service = MetricsService()