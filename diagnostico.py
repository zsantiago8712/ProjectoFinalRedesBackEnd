import subprocess
import socket
import requests
import platform
import sys
import dns.resolver
from datetime import datetime
import traceroute

def ejecutar_comando(comando):
    """Ejecuta un comando del sistema y retorna el resultado"""
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        return resultado.stdout
    except Exception as e:
        return f"Error al ejecutar {comando}: {str(e)}"

def verificar_ping(host):
    """Verifica la conectividad mediante ping"""
    print(f"\n[+] Verificando ping a {host}...")
    
    parametro = "-n" if platform.system().lower() == "windows" else "-c"
    comando = f"ping {parametro} 4 {host}"
    
    resultado = ejecutar_comando(comando)
    if "bytes=" in resultado.lower() or "64 bytes" in resultado.lower():
        print(f"✓ Ping exitoso a {host}")
        return True
    else:
        print(f"✗ Falló el ping a {host}")
        return False

def verificar_dns(dominio):
    """Verifica la resolución DNS"""
    print(f"\n[+] Verificando resolución DNS para {dominio}...")
    try:
        respuesta = dns.resolver.resolve(dominio, 'A')
        for ip in respuesta:
            print(f"✓ Resolución DNS exitosa: {dominio} -> {ip}")
        return True
    except Exception as e:
        print(f"✗ Error en resolución DNS: {str(e)}")
        return False

def verificar_puerto(host, puerto):
    """Verifica si un puerto está abierto"""
    print(f"\n[+] Verificando puerto {puerto} en {host}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        resultado = sock.connect_ex((host, puerto))
        if resultado == 0:
            print(f"✓ Puerto {puerto} está abierto")
            return True
        else:
            print(f"✗ Puerto {puerto} está cerrado")
            return False
    except Exception as e:
        print(f"✗ Error al verificar puerto {puerto}: {str(e)}")
        return False
    finally:
        sock.close()

def verificar_http(url):
    """Verifica la conectividad HTTP/HTTPS"""
    print(f"\n[+] Verificando conexión HTTP a {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"✓ Conexión HTTP exitosa (Código: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Error en conexión HTTP: {str(e)}")
        return False

def analizar_ruta(host):
    """Analiza la ruta de red hacia el destino"""
    print(f"\n[+] Analizando ruta hacia {host}...")
    comando = f"traceroute {host}" if platform.system().lower() != "windows" else f"tracert {host}"
    print(ejecutar_comando(comando))

def diagnostico_completo(objetivo):
    """Realiza un diagnóstico completo de conectividad"""
    print(f"\n=== Iniciando diagnóstico de conectividad para {objetivo} ===")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Determinar si es una URL o IP
    try:
        socket.inet_aton(objetivo)
        es_ip = True
    except socket.error:
        es_ip = False
    
    # Si es un dominio, verificar DNS primero
    if not es_ip:
        dns_ok = verificar_dns(objetivo)
        if not dns_ok:
            print("\n⚠ Problema detectado: Falla en resolución DNS")
            print("Soluciones sugeridas:")
            print("1. Verificar configuración de DNS")
            print("2. Intentar con DNS alternativos (8.8.8.8 o 1.1.1.1)")
            print("3. Limpiar caché DNS local")
    
    # Verificar ping
    ping_ok = verificar_ping(objetivo)
    if not ping_ok:
        print("\n⚠ Problema detectado: No hay respuesta al ping")
        print("Soluciones sugeridas:")
        print("1. Verificar conexión física a la red")
        print("2. Comprobar firewall local")
        print("3. Verificar si el host destino permite ping")
    
    # Verificar puertos comunes
    puertos = [80, 443]  # Puertos HTTP y HTTPS
    for puerto in puertos:
        puerto_ok = verificar_puerto(objetivo, puerto)
        if not puerto_ok:
            print(f"\n⚠ Problema detectado: Puerto {puerto} no accesible")
            print("Soluciones sugeridas:")
            print("1. Verificar si el servicio está ejecutándose")
            print("2. Comprobar reglas de firewall")
            print("3. Verificar si el puerto está bloqueado por el ISP")
    
    # Si es una URL web, verificar HTTP
    if not es_ip:
        for protocolo in ['http', 'https']:
            url = f"{protocolo}://{objetivo}"
            http_ok = verificar_http(url)
            if not http_ok:
                print(f"\n⚠ Problema detectado: No hay respuesta {protocolo.upper()}")
                print("Soluciones sugeridas:")
                print("1. Verificar si el servidor web está funcionando")
                print("2. Comprobar certificado SSL (para HTTPS)")
                print("3. Verificar configuración del servidor web")
    
    # Analizar ruta de red
    print("\n[+] Analizando ruta de red...")
    analizar_ruta(objetivo)
    
    print("\n=== Diagnóstico completado ===")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python diagnostico.py <dominio/ip>")
        sys.exit(1)
    
    objetivo = sys.argv[1]
    diagnostico_completo(objetivo)