import speedtest
import subprocess
import platform
from datetime import datetime
import json
from app.core.enums import ConnectionType
from app.utils.network import get_connection_type, get_interface_info
from app.schemas import models
import redis
import psutil
import time

class NetworkMonitor:
    def __init__(self, network_id: int):
        self.network_id = network_id
        self.st = speedtest.Speedtest()
        
    def _store_metric_in_redis(self, redis_client: redis.Redis, metrics: dict):
        """Almacena métricas en Redis con TTL"""
        # Guardar métricas actuales
        redis_key_current = f"network:{self.network_id}:current"
        redis_client.hset(redis_key_current, mapping=metrics)
        redis_client.expire(redis_key_current, 60)  # TTL 60 segundos

        # Guardar en historial de métricas (últimas 100)
        redis_key_history = f"network:{self.network_id}:history"
        redis_client.lpush(redis_key_history, json.dumps(metrics))
        redis_client.ltrim(redis_key_history, 0, 99)  # Mantener solo últimas 100
        redis_client.expire(redis_key_history, 86400)  # TTL 24 horas

    def _get_metrics_from_redis(self, redis_client: redis.Redis, limit: int = 100):
        """Obtiene métricas históricas de Redis"""
        redis_key_history = f"network:{self.network_id}:history"
        metrics = redis_client.lrange(redis_key_history, 0, limit - 1)
        return [json.loads(m) for m in metrics]

    def measure_speed(self):
        """Mide la velocidad de subida y bajada"""
        try:
            self.st.get_best_server()
            download_speed = self.st.download() / 1_000_000  # Convert to Mbps
            upload_speed = self.st.upload() / 1_000_000  # Convert to Mbps
            return upload_speed, download_speed
        except Exception as e:
            print(f"speedtest failed: {e}")
        
        
        try:
            # Opción 2: Métricas del sistema con psutil
            print("Trying psutil...")
            net_before = psutil.net_io_counters()
            time.sleep(1)  # Intervalo de 1 segundo para calcular la velocidad
            net_after = psutil.net_io_counters()
            download_speed = (net_after.bytes_recv - net_before.bytes_recv) / (1024 * 1024)  # Mbps
            upload_speed = (net_after.bytes_sent - net_before.bytes_sent) / (1024 * 1024)    # Mbps
            return upload_speed, download_speed
        except Exception as e:
            return 0.0, 0.0

    def measure_latency(self):
        """Mide la latencia usando ping"""
        try:
            host = "8.8.8.8"  # Google DNS
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "1", host]
            output = subprocess.check_output(command).decode("utf-8")
            
            if platform.system().lower() == "darwin":  # MacOS
                latency = float(output.split("time=")[1].split(" ms")[0])
            else:
                latency = float(output.split("time=")[1].split("ms")[0])
            
            return latency
        except:
            return 0.0

    def get_packet_loss(self):
        """Mide la pérdida de paquetes"""
        try:
            host = "8.8.8.8"
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "10", host]
            output = subprocess.check_output(command).decode("utf-8")
            
            if platform.system().lower() == "darwin":  # MacOS
                packet_loss = float(output.split("packet loss")[0].split()[-1].strip("%"))
            else:
                packet_loss = float(output.split("%")[0].split()[-1])
            
            return packet_loss
        except:
            return 0.0

    def get_metrics(self):
        """Obtiene todas las métricas de red"""
        upload_speed, download_speed = self.measure_speed()
        latency = self.measure_latency()
        packet_loss = self.get_packet_loss()
        connection_type = get_connection_type()
        
        return models.NetworkMetricCreate(
            network_id=self.network_id,
            upload_speed=upload_speed,
            download_speed=download_speed,
            latency=latency,
            packet_loss=packet_loss,
            connection_type=connection_type
        )

    def get_realtime_data(self, redis_client: redis.Redis):
        """Obtiene datos para Redis en tiempo real y los almacena"""
        metrics = self.get_metrics()
        metric_data = {
            "upload_speed": str(metrics.upload_speed),
            "download_speed": str(metrics.download_speed),
            "latency": str(metrics.latency),
            "packet_loss": str(metrics.packet_loss),
            "connection_type": str(metrics.connection_type.value),
            "timestamp": datetime.now().isoformat()
        }
        
        # Almacenar en Redis
        self._store_metric_in_redis(redis_client, metric_data)
        
        return metric_data

    def get_historical_metrics(self, redis_client: redis.Redis, limit: int = 100):
        """Obtiene métricas históricas de Redis"""
        return self._get_metrics_from_redis(redis_client, limit)
    
    def test_connection(self):
        try:
            upload_speed, download_speed = self.measure_speed()
            latency = self.measure_latency()
            metric_data = {
                "upload_speed": upload_speed,
                "download_speed": download_speed,
                "latency": latency,
            }
            return metric_data
        except Exception as e:
            print(f"speedtest failed: {e}")
            metric_data = {
                "upload_speed": 0.0,
                "download_speed": 0.0,
                "latency": 0.0,
            }
            
            return metric_data