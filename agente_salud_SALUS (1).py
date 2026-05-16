# ============================================================
# PROYECTO FINAL - INTELIGENCIA ARTIFICIAL
# AGENTE INTELIGENTE CON TOOLS Y SKILLS
# SALUS - Sistema de Apoyo a la Salud del Usuario
# ============================================================
# Línea de Proyecto: 4 - Agentes Inteligentes con Tools y Skills
# Entorno: Google Colab
# Modelo: Gemini 2.5 Flash (google-genai SDK 2.0)
# ============================================================


# ╔══════════════════════════════════════════════════════════╗
# ║  CELDA 1 - Instalación de dependencias                  ║
# ╚══════════════════════════════════════════════════════════╝

# !pip install -q google-genai requests


# ╔══════════════════════════════════════════════════════════╗
# ║  CELDA 2 - Importaciones y configuración del cliente    ║
# ╚══════════════════════════════════════════════════════════╝

from google import genai
from google.genai import types
from google.colab import userdata
import requests
import json
from datetime import datetime

# Cliente Gemini autenticado con secreto de Colab
# (Configura tu API key en el panel Secrets de Colab con el nombre 'GEMINI_API_KEY')
client = genai.Client(api_key=userdata.get('GEMINI_API_KEY'))

print("✅ Cliente Gemini inicializado correctamente")
print("Modelos disponibles con soporte de tools:")
for m in client.models.list():
    if 'generateContent' in m.supported_actions:
        print(f"  - {m.name}")


# ╔══════════════════════════════════════════════════════════╗
# ║  CELDA 3 - Definición de Tools (Herramientas)           ║
# ╚══════════════════════════════════════════════════════════╝
# Las tools son funciones Python que el LLM puede invocar
# para obtener información real del mundo exterior.
# El modelo decide CUÁNDO y CUÁLES usar según la consulta.

# ── Tool 1: Evaluación de síntomas ──────────────────────────
def evaluar_sintomas(sintomas: str) -> str:
    """
    Realiza un triaje básico de síntomas para orientar al usuario.
    NO reemplaza el diagnóstico médico profesional.

    Args:
        sintomas: Descripción de los síntomas que presenta el usuario.

    Returns:
        Nivel de urgencia y recomendación de acción.
    """
    # Base de conocimiento de triaje (simulada para el prototipo)
    sintomas_lower = sintomas.lower()

    # Síntomas de emergencia - requieren atención inmediata
    emergencia = [
        "dolor en el pecho", "dificultad para respirar", "pérdida de conciencia",
        "convulsión", "sangrado intenso", "parálisis", "habla trabada",
        "labios azules", "vómito con sangre"
    ]

    # Síntomas de alta prioridad - atención en menos de 4 horas
    alta_prioridad = [
        "fiebre alta", "temperatura mayor", "dolor intenso", "fractura",
        "corte profundo", "reacción alérgica", "vómito persistente",
        "deshidratación", "infección visible"
    ]

    # Síntomas de consulta programada
    consulta_normal = [
        "tos", "gripe", "dolor de cabeza", "cansancio", "mareo leve",
        "dolor muscular", "estreñimiento", "insomnio", "ansiedad", "resfriado"
    ]

    # Clasificar por urgencia
    for s in emergencia:
        if s in sintomas_lower:
            return (
                "🚨 NIVEL: EMERGENCIA\n"
                "Acción requerida: Llamar al 123 (emergencias Colombia) o ir a urgencias INMEDIATAMENTE.\n"
                f"Síntoma detectado de alto riesgo: '{s}'.\n"
                "No conduzca solo. Solicite ayuda ahora."
            )

    for s in alta_prioridad:
        if s in sintomas_lower:
            return (
                "⚠️ NIVEL: URGENTE\n"
                "Acción requerida: Acudir a urgencias en las próximas 2-4 horas.\n"
                f"Síntoma que requiere evaluación pronta: '{s}'.\n"
                "Lleve documento de identidad y carné de EPS."
            )

    for s in consulta_normal:
        if s in sintomas_lower:
            return (
                "🟡 NIVEL: CONSULTA PROGRAMADA\n"
                "Acción sugerida: Agendar cita con médico general en los próximos días.\n"
                "Puede aliviar síntomas con reposo, hidratación y medicamentos de venta libre según indicación.\n"
                "Si los síntomas empeoran, consulte urgencias."
            )

    return (
        "ℹ️ NIVEL: INFORMACIÓN INSUFICIENTE\n"
        "No pude clasificar los síntomas con precisión.\n"
        "Por favor describe con más detalle lo que sientes.\n"
        "Ejemplo: 'tengo fiebre de 39°C desde hace dos días y dolor de garganta'."
    )


