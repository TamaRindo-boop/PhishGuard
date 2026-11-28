import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

severidad = ctrl.Antecedent(np.arange(1, 11, 1), 'severidad')
probabilidad = ctrl.Antecedent(np.arange(1, 11, 1), 'probabilidad')
exposicion = ctrl.Antecedent(np.arange(1, 11, 1), 'exposicion')
controles = ctrl.Antecedent(np.arange(1, 11, 1), 'controles')
riesgo_empresarial = ctrl.Consequent(np.arange(0, 101, 1), 'riesgo_empresarial')

for var in [severidad, probabilidad, exposicion]:
    var['bajo'] = fuzz.trimf(var.universe, [1, 1, 5])
    var['medio'] = fuzz.trimf(var.universe, [3, 5, 8])
    var['alto'] = fuzz.trimf(var.universe, [6, 10, 10])

controles['deficiente'] = fuzz.trimf(controles.universe, [1, 1, 5])
controles['regular'] = fuzz.trimf(controles.universe, [3, 5, 8])
controles['excelente'] = fuzz.trimf(controles.universe, [6, 10, 10])

riesgo_empresarial['bajo'] = fuzz.trimf(riesgo_empresarial.universe, [0, 0, 35])
riesgo_empresarial['medio'] = fuzz.trimf(riesgo_empresarial.universe, [30, 50, 70])
riesgo_empresarial['alto'] = fuzz.trimf(riesgo_empresarial.universe, [60, 80, 90])
riesgo_empresarial['critico'] = fuzz.trimf(riesgo_empresarial.universe, [85, 100, 100])

r1 = ctrl.Rule(severidad['alto'] & probabilidad['alto'] & controles['deficiente'], riesgo_empresarial['critico'])
r2 = ctrl.Rule(severidad['alto'] & exposicion['alto'] & controles['deficiente'], riesgo_empresarial['critico'])
r3 = ctrl.Rule(probabilidad['alto'] & exposicion['alto'] & controles['deficiente'], riesgo_empresarial['critico'])
r4 = ctrl.Rule(severidad['alto'] & probabilidad['medio'], riesgo_empresarial['alto'])
r5 = ctrl.Rule(severidad['medio'] & probabilidad['alto'], riesgo_empresarial['alto'])
r6 = ctrl.Rule(controles['deficiente'] & exposicion['alto'], riesgo_empresarial['alto'])
r7 = ctrl.Rule(severidad['medio'] & probabilidad['medio'], riesgo_empresarial['medio'])
r8 = ctrl.Rule(controles['regular'] & exposicion['medio'], riesgo_empresarial['medio'])
r9 = ctrl.Rule(severidad['bajo'] & probabilidad['bajo'], riesgo_empresarial['bajo'])
r10 = ctrl.Rule(controles['excelente'] & exposicion['bajo'], riesgo_empresarial['bajo'])

riesgo_ctrl_emp = ctrl.ControlSystem([r1, r2, r3, r4, r5, r6, r7, r8, r9, r10])

def evaluar_riesgo_empresa(sev, prob, exp, ctrl_val):
    simulador = ctrl.ControlSystemSimulation(riesgo_ctrl_emp)
    simulador.input['severidad'] = sev
    simulador.input['probabilidad'] = prob
    simulador.input['exposicion'] = exp
    simulador.input['controles'] = ctrl_val
    simulador.compute()
    puntuacion = simulador.output['riesgo_empresarial']
    
    if puntuacion < 35:
        nivel = "BAJO"
        recomendacion = "Mantener las medidas actuales."
    elif puntuacion < 60:
        nivel = "MEDIO"
        recomendacion = "Revisar protocolos y capacitar al personal."
    elif puntuacion < 85:
        nivel = "ALTO"
        recomendacion = "Implementar controles urgentes."
    else:
        nivel = "CRÍTICO"
        recomendacion = "Detener operaciones y rediseñar la seguridad."
        
    return {"puntuacion": round(puntuacion, 2), "nivel": nivel, "recomendacion": recomendacion}
