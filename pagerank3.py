from tqdm import tqdm
import numpy as np
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s\t|%(levelname)s\t|%(name)s\t|%(message)s'
)


def extract_from_file(file_path):

    logging.info('Extracting interested information from file on disk')

    info = {}

    last_ASIN = None
    with open(file_path, 'r') as f:
        while True:
            line = f.readline()

            if line == '':
                break

            if line.startswith('ASIN: '):
                last_ASIN = line.strip().split()[1]
                info[last_ASIN] = {}
                logging.debug(f'{last_ASIN} detected')
            elif line.strip().startswith('salesrank'):
                salesrank = int(line.strip().split()[-1])
                info[last_ASIN]['salesrank'] = salesrank
                logging.debug(f'{last_ASIN} has salesrank {salesrank}')
            elif line.strip().startswith('similar'):
                similar = line.strip().split()[2:]
                info[last_ASIN]['similar'] = similar
                logging.debug(f'{last_ASIN} was co-purchased with {similar}')
                
    return info


def print_statistic(info):
    n_items = len(info)
    count_similarity = {}
    count_rank = {}
    list_rank = {}
    for ASIN in info:
        n_similarity = len(info[ASIN].get('similar', []))
        count_similarity[n_similarity] = count_similarity.get(n_similarity, 0) + 1

        salesrank = info[ASIN].get('salesrank', -1)
        count_rank[salesrank] = count_rank.get(salesrank, 0) + 1
        list_rank[salesrank] = list_rank.get(salesrank, []) + [ASIN]
    logging.info('Statistics includes:')
    logging.info(f'\t Number of items: {n_items}')
    logging.info(f'\t Similarity count: {count_similarity}')
    logging.info(f'\t Rank count: {count_rank}')
    logging.info(f'\t Rank list: {list_rank}')
    
    



def distribution_from(info):

    logging.info('Building distribution from info')
    
    distribution = {}
    for s in info:
        logging.debug(f'Processing {s}')
        if s not in distribution:
                distribution[s] = []
        for d in info[s].get('similar', []):
            
            if d not in distribution[s]:
                distribution[s].append(d)

            if d not in distribution:
                distribution[d] = []
            if s not in distribution[d]:
                distribution[d].append(s)          
        
    return distribution 


def init_PRvalue(distribution):
    logging.info('Initializing PRvalue')
    return {s: 1 for s in distribution}


def converge_PRvalue(distribution, PRvalue, n_iters, in_out_weighted, log_scale=True):

    for _ in range(n_iters):
        logging.info(f'Starting iteration {_ + 1}/{n_iters}')
        logging.info('Building contribution')
        contribution = {}
        for s, destinations in distribution.items():
            
            for d in destinations:


                if d not in contribution:
                    contribution[d] = ([], [])

                contribution[d][0].append(s)

            for d in destinations:

                if not in_out_weighted:
                    contrib_coef = 1 / len(destinations)
                else:
                    in_coef = len(contribution[d][0]) / sum(len(contribution[di][0]) for di in destinations)
                    out_coef = len(distribution[d][0]) / sum(len(distribution[di][0]) for di in destinations)
                    contrib_coef = 2 * in_coef * out_coef / (in_coef + out_coef)

                if not log_scale:
                    contrib_value = PRvalue[s] * contrib_coef
                else:
                    contrib_value = PRvalue[s] + np.log(contrib_coef)

                contribution[d][1].append(contrib_value)
        

        logging.info('Computing PRvalue')
        sum_ = 0
        for d in PRvalue:
            if d not in contribution:
                if not log_scale:
                    PRvalue[d] = 0
                else:
                    PRvalue[d] = 1e-9
                
                continue

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

def export_result(file_path, PRvalue):
    logging.info(f'Exporting result to {file_path}')
    with open(file_path, 'w') as f:
        for k, v in PRvalue.items():
            print(f'{k},{v}', file=f)



if __name__ == '__main__':

    info = extract_from_file('amazon-meta.txt')
    # print_statistic(info)
    distribution = distribution_from(info)
    PRvalue = init_PRvalue(distribution)
    PRvalue = converge_PRvalue(distribution, PRvalue, n_iters=30, in_out_weighted=True, log_scale=True)
    export_result('result_pagerank_original.txt', PRvalue)
    