# ── Tool 2: Buscar farmacias cercanas ───────────────────────
def buscar_farmacia(ciudad: str, barrio: str = "") -> str:
    """
    Busca farmacias y droguerías disponibles en una ubicación de Colombia.

    Args:
        ciudad: Ciudad donde buscar (ej: 'Cali', 'Bogotá', 'Medellín').
        barrio: Barrio o zona específica (opcional).

    Returns:
        Lista de farmacias con información de contacto y horarios.
    """
    # Base de datos simulada de farmacias (en producción se usaría Google Places API)
    farmacias_db = {
        "cali": [
            {
                "nombre": "Droguería Cruz Verde - Chipichape",
                "direccion": "Cra 100 # 11-60, Centro Comercial Chipichape",
                "telefono": "(602) 668-0000",
                "horario": "Lunes a Domingo: 8am - 10pm",
                "servicio_domicilio": True
            },
            {
                "nombre": "Farmatodo - Granada",
                "direccion": "Av. 9N # 14-55, Granada",
                "telefono": "(602) 882-1234",
                "horario": "24 horas",
                "servicio_domicilio": True
            },
            {
                "nombre": "Droguería La Rebaja - Centro",
                "direccion": "Cra 9 # 10-42, Centro",
                "telefono": "(602) 889-5678",
                "horario": "Lunes a Sábado: 7am - 9pm",
                "servicio_domicilio": False
            }
        ],
        "bogota": [
            {
                "nombre": "Droguería Colsubsidio - Chapinero",
                "direccion": "Cra 13 # 59-18, Chapinero",
                "telefono": "(601) 307-0700",
                "horario": "24 horas",
                "servicio_domicilio": True
            },
            {
                "nombre": "Farmatodo - Usaquén",
                "direccion": "Cra 7A # 123-45, Usaquén",
                "telefono": "(601) 215-9000",
                "horario": "8am - 11pm todos los días",
                "servicio_domicilio": True
            }
        ],
        "medellin": [
            {
                "nombre": "Droguería Éxito - El Poblado",
                "direccion": "Cra 43A # 1-50, El Poblado",
                "telefono": "(604) 322-4000",
                "horario": "7am - 10pm todos los días",
                "servicio_domicilio": True
            }
        ]
    }

    ciudad_lower = ciudad.lower().strip()
    farmacias = farmacias_db.get(ciudad_lower, [])

    if not farmacias:
        return (
            f"No tengo información de farmacias en '{ciudad}' en este momento.\n"
            "Te recomiendo buscar en Google Maps 'droguerías cerca de mí' o llamar a tu EPS."
        )

    # Filtrar por barrio si se especificó
    if barrio:
        barrio_lower = barrio.lower()
        farmacias_filtradas = [f for f in farmacias if barrio_lower in f["direccion"].lower()]
        if farmacias_filtradas:
            farmacias = farmacias_filtradas

    resultado = f"💊 Farmacias disponibles en {ciudad.title()}"
    if barrio:
        resultado += f" - {barrio.title()}"
    resultado += ":\n\n"

    for i, farm in enumerate(farmacias, 1):
        domicilio = "✅ Domicilio disponible" if farm["servicio_domicilio"] else "❌ Sin domicilio"
        resultado += (
            f"{i}. {farm['nombre']}\n"
            f"   📍 {farm['direccion']}\n"
            f"   📞 {farm['telefono']}\n"
            f"   🕐 {farm['horario']}\n"
            f"   {domicilio}\n\n"
        )

    return resultado.strip()


