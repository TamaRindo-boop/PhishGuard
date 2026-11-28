import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from urllib.parse import urlparse
import re

url_length = ctrl.Antecedent(np.arange(0, 151, 1), 'url_length')
uses_ip = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'uses_ip')
keywords = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'keywords')
protocol = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'protocol')
risk_level = ctrl.Consequent(np.arange(0, 101, 1), 'risk_level')

url_length['corta'] = fuzz.trimf(url_length.universe, [0, 0, 40])
url_length['media'] = fuzz.trimf(url_length.universe, [30, 50, 80])
url_length['larga'] = fuzz.trapmf(url_length.universe, [70, 90, 150, 150])

uses_ip['no'] = fuzz.trapmf(uses_ip.universe, [0, 0, 0.4, 0.6])
uses_ip['si'] = fuzz.trapmf(uses_ip.universe, [0.4, 0.6, 1, 1])

keywords['no'] = fuzz.trapmf(keywords.universe, [0, 0, 0.4, 0.6])
keywords['si'] = fuzz.trapmf(keywords.universe, [0.4, 0.6, 1, 1])

protocol['inseguro'] = fuzz.trapmf(protocol.universe, [0, 0, 0.4, 0.6])
protocol['seguro'] = fuzz.trapmf(protocol.universe, [0.4, 0.6, 1, 1])

risk_level['bajo'] = fuzz.trapmf(risk_level.universe, [0, 0, 25, 40])
risk_level['medio'] = fuzz.trapmf(risk_level.universe, [30, 45, 55, 70])
risk_level['alto'] = fuzz.trapmf(risk_level.universe, [60, 75, 85, 90])
risk_level['critico'] = fuzz.trapmf(risk_level.universe, [85, 95, 100, 100])

r1 = ctrl.Rule(url_length['larga'] & uses_ip['si'] & keywords['si'] & protocol['inseguro'], risk_level['critico'])
r2 = ctrl.Rule(url_length['larga'] & uses_ip['si'], risk_level['alto'])
r3 = ctrl.Rule(uses_ip['si'] & keywords['si'] & protocol['inseguro'], risk_level['critico'])
r4 = ctrl.Rule(url_length['media'] & uses_ip['si'] & protocol['inseguro'], risk_level['medio'])
r5 = ctrl.Rule(keywords['si'] & protocol['inseguro'], risk_level['alto'])
r6 = ctrl.Rule(url_length['larga'] & keywords['si'] & protocol['seguro'], risk_level['medio'])
r7 = ctrl.Rule(url_length['media'] & keywords['si'] & protocol['seguro'], risk_level['medio'])
r8 = ctrl.Rule(url_length['corta'] & uses_ip['no'] & keywords['no'] & protocol['seguro'], risk_level['bajo'])
r9 = ctrl.Rule(url_length['media'] & protocol['inseguro'], risk_level['medio'])
r10 = ctrl.Rule(url_length['corta'] & protocol['inseguro'], risk_level['medio'])

risk_ctrl = ctrl.ControlSystem([r1, r2, r3, r4, r5, r6, r7, r8, r9, r10])

def evaluar_url(url_ingresada):
    if not url_ingresada.startswith('http://') and not url_ingresada.startswith('https://'):
        url_ingresada = 'http://' + url_ingresada
        
    parsed_url = urlparse(url_ingresada)
    longitud = len(url_ingresada)
    
    # ... (tu código de usa_ip y palabras_sospechosas se queda igual) ...
    patron_ip = r'^(\d{1,3}\.){3}\d{1,3}$'
    usa_ip = 1 if re.match(patron_ip, parsed_url.netloc) else 0
    
    palabras_sospechosas = ['login', 'verify', 'secure', 'account', 'update', 'bank', 'paypal', 'signin']
    tiene_keywords = 1 if any(p in url_ingresada.lower() for p in palabras_sospechosas) else 0
    protocolo_seguro = 1 if parsed_url.scheme == 'https' else 0

    # --- NUEVO: Contar caracteres especiales (típicos de spam/tracking) ---
    caracteres_especiales = len(re.findall(r'[?=&_\-/]', url_ingresada))
    
    # --- Lógica Difusa ---
    simulador = ctrl.ControlSystemSimulation(risk_ctrl)
    simulador.input['url_length'] = min(longitud, 150)
    simulador.input['uses_ip'] = usa_ip
    simulador.input['keywords'] = tiene_keywords
    simulador.input['protocol'] = protocolo_seguro
    
    try:
        simulador.compute()
        puntuacion = round(simulador.output['risk_level'], 2)
    except KeyError:
        puntuacion = 10.0
    
    # --- NUEVO: Penalización manual por exceso de caracteres especiales o longitud extrema ---
    # Si la URL tiene más de 100 caracteres y muchos símbolos (?=&-_/)
    if longitud > 100 and caracteres_especiales > 15:
        puntuacion += 40  # Le sumamos 40 puntos de riesgo (se vuelve alto/crítico)
    elif longitud > 150:
        puntuacion += 30  # URLs demasiado largas también son sospechosas

    # Evitar que pase de 100
    puntuacion = min(puntuacion, 100)

    if puntuacion < 30:
        nivel = "BAJO"
    elif puntuacion < 60:
        nivel = "MEDIO"
    elif puntuacion < 80:
        nivel = "ALTO"
    else:
        nivel = "CRÍTICO"
        
    # --- Generar indicadores ---
    indicadores = []
    if longitud > 75: indicadores.append("Longitud de URL excesiva")
    if usa_ip: indicadores.append("Uso de dirección IP en lugar de dominio")
    if tiene_keywords: indicadores.append("Palabras clave de phishing detectadas")
    if not protocolo_seguro: indicadores.append("Protocolo HTTP no seguro")
    if caracteres_especiales > 15: indicadores.append("Exceso de caracteres especiales (posible spam/tracking)") # <-- Nuevo indicador

    if nivel in ["ALTO", "CRÍTICO"]:
        recomendaciones = ["No ingresar datos personales", "Evitar descargar archivos", "Reportar al equipo de seguridad"]
    elif nivel == "MEDIO":
        recomendaciones = ["Verificar la autenticidad del sitio", "No compartir información confidencial"]
    else:
        recomendaciones = ["El sitio parece seguro, pero mantén la precaución."]

    return {
        "url": url_ingresada,
        "puntuacion": puntuacion,
        "nivel": nivel,
        "indicadores": indicadores,
        "recomendaciones": recomendaciones
    }