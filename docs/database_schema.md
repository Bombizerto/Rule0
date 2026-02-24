# Modelo de Datos - Rule Zero (R0)

Este documento define el modelo relacional propuesto para la aplicación de torneos de Commander "Rule Zero". Está diseñado pensando en una base de datos SQL (como PostgreSQL) y soportar tanto entornos Casuales como cEDH (incluyendo la lógica de *Seating* y puntuaciones variables).

## Entidades Principales (Core)

### 1. `users` (Jugadores y Organizadores)
El perfil base. En el MVP permitimos perfiles temporales ("guests") creados por el organizador si alguien no tiene la app instalada.
*   `id` (UUID, PK)
*   `alias` (String, UQ) - El nombre que se ve en la mesa.
*   `email` (String, opcional para guests)
*   `is_guest` (Boolean) - `true` si fue creado por un TO.

### 2. `format_rulesets` (Reglas del Torneo)
Define si un torneo es cEDH puro (solo puntos al ganador) o Casual (puntos por logros/kills).
*   `id` (UUID, PK)
*   `name` (String) - Ej. "cEDH Standard" o "Casual Social".
*   `win_points` (Int) - Puntos base por ganar (ej. 4).
*   `draw_points` (Int) - Puntos por empatar (ej. 1).
*   `kill_points` (Int) - Puntos por eliminar a otro jugador.
*   `allows_custom_achievements` (Boolean) - Habilita la interfaz de logros en Casual.

### 3. `events` (El Torneo / Liga)
La agrupación global donde se juegan las partidas.
*   `id` (UUID, PK)
*   `title` (String) - "Liga R0 Febrero".
*   `organizer_id` (UUID, FK -> users)
*   `ruleset_id` (UUID, FK -> format_rulesets)
*   `status` (Enum: `pending`, `active`, `completed`)
*   `created_at` (Timestamp)

### 4. `event_players` (Inscripciones)
Relación N:M entre `users` y `events`. Sirve para trackear los puntos *totales* del jugador en esa liga para el matchmaking.
*   `event_id` (UUID, PK, FK -> events)
*   `user_id` (UUID, PK, FK -> users)
*   `total_points` (Int) - Caché de los puntos acumulados para búsquedas rápidas.
*   `average_seat_quality` (Float) - Crucial para el algoritmo de desempate de Asientos (ASQ). Se actualiza tras cada ronda.
*   `status` (Enum: `active`, `dropped`) - Para gestionar abandonos.

## Entidades Operativas (Matchmaking)

### 5. `rounds` (Rondas del Torneo)
*   `id` (UUID, PK)
*   `event_id` (UUID, FK -> events)
*   `round_number` (Int) - Ej. Ronda 1, Ronda 2.
*   `status` (Enum: `pairing`, `playing`, `completed`)

### 6. `pods` (Las Mesas de Juego / Matches)
Agrupa a los 3 o 4 jugadores elegidos por el algoritmo.
*   `id` (UUID, PK)
*   `round_id` (UUID, FK -> rounds)
*   `table_number` (Int) - Ej. Mesa 1, Mesa 2.
*   `status` (Enum: `waiting_results`, `reviewing`, `completed`)
*   `winner_id` (UUID, FK -> users, Nullable) - Quién ganó el pod.

### 7. `pod_results` (El resultado individual por jugador)
La tabla MÁS IMPORTANTE. Define qué hizo cada jugador en esa mesa en concreto.
*   `id` (UUID, PK)
*   `pod_id` (UUID, FK -> pods)
*   `user_id` (UUID, FK -> users)
*   `seat_position` (Int) - 1, 2, 3 o 4. El orden de turno asignado por la app.
*   `points_earned` (Int) - Puntos ganados *solo en esta partida*.
*   `status` (Enum: `alive`, `eliminated`, `winner`, `draw`)

## Entidades Extra (Para Casual / V2)

### 8. `achievements_catalog` (Catálogo de Logros)
*   `id` (UUID, PK)
*   `name` (String) - Ej. "First Blood" o "Mazo Temático".
*   `points_value` (Int) - Puede ser positivo (+1) o negativo (-2, como una penalización de Stax).

### 9. `pod_achievements_log`
Trackea qué logros consiguió un jugador en un Pod específico (para ligas Casuales).
*   `pod_result_id` (UUID, FK -> pod_results)
*   `achievement_id` (UUID, FK -> achievements_catalog)