# ── Tool 3: Agendar cita médica ──────────────────────────────
def agendar_cita(especialidad: str, fecha_preferida: str, nombre_paciente: str) -> str:
    """
    Simula el agendamiento de una cita médica en el sistema de salud.

    Args:
        especialidad: Tipo de médico requerido (ej: 'medicina general', 'pediatría').
        fecha_preferida: Fecha deseada para la cita (ej: 'mañana', '2025-06-15').
        nombre_paciente: Nombre completo del paciente.

    Returns:
        Confirmación de la cita agendada con número de referencia.
    """
    import random
    import string

    # Especialidades disponibles y sus tiempos de espera simulados
    especialidades = {
        "medicina general": {"disponible": True, "espera_dias": 1},
        "pediatría": {"disponible": True, "espera_dias": 2},
        "cardiología": {"disponible": True, "espera_dias": 7},
        "dermatología": {"disponible": True, "espera_dias": 5},
        "ginecología": {"disponible": True, "espera_dias": 4},
        "ortopedia": {"disponible": True, "espera_dias": 6},
        "psicología": {"disponible": True, "espera_dias": 3},
        "nutrición": {"disponible": True, "espera_dias": 2},
        "urgencias": {"disponible": True, "espera_dias": 0}
    }

    esp_lower = especialidad.lower().strip()

    # Buscar especialidad más cercana
    encontrada = None
    for esp in especialidades:
        if esp in esp_lower or esp_lower in esp:
            encontrada = esp
            break

    if not encontrada:
        return (
            f"La especialidad '{especialidad}' no está disponible en nuestro sistema.\n"
            "Especialidades disponibles: medicina general, pediatría, cardiología, "
            "dermatología, ginecología, ortopedia, psicología, nutrición.\n"
            "Para urgencias, dirígete directamente a la sala de urgencias de tu IPS."
        )

    info = especialidades[encontrada]
    # Generar número de referencia único
    ref = "SALUS-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    if info["espera_dias"] == 0:
        tiempo_str = "Inmediatamente (urgencias)"
        hora = "Atención inmediata"
    elif info["espera_dias"] == 1:
        tiempo_str = "Mañana"
        hora = "9:00 AM"
    else:
        tiempo_str = f"En aproximadamente {info['espera_dias']} días hábiles"
        hora = "10:30 AM"

    return (
        f"✅ CITA AGENDADA EXITOSAMENTE\n\n"
        f"📋 Número de referencia: {ref}\n"
        f"👤 Paciente: {nombre_paciente}\n"
        f"🩺 Especialidad: {encontrada.title()}\n"
        f"📅 Disponibilidad: {tiempo_str}\n"
        f"🕐 Hora estimada: {hora}\n\n"
        f"📌 INSTRUCCIONES:\n"
        f"- Lleve su carné de EPS y documento de identidad\n"
        f"- Llegue 15 minutos antes de la hora asignada\n"
        f"- Si no puede asistir, cancele con al menos 24 horas de anticipación\n"
        f"- Guarde el número de referencia: {ref}"
    )


