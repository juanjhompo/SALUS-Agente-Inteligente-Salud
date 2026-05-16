# SALUS — Agente Inteligente de Salud 🏥

> Proyecto Final · Asignatura: Inteligencia Artificial  
> Línea 4: Agentes Inteligentes con Tools y Skills  
> Equipo de 3 integrantes

---

## ¿Qué es SALUS?

SALUS (Sistema de Apoyo a la Salud del Usuario) es un agente conversacional impulsado por Gemini 2.5 Flash que orienta a personas en Colombia sobre síntomas, medicamentos, farmacias y emergencias médicas.

El agente **no es un médico**: es una herramienta de triaje y orientación que decide en tiempo real cuándo usar herramientas externas, cuándo aplicar protocolos especializados y cómo mantener una conversación de salud coherente con memoria histórica.

---

## Arquitectura del sistema

```
Usuario
  │
  ▼
SALUS (LLM Gemini 2.5 Flash)
  │  ├─ Skills activas (instrucciones Markdown)
  │  │    ├─ Triaje médico
  │  │    ├─ Privacidad y límites
  │  │    └─ Protocolo de emergencias
  │  │
  │  └─ Razonamiento interno (thinking_budget)
  │
  ├──► evaluar_sintomas()       → triaje básico
  ├──► buscar_farmacia()        → droguerías cercanas
  ├──► agendar_cita()           → agendamiento (simulado)
  ├──► consultar_clima_y_alertas() → API Open-Meteo
  ├──► info_medicamento()       → base de conocimiento
  └──► activar_emergencia()     → protocolo 123
```

---

## Tecnologías

| Componente | Tecnología |
|---|---|
| Modelo LLM | Gemini 2.5 Flash (`google-genai` SDK 2.0) |
| Tool Calling | Función nativa del SDK (automático) |
| API de clima | Open-Meteo (gratuita, sin API key) |
| Entorno | Google Colab (Python 3.10+) |
| Memoria conversacional | `client.chats.create()` del SDK |

---

## Requisitos

```bash
pip install google-genai requests
```

### API Key

1. Ve a [aistudio.google.com](https://aistudio.google.com) y crea tu API key de Gemini.
2. En Google Colab, abre el panel **Secrets** (ícono de llave).
3. Agrega un secreto llamado `GEMINI_API_KEY` con tu clave.
4. Activa el interruptor "Acceso desde el notebook".

---

## Cómo ejecutar

1. Abre `agente_salud_SALUS.py` en Google Colab (sube el archivo o copia las celdas).
2. Ejecuta las celdas en orden: **1 → 2 → 3 → 4 → 5 → 6**.
3. La **celda 6** inicia el chat interactivo.
4. La **celda 7** ejecuta la demostración automática con 5 casos.

---

## Tools implementadas

| Tool | Descripción |
|---|---|
| `evaluar_sintomas(sintomas)` | Triaje básico: emergencia / urgente / consulta programada |
| `buscar_farmacia(ciudad, barrio)` | Farmacias con horarios y servicio a domicilio |
| `agendar_cita(especialidad, fecha, nombre)` | Gestión de citas médicas (prototipo) |
| `consultar_clima_y_alertas(ciudad)` | Clima real vía Open-Meteo + alertas epidemiológicas |
| `info_medicamento(nombre)` | Usos, dosis, contraindicaciones y si requiere receta |
| `activar_emergencia(tipo, ubicacion)` | Protocolo de emergencia + número 123 + primeros auxilios |

---

## Skills implementadas

| Skill | Función |
|---|---|
| `skill_triaje` | Define cuándo y cómo clasificar síntomas por urgencia |
| `skill_privacidad_limites` | Establece qué puede y qué no puede hacer el agente |
| `skill_emergencias` | Protocolo de detección y actuación en crisis médicas |

---

## Casos de prueba

```
1. "Tengo fiebre de 39°C y dolor de cabeza. Vivo en Cali."
   → Usa: evaluar_sintomas() + consultar_clima_y_alertas()

2. "¿Dónde consigo ibuprofeno ahora en Granada, Cali?"
   → Usa: buscar_farmacia()

3. "¿Para qué sirve la amoxicilina?"
   → Usa: info_medicamento()

4. "Quiero cita con medicina general para mañana. Soy Carlos Pérez."
   → Usa: agendar_cita()

5. "Mi mamá tiene dolor en el pecho y no respira bien."
   → Usa: activar_emergencia() (protocolo inmediato)
```

---

## Criterios de evaluación cubiertos

| Criterio | Cómo se cumple |
|---|---|
| Solidez Técnica (40%) | 6 tools reales, 3 skills, thinking_config, SDK 2.0 |
| Funcionalidad (30%) | 5 casos de uso en demo automática, sin errores |
| Calidad del Código (15%) | Notebook organizado por celdas, comentado, README |
| Comunicación (15%) | Pitch de 8 min dividido entre 3 integrantes |

---

## Limitaciones y trabajo futuro

- Las farmacias y citas son datos simulados (prototipo). En producción: Google Places API + sistema real de EPS.
- La base de medicamentos cubre solo los más comunes. Se puede ampliar con OpenFDA API.
- No maneja imágenes (fotos de heridas, recetas). Posible extensión con Gemini Vision.

---

## ⚠️ Aviso importante

SALUS **no reemplaza la atención médica profesional**. Es una herramienta de orientación y triaje. Ante cualquier emergencia, llame al **123**.
