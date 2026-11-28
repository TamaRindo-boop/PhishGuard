from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .motor_empresarial import evaluar_riesgo_empresa
from .motor_urls import evaluar_url # <-- IMPORTANTE: Esta línea conecta el detector
from .models import EvaluacionRiesgo
from .models import EvaluacionRiesgo, AnalisisURL # <-- Agrega AnalisisURL
from django.contrib.auth.models import User # <-- Agrega esto arriba

import matplotlib
matplotlib.use('Agg') # Necesario para que funcione sin interfaz gráfica
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import skfuzzy as fuzz
from django.db.models import Count

def inicio(request):
    return render(request, 'web/index.html')

def login(request):
    if request.user.is_authenticated:
        return redirect('panel')
    error = None
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        password = request.POST.get('password')
        user = authenticate(request, username=usuario, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('panel')
        error = 'Usuario o contraseña incorrectos.'
    return render(request, 'web/login.html', {'error': error})

def salir(request):
    auth_logout(request)
    return redirect('login')

@login_required
def panel(request):
    resultado = None
    if request.method == 'POST':
        try:
            # Usamos .get() y verificamos que no vengan vacíos
            sev_str = request.POST.get('severidad', '5')
            prob_str = request.POST.get('probabilidad', '5')
            exp_str = request.POST.get('exposicion', '5')
            ctrl_str = request.POST.get('controles', '5')
            
            sev = int(sev_str) if sev_str else 5
            prob = int(prob_str) if prob_str else 5
            exp = int(exp_str) if exp_str else 5
            ctrl_val = int(ctrl_str) if ctrl_str else 5

            # 1. Calculamos el riesgo con el motor difuso
            resultado = evaluar_riesgo_empresa(sev, prob, exp, ctrl_val)
            
            # 2. Guardamos en la base de datos
            EvaluacionRiesgo.objects.create(
                usuario=request.user,
                severidad=sev,
                probabilidad=prob,
                exposicion=exp,
                controles=ctrl_val,
                puntuacion=resultado['puntuacion'],
                nivel=resultado['nivel'],
                recomendacion=resultado['recomendacion']
            )
        except Exception as e:
            # Si algo falla, mostramos el error en consola pero no rompemos la página
            print("Error al procesar el panel:", e)

    # 3. Traemos todo el historial
    historial = EvaluacionRiesgo.objects.all().order_by('-fecha')

    return render(request, 'web/panel.html', {
        'resultado': resultado,
        'historial': historial
    })

# ==========================================
# NUEVA VISTA PARA EL DETECTOR DE URLS
# ==========================================
@login_required
def detector_urls(request):
    resultado = None
    if request.method == 'POST':
        url_a_analizar = request.POST.get('url_analizar')
        if url_a_analizar:
            resultado = evaluar_url(url_a_analizar)
            
    return render(request, 'web/detector.html', {'resultado': resultado})

@login_required
def detector_urls(request):
    resultado = None
    if request.method == 'POST':
        url_a_analizar = request.POST.get('url_analizar')
        if url_a_analizar:
            resultado = evaluar_url(url_a_analizar)
            
            # Guardar en la base de datos el análisis
            AnalisisURL.objects.create(
                usuario=request.user,
                url=resultado['url'],
                nivel=resultado['nivel'],
                puntuacion=resultado['puntuacion']
            )

    # Traer los últimos 5 análisis para el historial
    historial = AnalisisURL.objects.all().order_by('-fecha')[:5]
            
    return render(request, 'web/detector.html', {'resultado': resultado, 'historial': historial})

def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Crear el usuario en la base de datos de Django
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = nombre
        user.save()
        
        # Loguearlo automáticamente después de registrarse
        auth_login(request, user)
        return redirect('detector')
        
    return render(request, 'web/registro.html')

@login_required
def estadisticas(request):
    # --- 1. GRÁFICA MAMDANI ---
    fig, ax = plt.subplots(figsize=(6, 4))
    universo = np.arange(1, 11, 1)
    
    ax.plot(universo, fuzz.trimf(universo, [1, 1, 5]), 'g', linewidth=2, label='Bajo')
    ax.plot(universo, fuzz.trimf(universo, [3, 5, 8]), 'y', linewidth=2, label='Medio')
    ax.plot(universo, fuzz.trimf(universo, [6, 10, 10]), 'r', linewidth=2, label='Alto')
    
    ax.set_title('Funciones de Pertenencia - Severidad', color='white')
    ax.set_xlabel('Nivel de Severidad (1-10)', color='white')
    ax.set_ylabel('Grado de Pertenencia', color='white')
    ax.tick_params(colors='white')
    ax.legend(facecolor='#1e293b', labelcolor='white')
    ax.grid(True, alpha=0.2, color='gray')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#1e293b')
    buffer.seek(0)
    grafica_mamdani = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    # --- 2. GRÁFICA DEL HISTORIAL ---
    conteo_niveles = EvaluacionRiesgo.objects.values('nivel').annotate(total=Count('id'))
    labels = [item['nivel'] for item in conteo_niveles]
    sizes = [item['total'] for item in conteo_niveles]
    
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    colores = {'BAJO': '#10b981', 'MEDIO': '#f59e0b', 'ALTO': '#ef4444', 'CRÍTICO': '#dc2626'}
    color_list = [colores.get(label, '#64748b') for label in labels]
    
    if sum(sizes) > 0:
        ax2.pie(sizes, labels=labels, colors=color_list, autopct='%1.1f%%', startangle=90, textprops={'color':"w", 'fontweight':'bold'})
        ax2.axis('equal')
    else:
        ax2.text(0.5, 0.5, 'Sin datos aún', ha='center', va='center', fontsize=14, color='white')
        
    ax2.set_title('Distribución de Riesgos Evaluados', color='white')
    fig2.patch.set_facecolor('#1e293b')
    
    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png', bbox_inches='tight', facecolor='#1e293b')
    buffer2.seek(0)
    grafica_historial = base64.b64encode(buffer2.getvalue()).decode('utf-8')
    plt.close()

    # Le decimos al navegador que no guarde esta página en caché
    response = render(request, 'web/estadisticas.html', {
        'grafica_mamdani': grafica_mamdani,
        'grafica_historial': grafica_historial,
        'total_evaluaciones': EvaluacionRiesgo.objects.count()
    })
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response