# ── Tool 4: Consulta de clima y alertas epidemiológicas ──────
def consultar_clima_y_alertas(ciudad: str) -> str:
    """
    Consulta el clima actual de una ciudad colombiana y genera alertas
    epidemiológicas relevantes basadas en las condiciones meteorológicas.

    Args:
        ciudad: Nombre de la ciudad colombiana (ej: 'Cali', 'Bogotá').

    Returns:
        Clima actual y alertas de salud asociadas a las condiciones.
    """
    # Coordenadas de ciudades principales de Colombia
    coordenadas = {
        "cali": (-3.4516, -76.5320),
        "bogota": (4.7110, -74.0721),
        "medellin": (6.2442, -75.5812),
        "barranquilla": (10.9685, -74.7813),
        "cartagena": (10.3910, -75.4794),
        "bucaramanga": (7.1254, -73.1198),
        "pereira": (4.8143, -75.6946),
        "manizales": (5.0689, -75.5174)
    }

    ciudad_lower = ciudad.lower().strip()
    coords = coordenadas.get(ciudad_lower)

    if not coords:
        return (
            f"No tengo coordenadas para '{ciudad}'.\n"
            "Ciudades disponibles: Cali, Bogotá, Medellín, Barranquilla, "
            "Cartagena, Bucaramanga, Pereira, Manizales."
        )

    lat, lon = coords

    try:
        # Consulta a Open-Meteo (API gratuita, sin API key)
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&hourly=relative_humidity_2m,uv_index"
            f"&forecast_days=1"
        )
        resp = requests.get(url, timeout=10).json()
        clima = resp.get("current_weather", {})

        temp = clima.get("temperature", "N/D")
        viento = clima.get("windspeed", "N/D")
        codigo = clima.get("weathercode", -1)

        # Decodificar código WMO de clima
        codigos_clima = {
            0: "Cielo despejado ☀️",
            1: "Principalmente despejado 🌤️",
            2: "Parcialmente nublado ⛅",
            3: "Nublado ☁️",
            45: "Niebla 🌫️",
            51: "Llovizna ligera 🌦️",
            61: "Lluvia leve 🌧️",
            63: "Lluvia moderada 🌧️",
            65: "Lluvia intensa 🌧️",
            80: "Chubascos 🌦️",
            95: "Tormenta eléctrica ⛈️"
        }
        descripcion = codigos_clima.get(codigo, "Condiciones variables 🌤️")

        # Generar alertas epidemiológicas según clima
        alertas = []
        if isinstance(temp, (int, float)):
            if temp > 30:
                alertas.append("🌡️ Calor intenso: riesgo de deshidratación y golpe de calor. Tome abundante agua.")
            if temp < 15:
                alertas.append("🧥 Temperatura baja: mayor riesgo de infecciones respiratorias. Abrígese bien.")
        if isinstance(viento, (int, float)) and viento > 30:
            alertas.append("💨 Viento fuerte: riesgo de alergias por partículas en el aire.")
        if codigo in [61, 63, 65, 80]:
            alertas.append("🦟 Lluvia: aumento del riesgo de dengue y enfermedades transmitidas por mosquitos.")
        if codigo in [95]:
            alertas.append("⛈️ Tormenta: evite zonas abiertas y árboles. Riesgo de accidentes.")

        resultado = (
            f"🌍 Clima actual en {ciudad.title()}:\n"
            f"   Condición: {descripcion}\n"
            f"   Temperatura: {temp}°C\n"
            f"   Viento: {viento} km/h\n\n"
        )

        if alertas:
            resultado += "⚕️ Alertas de salud:\n"
            for alerta in alertas:
                resultado += f"   {alerta}\n"
        else:
            resultado += "✅ Sin alertas de salud especiales para las condiciones actuales."

        return resultado

    except Exception as e:
        return f"No pude obtener el clima para {ciudad} en este momento. Error: {str(e)}"


