#!/usr/bin/env python3
"""
Servidor DNS simple para redirigir eljuegodeFer a la IP local
"""
import socket
import struct

def create_dns_response(query_data, domain, ip):
    """Crea una respuesta DNS para redirigir el dominio a la IP especificada"""
    # Parsear la consulta DNS
    transaction_id = query_data[:2]
    
    # Flags de respuesta (respuesta estándar, sin errores)
    flags = b'\x81\x80'  # Standard query response, no error
    
    # Número de preguntas, respuestas, autoridades, adicionales
    questions = b'\x00\x01'  # 1 pregunta
    answers = b'\x00\x01'    # 1 respuesta
    authority = b'\x00\x00'  # 0 autoridades
    additional = b'\x00\x00' # 0 adicionales
    
    # Construir la pregunta (copiarla de la consulta original)
    question_start = 12  # Después del header DNS
    question = query_data[question_start:]
    
    # Construir la respuesta
    # Puntero a la pregunta original
    answer_name = b'\xc0\x0c'  # Puntero al offset 12 (inicio de la pregunta)
    answer_type = b'\x00\x01'   # Tipo A (IPv4)
    answer_class = b'\x00\x01'  # Clase IN (Internet)
    answer_ttl = b'\x00\x00\x00\x3c'  # TTL de 60 segundos
    answer_length = b'\x00\x04'  # 4 bytes para IPv4
    answer_data = socket.inet_aton(ip)  # IP en formato binario
    
    # Construir respuesta completa
    response = (transaction_id + flags + questions + answers + authority + 
               additional + question + answer_name + answer_type + answer_class + 
               answer_ttl + answer_length + answer_data)
    
    return response

def start_dns_server():
    """Inicia el servidor DNS"""
    DOMAIN = "eljuegodeFer"
    LOCAL_IP = "192.168.1.140"
    DNS_PORT = 53
    
    # Crear socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind(('0.0.0.0', DNS_PORT))
        print(f"🚀 Servidor DNS iniciado en puerto {DNS_PORT}")
        print(f"📡 Redirigiendo {DOMAIN} -> {LOCAL_IP}")
        print("💡 Configura tu móvil para usar este DNS: 192.168.1.140")
        print("🔄 Presiona Ctrl+C para detener")
        
        while True:
            # Recibir consulta DNS
            data, addr = sock.recvfrom(512)
            print(f"📥 Consulta DNS desde: {addr}")
            
            # Crear y enviar respuesta
            if DOMAIN.lower().encode() in data.lower():
                response = create_dns_response(data, DOMAIN, LOCAL_IP)
                sock.sendto(response, addr)
                print(f"✅ Enviada respuesta: {DOMAIN} -> {LOCAL_IP}")
            else:
                print("❌ Consulta para otro dominio, ignorada")
                
    except PermissionError:
        print("❌ Error: Necesitas ejecutar como administrador para usar el puerto 53")
        print("💡 Ejecuta: python dns_server.py como administrador")
    except KeyboardInterrupt:
        print("\n🛑 Servidor DNS detenido")
    finally:
        sock.close()

if __name__ == "__main__":
    start_dns_server()
