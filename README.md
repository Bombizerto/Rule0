# Rule Zero (R0) - Commander MTG Tournament Manager

Rule Zero (R0) es una aplicación web integral diseñada para la gestión, organización y desarrollo de torneos y ligas de **Magic: The Gathering - Commander**. El principal problema que pretende resolver es sustituir el engorroso uso de hojas de cálculo manuales para gestionar eventos, ofreciendo una experiencia fluida e interactiva tanto para los Organizadores de Torneos (TO) como para los jugadores.

## ¿Qué problema resuelve?

En los formatos multijugador como Commander, determinar quién juega contra quién (matchmaking), en qué orden (seating) y cómo se reparten equitativamente los puntos (especialmente en entornos Casuales) es un proceso complejo. R0 automatiza estas decisiones de manera justa utilizando algoritmos matemáticos e históricos.

## Características Principales (MVP)

### 1. Sistema Suizo Adaptado para Multijugador
El motor de emparejamiento de R0 agrupa a los jugadores en mesas óptimas de 4 (o 3 cuando no es matemáticamente posible) basándose en sus puntos actuales del torneo. Busca el equilibrio competitivo sin requerir intervención manual constante.

### 2. Algoritmo de "Seating" (Orden de Turno)
El orden en que los jugadores desarrollan su turno influye drásticamente en su probabilidad de victoria en Commander (especialmente en **cEDH**). 
Para solucionar el desequilibrio inherente al orden de juego (donde salir primero es una ventaja estadística demostrable):
* Implementa una lógica basada en el historial de asientos (como el parámetro **ASQ - Average Seat Quality** y contabilización de salidas previas en Asiento 1).
* De esta forma, busca compensar para que quien ya ha tenido ventajas iniciales (asientos 1 y 2) ceda su turno a oponentes que hayan jugado sistemáticamente en peores asientos (ej. Asiento 4), independientemente de la puntuación total acumulada.

### 3. Puntuación Dinámica y Sistemas "Trust"
La aplicación está preparada para operar en dos realidades:
* **Entornos cEDH (Competitivo):** Se registran y otorgan puntos estándar de victoria/empate.
* **Entornos Casuales:** Se permiten sistemas personalizados de puntos (como "Logros" o "Kills") establecidos por cada local.

Además, incorpora funcionalidad de **"Trust System"**, donde un jugador reporta los resultados de la mesa desde su móvil y el resto de los contrincantes aprueba e ingresa dicho reporte al sistema en tiempo real.

### 4. Interfaz Self-Service (Jugadores) "Trae tu Propio Dispositivo"
Los jugadores no dependen de buscar su nombre en una hoja de papel pegada en una pared. R0 cuenta con un perfil para jugadores que mostrará de manera automática el número de su mesa, sus respectivos oponentes y el tan vital orden de la silla (Asiento 1 a 4).

## Futuro del Proyecto (V2)

En futuras expansiones, la aplicación pretende integrar analíticas cruzando información de las barajas con APIs como Scryfall/Moxfield para mostrar el Metajuego local del local, incorporar sistemas de Gamificación (logros permanentes) e integrar métricas de "*Power Level*" para el disfrute de la vertiente Casual.
