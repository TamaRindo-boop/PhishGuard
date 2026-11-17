import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# 1. DEFINIR LAS VARIABLES (Entradas y Salida)
# URL Length: de 0 a 150
url_length = ctrl.Antecedent(np.arange(0, 151, 1), 'url_length')
uses_ip = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'uses_ip')
keywords = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'keywords')
protocol = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'protocol')
risk_level = ctrl.Consequent(np.arange(0, 101, 1), 'risk_level')

# 2. FUNCIONES DE PERTENENCIA (Fuzzyficación)
# URL Length
url_length['corta'] = fuzz.trimf(url_length.universe, [0, 0, 40])
url_length['media'] = fuzz.trimf(url_length.universe, [30, 50, 80])
url_length['larga'] = fuzz.trapmf(url_length.universe, [70, 90, 150, 150])

# Uses IP
uses_ip['no'] = fuzz.trapmf(uses_ip.universe, [0, 0, 0.4, 0.6])
uses_ip['si'] = fuzz.trapmf(uses_ip.universe, [0.4, 0.6, 1, 1])

# Keywords
keywords['no'] = fuzz.trapmf(keywords.universe, [0, 0, 0.4, 0.6])
keywords['si'] = fuzz.trapmf(keywords.universe, [0.4, 0.6, 1, 1])

# Protocol
protocol['inseguro'] = fuzz.trapmf(protocol.universe, [0, 0, 0.4, 0.6])
protocol['seguro'] = fuzz.trapmf(protocol.universe, [0.4, 0.6, 1, 1])

# Risk Level
risk_level['bajo'] = fuzz.trapmf(risk_level.universe, [0, 0, 25, 40])
risk_level['medio'] = fuzz.trapmf(risk_level.universe, [30, 45, 55, 70])
risk_level['alto'] = fuzz.trapmf(risk_level.universe, [60, 75, 85, 90])
risk_level['critico'] = fuzz.trapmf(risk_level.universe, [85, 95, 100, 100])

# 3. BASE DE REGLAS
rule1 = ctrl.Rule(url_length['larga'] & uses_ip['si'] & keywords['si'] & protocol['inseguro'], risk_level['critico'])
rule2 = ctrl.Rule(url_length['larga'] & uses_ip['si'], risk_level['alto'])
rule3 = ctrl.Rule(uses_ip['si'] & keywords['si'] & protocol['inseguro'], risk_level['critico'])
rule4 = ctrl.Rule(url_length['media'] & uses_ip['si'] & protocol['inseguro'], risk_level['medio'])
rule5 = ctrl.Rule(keywords['si'] & protocol['inseguro'], risk_level['alto'])
rule6 = ctrl.Rule(url_length['larga'] & keywords['si'] & protocol['seguro'], risk_level['medio'])
rule7 = ctrl.Rule(url_length['media'] & keywords['si'] & protocol['seguro'], risk_level['medio'])
rule8 = ctrl.Rule(url_length['corta'] & uses_ip['no'] & keywords['no'] & protocol['seguro'], risk_level['bajo'])
rule9 = ctrl.Rule(url_length['media'] & protocol['inseguro'], risk_level['medio'])
rule10 = ctrl.Rule(url_length['corta'] & protocol['inseguro'], risk_level['medio'])

# 4. CREAR EL SISTEMA DE CONTROL
risk_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10])

# 5. PRUEBA DE FUNCIONAMIENTO
def probar_sistema():
    riesgo_simulador = ctrl.ControlSystemSimulation(risk_ctrl)
    
    # Ejemplo de URL sospechosa (Larga, usa IP, tiene keywords, es HTTP)
    riesgo_simulador.input['url_length'] = 120
    riesgo_simulador.input['uses_ip'] = 1
    riesgo_simulador.input['keywords'] = 1
    riesgo_simulador.input['protocol'] = 0
    
    riesgo_simulador.compute()
    print(f"Puntuación de Riesgo: {riesgo_simulador.output['risk_level']:.2f} / 100")

if __name__ == "__main__":
    probar_sistema()