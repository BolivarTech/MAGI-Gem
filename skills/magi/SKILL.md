---
name: magi-analysis
description: Multi-perspective agent analysis (Melchior, Balthasar, Caspar) for complex decision making and code review.
---
# MAGI Analysis System

Usa esta skill cuando el usuario requiera una revisión técnica profunda, una evaluación de riesgos o una decisión arquitectónica compleja.

## Workflow
1. **Analizar Contexto:** Lee los archivos relevantes del proyecto.
2. **Ejecutar Agentes:** Invoca `python3 skills/magi/scripts/run_magi.py` pasando el contexto recolectado.
3. **Reportar:** Presenta el reporte Markdown generado por el sistema de consenso.

## Seguridad
- No compartas secretos de entorno.
- El sistema utiliza la autenticación nativa de **Gemini CLI**, por lo que no es necesario configurar API Keys adicionales para el funcionamiento básico de la skill.
