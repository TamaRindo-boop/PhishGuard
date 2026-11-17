from .url_analyzer import extraer_caracteristicas
from . import motor_difuso as motor
def evaluar_url(url_ingresada):
    # 1. Extraer las características de la URL
    caracteristicas = extraer_caracteristicas(url_ingresada)
    
    # 2. Preparar el simulador difuso
    simulador = motor.ctrl.ControlSystemSimulation(motor.risk_ctrl)
    
    # 3. Asignar los valores extraídos al motor
    simulador.input['url_length'] = caracteristicas['longitud']
    simulador.input['uses_ip'] = caracteristicas['usa_ip']
    simulador.input['keywords'] = caracteristicas['tiene_keywords']
    simulador.input['protocol'] = caracteristicas['protocolo_seguro']
    
    # 4. Calcular el riesgo
    simulador.compute()
    
    # 5. Obtener el resultado
    puntuacion = simulador.output['risk_level']
    
    # 6. Clasificar el nivel para mostrarlo bonito
    if puntuacion < 30:
        nivel = "BAJO (Seguro)"
    elif puntuacion < 60:
        nivel = "MEDIO (Precaución)"
    elif puntuacion < 80:
        nivel = "ALTO (Sospechoso)"
    else:
        nivel = "CRÍTICO (Peligroso)"
        
    return {
        "url": caracteristicas['url_original'],
        "puntuacion": round(puntuacion, 2),
        "nivel": nivel,
        "detalles": caracteristicas
    }

# --- PRUEBA DEL SISTEMA COMPLETO ---
if __name__ == "__main__":
    print("=== SISTEMA DE DETECCIÓN DE PHISHING ===")
    
    # Prueba 1: URL normal y segura
    url_segura = "https://www.google.com"
    print(f"\nAnalizando: {url_segura}")
    resultado1 = evaluar_url(url_segura)
    print(f"Resultado: {resultado1['puntuacion']}/100 - Nivel: {resultado1['nivel']}")
    
    # Prueba 2: URL sospechosa (la que probamos antes)
    url_peligrosa = "http://192.168.1.50/paypal-login-verify-account-update"
    print(f"\nAnalizando: {url_peligrosa}")
    resultado2 = evaluar_url(url_peligrosa)
    print(f"Resultado: {resultado2['puntuacion']}/100 - Nivel: {resultado2['nivel']}")