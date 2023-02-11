from tqdm import tqdm
import numpy as np

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


def init_PRvalue(distribution):
    return {s: 1 for s in distribution}


def converge_PRvalue(distribution, PRvalue, n_iters, weighted, log_scale=True):
    assert isinstance(weighted, bool), 'weighted must be boolean'


    for _ in tqdm(range(n_iters)):
        contribution = {}
        for s in distribution:
            destinations, weights = distribution[s]
            for d, w in zip(destinations, weights):

                if d not in contribution:
                    contribution[d] = ([], [])

                contribution[d][0].append(s)

                if not weighted:
                    contrib_coef = 1 / len(weights)
                else:
                    contrib_coef = w / sum(weights)

                if not log_scale:
                    contrib_value = PRvalue[s] * contrib_coef
                else:
                    contrib_value = PRvalue[s] + np.log(contrib_coef)

                contribution[d][1].append(contrib_value)
        
        sum_ = 0
        for d in PRvalue:
            if not log_scale:
                PRvalue[d] = sum(contribution[d][1])
            else:
                PRvalue[d] = sum(np.exp(v) for v in contribution[d][1])
            sum_ += PRvalue[d]

        for d in contribution:
            if not log_scale:
                PRvalue[d] = PRvalue[d] / sum_
            else:
                PRvalue[d] = np.log(PRvalue[d]) - np.log(sum_)

    return PRvalue


if __name__ == '__main__':

    # distribution = distribution_from('popularity_weight.csv', undirected=True)
    # PRvalue = init_PRvalue(distribution)
    # PRvalue = converge_PRvalue(distribution, PRvalue, n_iters=10, weighted=False)

    distribution = distribution_from('test_data.txt', undirected=False)
    PRvalue = init_PRvalue(distribution)
    PRvalue = converge_PRvalue(distribution, PRvalue, n_iters=10, weighted=False, log_scale=True)
    
    print(PRvalue)