from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .motor_empresarial import evaluar_riesgo_empresa
from .motor_urls import evaluar_url # <-- IMPORTANTE: Esta línea conecta el detector
from .models import EvaluacionRiesgo
from .models import EvaluacionRiesgo, AnalisisURL # <-- Agrega AnalisisURL
from django.contrib.auth.models import User # <-- Agrega esto arriba

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