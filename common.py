

def distribution_from(file_path, undirected):
    assert isinstance(undirected, bool), 'undirected must be boolean'
    
    with open(file_path, 'r') as f:
        
        links = f.read().strip()

    delimeter = ',' if ',' in links else None
    links = links.split('\n')
    links = [l.split(delimeter) for l in links]
    
    distribution = {}
    for a1, a2, w in links:
        if not('0' <= a1[0] <= '9'):
            continue

        a1, a2, w = int(a1), int(a2), float(w)
        
        for s, d in (((a1, a2), (a2, a1)) if undirected else ((a1, a2),)):
            if s not in distribution:
                distribution[s] = ([], [])

            distribution[s][0].append(d)
            distribution[s][1].append(w)
        
    return distribution  
    

def contribution_from(distribution, weighted):
    assert isinstance(weighted, bool), 'weighted must be boolean'

    contribution = {}
    for s in distribution:
        destinations, weights = distribution[s]
        for d, w in zip(destinations, weights):
            
            if d not in contribution:
                contribution[d] = ([], [])
            
            contribution[d][0].append(s)
            
            if not weighted:
                contrib_coef = 1 / len(destinations)
            else:
                contrib_coef = w / sum(weights)

            contribution[d][1].append(contrib_coef)
    
    return contribution


if __name__ == '__main__':

    distribution = distribution_from('popularity_weight.csv', undirected=True)
    contribution = contribution_from(distribution, weighted=True)
    print(contribution)