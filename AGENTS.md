# AGENT RULES - Kimi CLI

## REGLAS OBLIGATORIAS (LEER SIEMPRE ANTES DE ACTUAR)

### 1. JAMÁS HACER PUSH SIN PERMISO
- **NUNCA** ejecutar `git push` sin permiso explícito y escrito del usuario
- El usuario debe aprobar personalmente el código antes de cualquier push
- Si hay duda, NO hacer push y preguntar primero

### 2. SIEMPRE PREGUNTAR ANTES DE CAMBIAR
- Antes de cualquier modificación NO solicitada explícitamente, preguntar al usuario
- NO asumir que se quiere cambiar algo "porque queda mejor"
- Si el usuario dice "reorganiza la sección X", eso NO significa "elimina contenido"

### 3. JAMÁS ELIMINAR CONTENIDO EXISTENTE
- **NUNCA** quitar texto, ecuaciones, tablas o secciones que ya están escritas
- Si se pide "reorganizar", mantener TODO el contenido, solo cambiar el orden
- Si algo parece duplicado, preguntar antes de eliminar

### 4. MOSTRAR DIFF ANTES DE CONFIRMAR
- Antes de decir "listo", mostrar qué cambios se hicieron con `git diff`
- Permitir al usuario revisar y aprobar antes de considerar terminado

### 5. CAMBIOS SOLO BAJO INSTRUCCIÓN EXPLÍCITA
- Si el usuario NO pidió modificar algo, NO lo modificar
- "Arregla X" NO significa "también mejora Y y Z"
- Mantener el scope exacto de lo solicitado

### 6. CAMBIOS ESPECÍFICOS ÚNICAMENTE - NADA DE GENERALIDADES
- **NUNCA** hacer cambios generales - solo el caso específico que se solicita
- Cuando se pide algo, enfocarse ÚNICAMENTE en cambiar eso y **NUNCA** nada más
- NO aplicar "mejoras" o "optimizaciones" no solicitadas
- NO modificar código/archivos que no están directamente relacionados con la tarea
- Si se pide "arregla X", solo se arregla X, no se toca Y ni Z aunque "quede mejor"

---

## RECORDATORIO INICIAL
> Al iniciar cada sesión, leer este archivo y confirmar al usuario que las reglas están activas.

## COMANDOS PROHIBIDOS SIN PERMISO
```bash
git push
git commit -m "..."  # sin confirmación previa
git rebase
git reset --hard
```

## COMANDOS PERMITIDOS LIBREMENTE
```bash
git status
git diff
git log --oneline -5
git add  # solo si el usuario pidió preparar cambios
git checkout -- archivo  # para revertir cambios no deseados
```
