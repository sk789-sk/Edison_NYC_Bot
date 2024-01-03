import pickle


def parse_test(file):

    with open(file,'rb') as f:
        text = pickle.load(f)
    
    lines = text.split('\n')

    for val in lines:
        print(val.split('\t'))


    return text

if __name__ == "__main__":
    data = parse_test('test.pkl')
    