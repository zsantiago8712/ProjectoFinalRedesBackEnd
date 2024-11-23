import psutil
from app.core.enums import ConnectionType

def get_connection_type() -> ConnectionType:
    """
    Detecta el tipo de conexión de red actual.
    Returns:
        ConnectionType: ETHERNET o WIFI
    """
    interfaces = psutil.net_if_stats()
    
    for interface, stats in interfaces.items():
        if stats.isup:  # Si la interfaz está activa
            # En MacOS, las interfaces WiFi suelen empezar con 'en' o 'wl'
            if interface.startswith(('en', 'wl')):
                return ConnectionType.WIFI
            elif interface.startswith('eth'):
                return ConnectionType.ETHERNET
    
    return ConnectionType.WIFI  # Por defecto WiFi si no se puede determinar

def get_interface_info():
    """
    Obtiene información detallada de la interfaz de red activa.
    Returns:
        dict: Información de la interfaz
    """
    interfaces = psutil.net_if_stats()
    addresses = psutil.net_if_addrs()
    
    active_interface = None
    interface_info = {}
    
    for interface, stats in interfaces.items():
        if stats.isup:
            active_interface = interface
            interface_info = {
                'name': interface,
                'speed': stats.speed,
                'mtu': stats.mtu,
                'connection_type': get_connection_type(),
                'addresses': addresses.get(interface, [])
            }
            break
            
    return interface_info