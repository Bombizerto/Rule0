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
