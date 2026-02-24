# Tareas Funcionales: App Commander MTG (Matchmaking & Puntos)

Este documento detalla las tareas funcionales necesarias para desarrollar la aplicación, divididas en MVP (Producto Mínimo Viable) y V2 (Futuras Versiones), con un enfoque en la correcta asignación de puntos, emparejamiento (matchmaking) y orden de turnos (seating).

## Fase 1: MVP (Producto Mínimo Viable) - Core del Torneo

Requisitos mínimos para sustituir el uso de hojas de cálculo y ofrecer una experiencia fluida en la tienda.

### 1. Gestión de Ligas y Eventos (Organizador)
- [ ] Crear un panel para el Organizador (TO - Tournament Organizer).
- [ ] Implementar la creación de un nuevo "Evento/Torneo".
- [ ] Implementar la configuración de "Categorías/Formatos" (Casual vs cEDH) al crear un evento:
    - Definir puntos por victoria y puntos por empate (cEDH).
    - Habilitar/Deshabilitar el sistema de Logros y Penalizaciones (Casual).
- [ ] Crear selector de "Reglas de Puntuación" personalizables (ej. +4 Victoria, +1 Kill).
- [ ] Implementar la gestión de la lista de jugadores inscritos (añadir/eliminar).

### 2. Motor de Emparejamiento (Matchmaking) y Asientos (Seating)
- [ ] Desarrollar el agoritmo base de agrupación en mesas de 4 (pods) basándose en puntos actuales (Sistema Suizo adaptado).
- [ ] Implementar agrupaciones para mesas de 3 (cuando no hay múltiplos de 4).
- [ ] **Lógica de Asientos (cEDH):** Desarrollar algoritmo para asignar el orden de turnos (1º a 4º) premiando al jugador con más puntos.
- [ ] **Lógica de Desempate de Asientos (ASQ - Average Seat Quality):** Implementar cálculo histórico para resolver empates y evitar rachas en el asiento 4.
- [ ] Desarrollar la opción de "Matchmaking Casual" (priorizar no repetir oponentes frente a emparejar por puntos).

### 3. Ejecución de la Ronda (Dashboard Organizador)
- [ ] Crear vista de "Ronda Activa" para el Organizador.
- [ ] Implementar la generación automática de la ronda (botón "Generar Emparejamientos").
- [ ] Permitir al Organizador modificar (drag & drop o selectores) un emparejamiento manual antes de publicar la ronda.
- [ ] Implementar funcionalidad "Drop" (Jugador abandona el torneo) y "Pausa" (Se salta esta ronda).

### 4. Experiencia del Jugador (UI/App Self-Service)
- [ ] Crear perfil básico de jugador (Alias).
- [ ] Desarrollar pantalla de "Mi Emparejamiento" que muestre claramente:
    - Número de Mesa.
    - Oponentes.
    - **Orden de Turno (Asiento 1 al 4)** explícito.
- [ ] Implementar formulario dinámico de "Reportar Resultado" según la categoría (cEDH: solo ganador/empate; Casual: checklist de logros/kills).
- [ ] Desarrollar el sistema de **Confirmación Cruzada (Trust System)**: Alguien reporta, los demás aprueban para subir el resultado al servidor.

### 5. Clasificación y Resultados Visibles
- [ ] Crear la pantalla de "Clasificación Actual" (Leaderboard) calculada en tiempo real.
- [ ] Desarrollar la vista "Display Público" (pantalla grande, cronómetro, lista de mesas y jugadores).

---

## Fase 2: V2 (Gamificación, Integraciones y Experiencia Premium)

Características para expandir la utilidad de la app una vez el MVP sea estable.

### 6. Integración Externa y Analíticas de Mazos
- [ ] Permitir a los jugadores registrar su Comandante (búsqueda de cartas en Scryfall API).
- [ ] Permitir pegar enlaces a listas de mazos (Moxfield/Archidekt).
- [ ] Desarrollar módulo de analíticas del "Metajuego del Local" (comandantes más jugados, win-rates por color).

### 7. Gamificación ("Salón de la Fama")
- [ ] Diseñar e implementar "Insignias/Logros Virtuales" para perfiles de jugador (ej. "Pacifista", "El Verdugo").
- [ ] Crear historial histórico de ligas en el perfil de usuario.

### 8. Gestión de "Power Level" (Entornos Casuales)
- [ ] Implementar sistema de autoevaluación o "tags" de nivel de poder para mazos.
- [ ] Modificar el algoritmo de emparejamiento Casual para considerar la paridad de Power Level.

### 9. Eventos Especiales y Notificaciones
- [ ] Integrar WebSockets para notificaciones en tiempo real ("¡La Ronda 2 ha empezado!").
- [ ] Añadir soporte para "Reglas Especiales por Ronda" (El organizador envía reglas *custom* a todos los dispositivos).
