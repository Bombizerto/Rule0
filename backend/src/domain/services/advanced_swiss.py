import random
from typing import List, Dict

def advanced_swiss_matchmaking(players: List[str], player_scores: Dict[str, int], player_history: Dict[str, List[str]]):
    """
    Algoritmo Suizo para juegos Multijugador (EDH).
    
    1. Ordena a los jugadores por sus puntos actuales (de más a menos).
    2. En caso de empate a puntos, desempaeta aleatoriamente (o por win_percentage_opponents).
    3. Intenta formar mesas asignando a los jugadores en grupos de 4 o 3 (según el número total).
    4. Al formar una mesa, comprueba si han jugado antes. Si hay muchas repeticiones, 
       intenta intercambiar al jugador con el siguiente en la lista de puntuación.
       
    Args:
        players: Lista de IDs de jugadores activos.
        player_scores: Diccionario con {player_id: puntos}.
        player_history: Diccionario con los rivales contra los que ya ha jugado {player_id: [rival_id1, rival_id2...]}
    """
    
    # 0. Calculamos las mesas necesarias
    from domain.services.matchmaking import calculate_tables
    t3, t4, t5 = calculate_tables(len(players))
    
    # 1. Ordenamos a los jugadores primero aleatoriamente (para desempatar de forma justa)
    random.shuffle(players)
    
    # 2. Ordenamos por puntos de mayor a menor
    sorted_players = sorted(players, key=lambda pid: player_scores.get(pid, 0), reverse=True)
    
    # Lista donde guardaremos los grupos finales (pods)
    groups = []
    
    # Necesitamos asignar primero las mesas grandes (o las de 3, según preferamos el diseño)
    # Por lo general en competiciones, las mesas top (los que más puntos tienen) 
    # deben ser mesas de 4 obligatoriamente para favorecer un juego equilibrado.
    
    # Para simplificar el borrador MVP:
    # Cogeremos a los jugadores por su orden y los intentamos agrupar.
    
    unpaired_players = sorted_players.copy()
    
    while unpaired_players:
        # Determinamos de qué tamaño va a ser esta mesa
        # Daremos prioridad a mesas de 4 siempre que todavía nos queden cupos (t4 > 0)
        table_size = 0
        if t4 > 0:
            table_size = 4
            t4 -= 1
        elif t3 > 0:
            table_size = 3
            t3 -= 1
        elif t5 > 0:
            table_size = 5
            t5 -= 1
            
        if table_size == 0 or len(unpaired_players) < table_size:
            break
            
        current_table = [unpaired_players.pop(0)] # Metemos al cabeza de serie de la mesa
        
        # Intentamos rellenar la mesa con los siguientes
        while len(current_table) < table_size:
            best_candidate_index = 0
            # Buscamos en la lista de unpaired al primero que cause menos repeticiones
            # En un suizo basico, cogemos al siguiente en la lista [0]
            # y penalizamos si ya ha jugado contra los de la current_table
            
            lowest_penalty = 999
            best_index = 0
            
            # Buscamos entre los próximos X candidatos (ej. los próximos 5) para no irnos
            # muy abajo en la tabla de puntos y desvirtuar el Suizo
            search_depth = min(5, len(unpaired_players))
            
            for i in range(search_depth):
                candidate = unpaired_players[i]
                penalty = 0
                
                # Comprobar historial con los que ya están sentados en la current_table
                for seated_player in current_table:
                    if seated_player in player_history.get(candidate, []):
                        penalty += 1 # Ya han jugado, sumamos penalización
                
                if penalty < lowest_penalty:
                    lowest_penalty = penalty
                    best_index = i
                    
                if penalty == 0:
                    break # Encontramos un candidato perfecto que no ha jugado con nadie de la mesa
            
            # Sentamos al mejor candidato (el que menos repite o el primero si todos repiten)
            current_table.append(unpaired_players.pop(best_index))
            
        groups.append(current_table)
        
    return groups
