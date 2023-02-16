from tqdm import tqdm
import numpy as np
import logging
import argparse
from pathlib import Path

HERE = Path(__file__).parent


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s\t|%(levelname)s\t|%(name)s\t|%(message)s'
)


def parse_opt():

    ap = argparse.ArgumentParser()

    ap.add_argument('--directed', default=False, type=bool)
    ap.add_argument('--in_out_weighted', action='store_true')
    ap.add_argument('--n_iters', default=30, type=int)
    ap.add_argument('--log_scale', default=True, type=bool)

    opt = ap.parse_args()

    return opt



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
    
    



def distribution_from(info, directed):
    assert directed is True or directed is False, 'directed must be True or False'

    logging.info('Building distribution from info')
    
    distribution = {}
    for s in info:
        logging.debug(f'Processing {s}')
        if s not in distribution:
                distribution[s] = []
        for d in info[s].get('similar', []):
            
            if d not in distribution[s]:
                distribution[s].append(d)

            if not directed:
                if d not in distribution:
                    distribution[d] = []
                if s not in distribution[d]:
                    distribution[d].append(s)          
        
    return distribution


def export_true_rank(file_path, info):
    logging.info(f'Exporting true rank to {file_path}')
    
    with open(file_path, 'w') as f:
        for ASIN in info:
            if 'salesrank' in info[ASIN]:
                print(f"{ASIN},{info[ASIN]['salesrank']}", file=f)


def init_PRvalue(distribution):
    logging.info('Initializing PRvalue')
    return {s: 1 for s in distribution}


def converge_PRvalue(distribution, PRvalue, n_iters, in_out_weighted, log_scale=True):

    logging.info(f'Params: n_iters={n_iters}, in_out_weighted={in_out_weighted}, log_scale={log_scale}')

    for _ in range(n_iters):
        logging.info(f'Starting iteration {_ + 1}/{n_iters}')
        logging.info('Building contribution')
        contribution = {}
        for s, destinations in distribution.items():
            
            for d in destinations:

                if d not in contribution:
                    contribution[d] = ([], [])

                contribution[d][0].append(s)
        
        for s, destinations in distribution.items():
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

    # opt = parse_opt()

    info = extract_from_file(str(HERE / 'amazon-meta.txt'))
    # print_statistic(info)
    export_true_rank(str(HERE / 'true_rank.txt'), info)
    
    # distribution = distribution_from(info, directed=opt.directed)
    # PRvalue = init_PRvalue(distribution)
    # PRvalue = converge_PRvalue(distribution, PRvalue, n_iters=opt.n_iters, in_out_weighted=opt.in_out_weighted, log_scale=opt.log_scale)
    
    # export_result(str(HERE / f"result_pagerank_{'original' if not opt.in_out_weighted else 'weighted'}_{'directed' if opt.directed else 'indirected'}.txt"), PRvalue)
    
