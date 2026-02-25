from typing import List
from domain.entities import User
import random
def calculate_tables(num_players: int):
    remainder= num_players % 4
    tables_of_3 = 4 - remainder if remainder > 0 else 0
    tables_of_4 = (num_players-(tables_of_3 * 3))//4
    return tables_of_3, tables_of_4

def create_groups(players: List[str]):
    current=0
    groups = []
    random.shuffle(players)
    t3,t4=calculate_tables(len(players))
    for _ in range(t4):
        groups.append(players[current:current+4])
        current+=4
    for _ in range(t3):
        groups.append(players[current:current+3])
        current+=3
    return groups

def assign_seats(table_players: List[User]):
    random.shuffle(table_players)
    seats=sorted(table_players, key=lambda x: x.seat_history[1])
    return seats

