import pickle
import re


def parse_file(file):

    with open(file,'rb') as f:
        text = pickle.load(f)
    
    lines = text.split('\n')

    # for val in lines:
    #     new = (val.replace(',', "").replace('\r',"").split('\t'))
    #     new = list(filter(None,new))

    pattern = r'^(\d+)?\t(.*?)\s+\((\d+)\)'
    pattern = r'^(\d+)?\t?(.*?)\s+\((\d+)\)' 
    # (\d+)? sequence of digits at the start of a string optional group 1
    # \t? optional tab
    #(.*?) non-greedy capture of name until next sequence is hit
    #\s+\((\d+)\) whitespace following open parenthesis and capture the digits
    entrants = []

    for line in lines:
        match = re.match(pattern, line)
        entrant_counter = 0
        if match:
            entrant_counter +=1
            initial_digit = (len(entrants)+1) #or match.group(1) #entrants length is probably more accurate 
            name = match.group(2)
            id_ = match.group(3)
            print(f'Initial Digit: {initial_digit}, Name: {name}, ID: {id_}')
            entrants.append([initial_digit,name, id_])
        else:
            print(f'No match found for line: {line}')

    #return [rank, name, konami id]
        
    

    return entrants

def parsetext(text):
    pass
    

if __name__ == "__main__":
    data = parse_file('test.pkl')
    print(data)
    