# ── Tool 5: Información de medicamentos ─────────────────────
def info_medicamento(nombre_medicamento: str) -> str:
    """
    Proporciona información básica sobre medicamentos de uso común:
    usos, contraindicaciones y advertencias importantes.
    NO reemplaza la prescripción médica.

    Args:
        nombre_medicamento: Nombre del medicamento a consultar (ej: 'ibuprofeno').

    Returns:
        Información general del medicamento con advertencias.
    """
    medicamentos = {
        "ibuprofeno": {
            "tipo": "Antiinflamatorio no esteroideo (AINE)",
            "usos": "Dolor, fiebre, inflamación, artritis",
            "dosis_adulto": "200-400mg cada 6-8 horas con alimentos",
            "contraindicaciones": [
                "Úlcera gástrica activa",
                "Insuficiencia renal grave",
                "Embarazo (3er trimestre)",
                "Alergia a AINEs o aspirina"
            ],
            "advertencias": "Tome siempre con alimentos. No exceda 1200mg/día sin supervisión médica.",
            "requiere_receta": False
        },
        "acetaminofen": {
            "tipo": "Analgésico y antipirético",
            "usos": "Dolor leve a moderado, fiebre",
            "dosis_adulto": "500-1000mg cada 4-6 horas",
            "contraindicaciones": [
                "Insuficiencia hepática grave",
                "Consumo excesivo de alcohol"
            ],
            "advertencias": "No exceda 4000mg/día. Revise otros medicamentos que puedan contenerlo.",
            "requiere_receta": False
        },
        "paracetamol": {
            "tipo": "Analgésico y antipirético",
            "usos": "Dolor leve a moderado, fiebre",
            "dosis_adulto": "500-1000mg cada 4-6 horas",
            "contraindicaciones": [
                "Insuficiencia hepática grave",
                "Consumo excesivo de alcohol"
            ],
            "advertencias": "Es el mismo principio activo que el Acetaminofén. No exceda 4000mg/día.",
            "requiere_receta": False
        },
        "amoxicilina": {
            "tipo": "Antibiótico betalactámico",
            "usos": "Infecciones bacterianas: respiratorias, urinarias, dentales",
            "dosis_adulto": "500mg cada 8 horas por 7-10 días (según prescripción)",
            "contraindicaciones": [
                "Alergia a penicilinas",
                "Mononucleosis infecciosa"
            ],
            "advertencias": "REQUIERE PRESCRIPCIÓN MÉDICA. Complete el tratamiento completo aunque mejore.",
            "requiere_receta": True
        },
        "loratadina": {
            "tipo": "Antihistamínico de segunda generación",
            "usos": "Alergias, rinitis alérgica, urticaria",
            "dosis_adulto": "10mg una vez al día",
            "contraindicaciones": [
                "Hipersensibilidad a la loratadina"
            ],
            "advertencias": "No produce somnolencia significativa. Puede tomarse en el día.",
            "requiere_receta": False
        },
        "metformina": {
            "tipo": "Antidiabético biguanida",
            "usos": "Diabetes tipo 2, síndrome de ovario poliquístico",
            "dosis_adulto": "500-2000mg/día con comidas (según prescripción)",
            "contraindicaciones": [
                "Insuficiencia renal",
                "Insuficiencia hepática",
                "Alcoholismo"
            ],
            "advertencias": "REQUIERE PRESCRIPCIÓN MÉDICA. Control periódico de función renal.",
            "requiere_receta": True
        }
    }

    med_lower = nombre_medicamento.lower().strip()

    # Buscar coincidencia exacta o parcial
    info = None
    for nombre, datos in medicamentos.items():
        if nombre in med_lower or med_lower in nombre:
            info = datos
            nombre_encontrado = nombre
            break

    if not info:
        return (
            f"No tengo información detallada sobre '{nombre_medicamento}'.\n"
            "Medicamentos disponibles en mi base de datos: "
            "ibuprofeno, acetaminofén/paracetamol, amoxicilina, loratadina, metformina.\n"
            "Para cualquier medicamento, consulta siempre a tu médico o farmacéutico."
        )

    receta_str = "⚠️ REQUIERE RECETA MÉDICA" if info["requiere_receta"] else "✅ Venta libre (sin receta)"
    contra_str = "\n   - ".join(info["contraindicaciones"])

    return (
        f"💊 {nombre_encontrado.upper()}\n"
        f"   Tipo: {info['tipo']}\n"
        f"   Usos: {info['usos']}\n"
        f"   Dosis adulto: {info['dosis_adulto']}\n"
        f"   {receta_str}\n\n"
        f"❌ Contraindicaciones:\n   - {contra_str}\n\n"
        f"⚠️ Advertencias: {info['advertencias']}\n\n"
        f"⚕️ IMPORTANTE: Esta información es orientativa. "
        f"Siempre consulte a su médico o farmacéutico antes de iniciar un tratamiento."
    )


