# import pandas as pd

# # # create example dataframe
# data = {'node1': ['A', 'B', 'C'], 'node2': [['X', 'Y'], ['Y', 'Z'], ['Z', 'W']]}
# df = pd.DataFrame(data)
# print(df)
# # EM ƠI EM CÓ ĐANG XEM KHÔNG

# # use explode to create new rows for each element in the list
# df = df.explode('node2')

# # concatenate node1 and node2 into a single column
# df['pairs'] = list(df['node1'] + ',' + df['node2'])

# # select only the pairs column
# pairs = df['pairs'].tolist()

# print(pairs)

import pandas as pd

# create a sample dataframe
# data = {'node1': ['A', 'B', 'C'], 'node2_list': [['X', 'Y'], ['Y', 'Z'], ['X', 'Z']]}
# df = pd.DataFrame(data)

# # create list of all node pairs
# pairs = [[row.node1, node2] for row in df.itertuples() for node2 in row.node2_list]

# print(df.itertuples())

# 1. Process the data
def process_the_data():
    
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

    df = pd.DataFrame(extract_from_file('./data/amazon-meta.txt'))
    
    df = df[["ASIN", "similar"]]
    df = df[df['similar'].notna()]
    pairs = [[row.ASIN, node2] for row in df.itertuples() for node2 in row.similar] 
    # for row in df.itertuples():
    #     print(row.similar)
    return pairs

# print the list of pairs
print(process_the_data())

