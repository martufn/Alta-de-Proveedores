# Bot de Alta de Proveedores — DevSolutions S.R.L.

Trabajo Práctico Integrador de **Organización Empresarial** — Tecnicatura Universitaria en Programación a Distancia (TUPaD - UTN).

Este proyecto automatiza, mediante un chatbot (simulador por consola), el proceso administrativo de **alta de proveedores** de una empresa de software. La lógica del programa sigue fielmente el diagrama **BPMN 2.0** del proceso.

## ¿Qué hace?

El bot le pide al usuario los datos de un proveedor nuevo, los valida en el momento y, según las reglas de negocio, decide el resultado:

1. **Valida el CUIT** (formato de 11 dígitos) y verifica que no esté repetido en la base.
2. **Evalúa el monto estimado anual:** si es menor o igual a $500.000, el alta es automática; si lo supera, se deriva al Responsable de Compras.
3. **Aprobación:** si el responsable aprueba, el proveedor queda *Activo*; si no, queda *Rechazado*.

El bot tiene "memoria" (máquina de estados) y maneja errores de entrada (camino infeliz).

## Estructura del repositorio

```
.
├── simulador_alta_proveedores.py   # Programa principal (bot + máquina de estados)
├── proveedores.csv                 # Base de datos simulada (viene con datos de ejemplo)
├── bpmn_alta_proveedores.png       # Diagrama BPMN 2.0 del proceso
└── README.md                       # Este archivo
```

## Cómo ejecutarlo

Requiere tener Python 3 instalado. No usa librerías externas (solo módulos estándar).

```bash
python3 simulador_alta_proveedores.py
```

Seguir las preguntas del bot. Para salir en cualquier momento, escribir `cancelar`.

## Cómo probar cada camino

- **Alta automática:** cargar un CUIT nuevo y un monto menor o igual a 500000.
- **Proveedor duplicado:** usar el CUIT `20304050607` (ya está en `proveedores.csv`).
- **Derivación a aprobación:** cargar un monto mayor a 500000 y responder `si` o `no` como Responsable de Compras.
- **Camino infeliz:** ingresar un CUIT con letras, un email sin `@` o un monto con texto, para ver cómo el bot vuelve a pedir el dato.

## Integrantes

- Fernandez Martina
- Escobar Gonzalez Tomás

## Link Repositorio
- https://github.com/martufn/Alta-de-Proveedores.git

## Reglas de negocio (resumen)

| Regla | Condición | Resultado |
|-------|-----------|-----------|
| Validación de CUIT | 11 dígitos y no existente | Continúa / Rechaza |
| Umbral de aprobación | Monto ≤ $500.000 | Alta automática |
| Umbral de aprobación | Monto > $500.000 | Deriva a aprobación |
| Decisión del responsable | Aprueba / Rechaza | Activo / Rechazado |