# ── Tool 6: Activar protocolo de emergencia ─────────────────
def activar_emergencia(tipo_emergencia: str, ubicacion: str) -> str:
    """
    Activa el protocolo de emergencia médica y proporciona los números
    de contacto y pasos inmediatos según el tipo de emergencia.

    Args:
        tipo_emergencia: Descripción de la emergencia (ej: 'infarto', 'accidente').
        ubicacion: Dirección o lugar donde ocurre la emergencia.

    Returns:
        Protocolo de actuación y números de emergencia.
    """
    timestamp = datetime.now().strftime("%H:%M - %d/%m/%Y")

    return (
        f"🚨 PROTOCOLO DE EMERGENCIA ACTIVADO\n"
        f"📍 Ubicación reportada: {ubicacion}\n"
        f"🆘 Tipo: {tipo_emergencia}\n"
        f"🕐 Hora: {timestamp}\n\n"
        f"═══ LLAME AHORA ═══\n"
        f"🆘 Emergencias Colombia: 123\n"
        f"🚑 Cruz Roja: 132\n"
        f"🚒 Bomberos: 119\n"
        f"👮 Policía: 112\n\n"
        f"═══ MIENTRAS LLEGA LA AYUDA ═══\n"
        f"1. Mantenga la calma y no mueva al paciente si hay trauma\n"
        f"2. Asegure que el paciente pueda respirar\n"
        f"3. Si hay sangrado: presione firmemente con tela limpia\n"
        f"4. Si no hay pulso y sabe RCP: inicie compresiones (30 compresiones / 2 respiraciones)\n"
        f"5. Permanezca en línea con el operador de emergencias\n"
        f"6. Envíe a alguien a esperar la ambulancia en la entrada\n\n"
        f"⚠️ NO administre medicamentos sin indicación del operador médico."
    )


print("✅ Las 6 tools del agente SALUS están definidas:")
print("   1. evaluar_sintomas()")
print("   2. buscar_farmacia()")
print("   3. agendar_cita()")
print("   4. consultar_clima_y_alertas()")
print("   5. info_medicamento()")
print("   6. activar_emergencia()")


# ╔══════════════════════════════════════════════════════════╗
# ║  CELDA 4 - Definición de Skills (instrucciones)         ║
# ╚══════════════════════════════════════════════════════════╝
# Las skills son bloques de instrucciones en Markdown que se
# inyectan en el contexto del agente para guiar su razonamiento
# ante situaciones específicas.

skill_triaje = """
## SKILL: PROTOCOLO DE TRIAJE MÉDICO

### Reglas de clasificación:
1. **EMERGENCIA** (actúa de inmediato):
   - Dolor en el pecho o brazo izquierdo → posible infarto
   - Dificultad respiratoria grave → llamar 123 YA
   - Pérdida de conciencia → activar_emergencia() inmediatamente
   - Convulsiones activas → activar_emergencia()
   - Sangrado que no cede → emergencia

2. **URGENTE** (atención en 2-4 horas):
   - Fiebre > 39°C en adultos, > 38°C en niños
   - Dolor intenso (>7/10 en escala de dolor)
   - Herida que requiere sutura
   - Vómito o diarrea con signos de deshidratación

3. **CONSULTA PROGRAMADA** (próximos días):
   - Síntomas leves que no interfieren con actividad diaria
   - Condiciones crónicas en seguimiento
   - Revisiones preventivas

### Comportamiento esperado:
- SIEMPRE usa evaluar_sintomas() antes de emitir cualquier recomendación.
- Si detectas emergencia, usa activar_emergencia() INMEDIATAMENTE, luego explica.
- NUNCA minimices síntomas que puedan ser graves.
- Recuerda siempre que NO eres médico y que el usuario debe consultar a un profesional.
"""

skill_privacidad_limites = """
## SKILL: PRIVACIDAD Y LÍMITES MÉDICO-LEGALES

### Lo que PUEDES hacer:
- Orientar sobre síntomas y urgencia
- Buscar farmacias y horarios
- Agendar citas (simulado en prototipo)
- Informar sobre medicamentos de venta libre
- Dar primeros auxilios básicos en emergencias
- Consultar clima y alertas epidemiológicas

### Lo que NO puedes hacer:
- Diagnosticar enfermedades
- Prescribir medicamentos (solo informas sobre ellos)
- Dar dosis específicas sin consultar al médico
- Garantizar diagnósticos basados en síntomas

### Privacidad:
- No solicites datos sensibles innecesarios (número de documento, EPS, etc.)
- Si el usuario da datos personales, úsalos solo para el contexto inmediato
- Recuerda siempre que esta es una herramienta de apoyo, no un sistema médico oficial

### Tono:
- Empático pero preciso
- Nunca alarmista innecesariamente
- Siempre tranquilizador en emergencias reales: "ayuda está en camino"
"""

