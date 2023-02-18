import pandas as pd
def create_edges():
        datafile = open('./popularity_weight.csv')
        edges = []
        for line in datafile:
            row_data = line.strip("\n").split(",")
            row_data = row_data[:2]
            
            # try:
            #     row_data[2] = float(row_data[2])
            # except ValueError:
            #     pass
            edges.append(row_data)
        edges.pop(0)
        return edges

a = pd.DataFrame(create_edges())
print(create_edges()[:50])