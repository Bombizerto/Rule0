from typing import List
from domain.entities import User
import random
def calculate_tables(num_players: int):
    tables_of_5=0
    if num_players < 3:
        raise ValueError("No hay suficientes jugadores")
    if num_players==5:
        return 0,0,1
    remainder= num_players % 4
    tables_of_3 = 4 - remainder if remainder > 0 else 0
    tables_of_4 = (num_players-(tables_of_3 * 3))//4
    return tables_of_3, tables_of_4,tables_of_5

def create_groups(players: List[str]):
    current=0
    groups = []
    random.shuffle(players)
    t3,t4,t5=calculate_tables(len(players))
    for _ in range(t4):
        groups.append(players[current:current+4])
        current+=4
    for _ in range(t3):
        groups.append(players[current:current+3])
        current+=3
    if t5!=0:
        groups.append(players[current:current+5])
    return groups

def assign_seats(table_players: List[User]):
    random.shuffle(table_players)
    seats=sorted(table_players, key=lambda x: x.seat_history[1])
    return seats

def run_casual_matchmaking(players: List[User]):
    tables=create_groups(players)
    finalPods=[]
    for table in tables:
        finalPods.append(assign_seats(table))
    return finalPods

from typing import Dict
def advanced_swiss_matchmaking(players: List[User], player_scores: Dict[str, int], player_history: Dict[str, List[str]]):
    """
    Algoritmo Suizo para juegos Multijugador (EDH).
    """
    t3, t4, t5 = calculate_tables(len(players))
    
    # 1. Mezclamos primero
    random.shuffle(players)
    
    # 2. Ordenamos por puntos (de mayor a menor)
    sorted_players = sorted(players, key=lambda p: player_scores.get(p.id, 0), reverse=True)
    
    groups = []
    unpaired_players = sorted_players.copy()
    
    while unpaired_players:
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
            # Los metemos al ultimo grupo si sobra algo raro, o creamos mesa
            if len(unpaired_players) > 0 and groups:
                groups[-1].extend(unpaired_players)
            elif len(unpaired_players) > 0:
                groups.append(unpaired_players)
            break
            
        current_table = [unpaired_players.pop(0)] 
        
        while len(current_table) < table_size and unpaired_players:
            lowest_penalty = 999
            best_index = 0
            
            search_depth = min(5, len(unpaired_players))
            
            for i in range(search_depth):
                candidate = unpaired_players[i]
                penalty = 0
                
                for seated_player in current_table:
                    if seated_player.id in player_history.get(candidate.id, []):
                        penalty += 1
                
                if penalty < lowest_penalty:
                    lowest_penalty = penalty
                    best_index = i
                    
                if penalty == 0:
                    break 
            
            current_table.append(unpaired_players.pop(best_index))
            
        groups.append(current_table)
        
    finalPods = []
    for table in groups:
        finalPods.append(assign_seats(table))
    return finalPods
