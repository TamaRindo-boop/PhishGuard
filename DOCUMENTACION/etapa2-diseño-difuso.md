# Diseño del Sistema Difuso Mamdani

## Variables de Entrada
- **url_length**: Longitud de la URL (0 a 150).
- **uses_ip**: Usa IP en vez de dominio (0 = No, 1 = Sí).
- **keywords**: Tiene palabras clave sospechosas (0 = No, 1 = Sí).
- **protocol**: Tipo de conexión (0 = HTTP, 1 = HTTPS).

## Variable de Salida
- **risk_level**: Nivel de riesgo (0 a 100).

## Base de Reglas (10 reglas principales)
1. Si URL es Larga Y usa IP Y tiene keywords Y es HTTP -> Riesgo Crítico
2. Si URL es Larga Y usa IP -> Riesgo Alto
3. Si usa IP Y tiene keywords Y es HTTP -> Riesgo Crítico
4. Si URL es Media Y usa IP Y es HTTP -> Riesgo Medio
5. Si tiene keywords Y es HTTP -> Riesgo Alto
6. Si URL es Larga Y tiene keywords Y es HTTPS -> Riesgo Medio
7. Si URL es Media Y tiene keywords Y es HTTPS -> Riesgo Medio
8. Si URL es Corta Y No usa IP Y No tiene keywords Y es HTTPS -> Riesgo Bajo
9. Si URL es Media Y es HTTP -> Riesgo Medio
10. Si URL es Corta Y es HTTP -> Riesgo Medio