skill_emergencias = """
## SKILL: MANEJO DE EMERGENCIAS MÉDICAS

### Protocolo de detección:
Palabras clave que SIEMPRE desencadenan activar_emergencia():
- "me estoy muriendo", "no puedo respirar", "me desmayé"
- "accidente", "caída grave", "trauma fuerte"
- "sangre mucha", "quemadura grave"
- "envenenamiento", "sobredosis"

### Protocolo de respuesta:
1. Usa activar_emergencia() con el tipo y la ubicación del usuario
2. Proporciona los números de emergencia PRIMERO
3. Da instrucciones de primeros auxilios claras y numeradas
4. Mantén al usuario calmado con mensajes tranquilizadores
5. No hagas preguntas largas: tiempo es crítico

### Derivación hospitalaria:
Indica siempre la urgencia de ir al hospital cuando:
- Síntomas cardiovasculares (pecho, brazo, mandíbula)
- Síntomas neurológicos (cara caída, confusión súbita, debilidad unilateral)
- Trauma por accidente
- Intoxicación o sobredosis

### Mensaje final en emergencias:
Cierra siempre con: "El número de emergencias en Colombia es el 123. ¿Hay alguien contigo ahora mismo?"
"""

print("✅ Skills definidas:")
print("   - skill_triaje: protocolo de clasificación de urgencias")
print("   - skill_privacidad_limites: límites éticos y legales del agente")
print("   - skill_emergencias: manejo de emergencias con protocolo de actuación")


# ╔══════════════════════════════════════════════════════════╗
# ║  CELDA 5 - Configuración del agente SALUS               ║
# ╚══════════════════════════════════════════════════════════╝

# Instrucción maestra del sistema
instruccion_sistema = f"""
Eres SALUS, un agente de inteligencia artificial especializado en orientación de salud
para usuarios en Colombia. Tienes un tono cálido, empático y profesional.

════════════════════════════════════
HERRAMIENTAS DISPONIBLES:
════════════════════════════════════
Tienes acceso a 6 herramientas. Úsalas activamente:

1. evaluar_sintomas(sintomas) → Triaje básico de urgencia
2. buscar_farmacia(ciudad, barrio) → Droguerías cercanas
3. agendar_cita(especialidad, fecha_preferida, nombre_paciente) → Programar cita
4. consultar_clima_y_alertas(ciudad) → Clima + alertas epidemiológicas
5. info_medicamento(nombre_medicamento) → Usos y contraindicaciones
6. activar_emergencia(tipo_emergencia, ubicacion) → Protocolo de emergencia

════════════════════════════════════
INSTRUCCIONES DE COMPORTAMIENTO:
════════════════════════════════════

{skill_triaje}

{skill_privacidad_limites}

{skill_emergencias}

════════════════════════════════════
FLUJO INTELIGENTE:
════════════════════════════════════
- Cuando el usuario mencione síntomas → SIEMPRE evalua_sintomas() primero
- Cuando pregunte por medicamentos → info_medicamento() con advertencia de consulta médica
- Cuando busque farmacia → buscar_farmacia() con ciudad y barrio si los da
- Cuando quiera cita → agendar_cita() con los datos del usuario
- Cuando haya emergencia → activar_emergencia() INMEDIATAMENTE, luego explica
- Combina herramientas cuando tenga sentido (ej: síntomas + clima si hay alerta epidémica)

════════════════════════════════════
LIMITACIONES IMPORTANTES:
════════════════════════════════════
- NO eres médico. NUNCA diagnostiques ni prescribas.
- SIEMPRE cierra con "¿Hay algo más en lo que pueda ayudarte?"
- En emergencias, prioriza la seguridad del usuario sobre cualquier otra respuesta.
- Si no tienes información, dilo claramente en lugar de inventar.
"""

# Lista de herramientas disponibles para el agente
herramientas_salus = [
    evaluar_sintomas,
    buscar_farmacia,
    agendar_cita,
    consultar_clima_y_alertas,
    info_medicamento,
    activar_emergencia
]

