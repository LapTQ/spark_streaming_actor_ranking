import numpy as np
import pandas as pd
pd.set_option('display.max_colwidth', None)
from tqdm import tqdm


def extract_from_file(file_path):

    buf = []

    with open(file_path, 'r') as f:
        while True:
            line = f.readline()

            if line == '':
                break

            if line.startswith('ASIN: '):
                buf.append({'ASIN': line.strip().split()[1]})
            elif line.strip().startswith('salesrank'):
                buf[-1]['salesrank'] = int(line.strip().split()[-1])
            elif line.strip().startswith('similar'):
                buf[-1]['similar'] = line.strip().split()[2:]

    return buf


def main():
    df = pd.DataFrame(extract_from_file('./data/amazon-meta.txt'))
    # print(df[df["ASIN"] == "0374518173"]["similar"])
    print(df[["similar", "ASIN"]])
    
    # 0140585532 -> [0520201663, 0140586687, 0374518173, 0060765291, 0375411399]


if __name__ == '__main__':
    main()
