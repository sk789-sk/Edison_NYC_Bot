from table2ascii import table2ascii
from models import Tournament , User
from urllib.parse import urlencode


#Given a header and data create te table

def create_tournament_table(t_obj:Tournament):
    #Sort tournament by rank
    sorted_obj = t_obj
    # sorted_obj = sorted(t_obj, key=lambda x: x['Entrant']['rank'])
    table_header = ['Place','Name','Konami ID']
    
    #sort the entrants by rank first
    table_body = [[entrant['rank'],entrant['user_info']["name"],
    entrant['user_info']["konami_id"]] for entrant in sorted_obj['Entrant']]
    table = table2ascii(header=table_header, body=table_body)
    return table

def create_user_table(user_obj:User):
    table_header = ['Place','Date','Store','Rounds']
    table_body = [[val['rank'],val['tournament_info']['date'],val['tournament_info']['host'],val['tournament_info']['rounds']] for val in user_obj['Entrant']]
    table = table2ascii(header=table_header, body=table_body)
    return table

def build_query_string(**kwargs):
    query_params = {key:value for key,value in kwargs.items() if value is not None}
    return urlencode(query_params)