# Configuración de generación del modelo
config_salus = types.GenerateContentConfig(
    system_instruction=instruccion_sistema,
    tools=herramientas_salus,
    temperature=0.4,        # Bajo para respuestas médicas más precisas y consistentes
    thinking_config=types.ThinkingConfig(
        include_thoughts=False,  # Ocultar razonamiento interno al usuario
        thinking_budget=1000     # Presupuesto de razonamiento para decisiones complejas
    )
)

print("✅ Agente SALUS configurado con:")
print(f"   - Modelo: gemini-2.5-flash-preview-05-20")
print(f"   - Temperature: 0.4 (respuestas precisas)")
print(f"   - Herramientas: {len(herramientas_salus)}")
print(f"   - Skills activas: triaje, privacidad, emergencias")


# ╔══════════════════════════════════════════════════════════╗
# ║  CELDA 6 - Ejecución del agente conversacional          ║
# ╚══════════════════════════════════════════════════════════╝

MODEL_ID = "gemini-2.5-flash-preview-05-20"

# Crear sesión de chat (mantiene historial automáticamente)
chat_salus = client.chats.create(model=MODEL_ID, config=config_salus)

print("\n" + "═" * 60)
print("  🏥 SALUS - Sistema de Apoyo a la Salud del Usuario")
print("  Agente Inteligente con Tools y Skills | IA 2025")
print("═" * 60)
print("  Escribe 'salir' para terminar | 'historial' para ver el chat")
print("═" * 60 + "\n")

while True:
    try:
        usuario_input = input("Tú: ").strip()
    except KeyboardInterrupt:
        print("\n\nSALUS: Sesión finalizada. ¡Cuídate mucho! 🏥")
        break

    if not usuario_input:
        continue

    if usuario_input.lower() in ["salir", "exit", "chau", "adios", "bye"]:
        print("\nSALUS: ¡Hasta pronto! Recuerda: ante cualquier duda médica, consulta a un profesional. 🏥")
        break

    if usuario_input.lower() == "historial":
        print("\n--- HISTORIAL DE CONVERSACIÓN ---")
        for msg in chat_salus.get_history():
            rol = "Tú" if msg.role == "user" else "SALUS"
            for part in msg.parts:
                if hasattr(part, 'text') and part.text:
                    print(f"{rol}: {part.text[:100]}...")
        print("--- FIN DEL HISTORIAL ---\n")
        continue

    # Enviar mensaje al agente (el SDK maneja automáticamente el tool calling)
    response = chat_salus.send_message(usuario_input)
    print(f"\nSALUS: {response.text}\n")
    print("-" * 60)


# ╔══════════════════════════════════════════════════════════╗
# ║  CELDA 7 - Casos de prueba para la demostración         ║
# ╚══════════════════════════════════════════════════════════╝
# Ejecuta esta celda para ver al agente en acción de forma
# automática con 5 casos representativos.

print("\n" + "═" * 60)
print("  DEMOSTRACIÓN AUTOMÁTICA - CASOS DE USO")
print("═" * 60)

casos_prueba = [
    # Caso 1: Triaje de síntomas + clima
    "Tengo fiebre de 39°C y dolor de cabeza intenso desde ayer. Vivo en Cali.",

    # Caso 2: Búsqueda de farmacia
    "¿Dónde puedo conseguir ibuprofeno ahora? Estoy en el barrio Granada, Cali.",

    # Caso 3: Información de medicamento
    "¿Para qué sirve la amoxicilina y la puedo tomar sin receta?",

    # Caso 4: Agendamiento de cita con contexto previo (prueba de memoria)
    "Quiero agendar una cita con medicina general para mañana. Me llamo Carlos Pérez.",

    # Caso 5: Emergencia (activar protocolo)
    "Mi mamá está con dolor en el pecho y no puede respirar bien. Estamos en Av. 5N #20-30, Cali.",
]

chat_demo = client.chats.create(model=MODEL_ID, config=config_salus)

for i, caso in enumerate(casos_prueba, 1):
    print(f"\n{'─'*60}")
    print(f"CASO {i}: {caso}")
    print(f"{'─'*60}")
    resp = chat_demo.send_message(caso)
    print(f"SALUS: {resp.text}")

print("\n" + "═" * 60)
print("  ✅ Demostración completada")
print("  El agente usó tools y mantuvo contexto entre mensajes")
print("═" * 60)
