from urllib.parse import urlparse
import re

def extraer_caracteristicas(url):
    # 1. Validar y parsear la URL
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url # Si el usuario no pone protocolo, asumimos HTTP por defecto
        
    parsed_url = urlparse(url)
    dominio = parsed_url.netloc
    ruta_completa = parsed_url.path
    
    # --- CARACTERÍSTICA 1: Longitud ---
    longitud = len(url)
    
    # --- CARACTERÍSTICA 2: ¿Usa IP? ---
    # Busca un patrón de 4 números separados por puntos (ej. 192.168.1.1)
    patron_ip = r'^(\d{1,3}\.){3}\d{1,3}$'
    usa_ip = 1 if re.match(patron_ip, dominio) else 0
    
    # --- CARACTERÍSTICA 3: Palabras clave ---
    palabras_sospechosas = ['login', 'verify', 'secure', 'account', 'update', 'bank', 'paypal', 'signin']
    tiene_keywords = 0
    for palabra in palabras_sospechosas:
        if palabra in url.lower():
            tiene_keywords = 1
            break
            
    # --- CARACTERÍSTICA 4: Protocolo ---
    protocolo_seguro = 1 if parsed_url.scheme == 'https' else 0
    
    return {
        "url_original": url,
        "longitud": longitud,
        "usa_ip": usa_ip,
        "tiene_keywords": tiene_keywords,
        "protocolo_seguro": protocolo_seguro
    }

# --- PRUEBA ---
if __name__ == "__main__":
    # Probemos con una URL de phishing
    url_peligrosa = "http://192.168.1.50/paypal-login-verify-account-update"
    print("Analizando URL:", url_peligrosa)
    caracteristicas = extraer_caracteristicas(url_peligrosa)
    print(caracteristicas)