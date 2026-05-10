# Plan de Migración: MAGI — Claude Code a Gemini CLI Extension

Este documento detalla el plan estratégico para migrar el sistema **MAGI** (https://github.com/BolivarTech/magi) de su implementación actual como plugin de Claude Code a una **Gemini CLI Extension** utilizando el estándar de **Agent Skills**.

---

## 1. Nueva Estructura del Repositorio

La migración implica reorganizar la estructura para cumplir con el estándar de Gemini CLI, manteniendo la lógica central de Python.

```text
magi-gemini/
├── .geminiignore          # Similar a .gitignore, define qué no subir
├── gemini-extension.json  # Manifiesto global de la extensión
├── README.md              # Documentación para el usuario
└── skills/
    └── magi/              # Carpeta raíz de la Skill
        ├── SKILL.md       # El "cerebro" y manifiesto de la Skill
        ├── agents/        # Prompts originales (Melchior, Balthasar, Caspar)
        ├── scripts/       # Lógica Python (run_magi.py, consensus.py, etc.)
        ├── tests/         # Suite de pruebas adaptada
        └── pyproject.toml # Dependencias de Python
```

---

## 2. Cambios en la Lógica Central (Python)

### A. Sustitución del Engine (de `claude -p` a `Gemini API`)
Actualmente, `run_magi.py` invoca el CLI de Claude. La versión para Gemini debe:
*   Utilizar la librería `google-generativeai`.
*   Implementar llamadas asíncronas (`AsyncGenerateContentResponse`).
*   **Ventaja:** No depende de que el usuario tenga un CLI instalado; la API se maneja internamente.

### B. Mejora del Parsing (JSON Mode)
En lugar de depender de regex para extraer JSON de bloques de texto (etiquetas `<verdict>`), configuraremos Gemini para usar **Structured Outputs**:
*   Definir un `ResponseSchema` para los veredictos.
*   Esto elimina el 90% del código de validación y parsing actual en `validate.py` y `parse_agent_output.py`.

---

## 3. Implementación de `SKILL.md`

Este es el archivo que Gemini CLI leerá para entender cuándo y cómo usar MAGI.

```markdown
---
name: magi-analysis
description: Multi-perspective agent analysis (Melchior, Balthasar, Caspar) for complex decision making and code review.
---
# MAGI Analysis System

Usa esta skill cuando el usuario requiera una revisión técnica profunda, una evaluación de riesgos o una decisión arquitectónica compleja.

## Workflow
1. **Analizar Contexto:** Lee los archivos relevantes del proyecto.
2. **Ejecutar Agentes:** Invoca `python3 scripts/run_magi.py` pasando el contexto recolectado.
3. **Reportar:** Presenta el reporte Markdown generado por el sistema de consenso.

## Seguridad
- No compartas secretos de entorno.
- El script de Python requiere una API KEY de Google en la variable `GOOGLE_API_KEY`.
```

---

## 4. Adaptación del Manifiesto (`gemini-extension.json`)

Sustituye al antiguo `.claude-plugin/manifest.json`.

```json
{
  "name": "magi",
  "version": "1.0.0",
  "description": "MAGI Multi-Perspective Analysis for Gemini CLI",
  "author": "BolivarTech",
  "skills": ["skills/magi"],
  "contributions": {
    "commands": [
      {
        "name": "magi",
        "description": "Ejecuta un análisis MAGI sobre el estado actual"
      }
    ]
  }
}
```

---

## 5. Cronograma de Ejecución

1.  **Fase 1: Preparación (Día 1)**
    *   Clonar el repo original.
    *   Crear la nueva estructura de carpetas.
2.  **Fase 2: Refactor de Motor (Día 2-3)**
    *   Migrar `run_magi.py` al SDK de Google Generative AI.
    *   Adaptar los prompts de los agentes en `/agents` para optimizar el uso de Gemini 1.5 Pro.
3.  **Fase 3: Integración con Gemini CLI (Día 4)**
    *   Escribir el `SKILL.md`.
    *   Configurar el manejo de dependencias de Python para que se instalen automáticamente.
4.  **Fase 4: Validación y Pruebas (Día 5)**
    *   Ejecutar la suite de tests (`pytest`) simulando respuestas de la API de Gemini.
    *   Prueba de instalación local con `gemini skills link`.

---

## 6. Ventajas Clave post-Migración
*   **Contexto Masivo:** Capacidad de analizar PRs gigantes o arquitecturas completas (1M+ tokens).
*   **Velocidad:** Las llamadas paralelas vía API son significativamente más rápidas que lanzar múltiples procesos de un CLI externo.
*   **Estabilidad:** El uso de esquemas JSON nativos reduce errores de comunicación entre agentes.
