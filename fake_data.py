import numpy as np
import os
from pathlib import Path
import random
import os
from hdfs import InsecureClient
import time

CLIENT = InsecureClient('http://master-node:9870', user='hdfs')
TEMP_WEIGHTS_DIR = '/user/hadoop/temp_weight'
WEIGHTS_DIR = '/user/hadoop/weight'

N_LINKS = 5
MIN_ID = 2
MAX_ID = 50
MIN_WEIGHT = 1
MAX_WEIGHT = 50

no = len(list(Path('.').glob('f_*.csv')))

buf = []
n = 0
while n < N_LINKS:
    src = random.randint(MIN_ID, MAX_ID)
    dst = random.randint(MIN_ID, MAX_ID)
    wgt = random.randint(MIN_WEIGHT, MAX_WEIGHT)

    if src != dst:
        src, dst = (src, dst) if src < dst else (dst, src)
        buf.append(f'{src},{dst},{wgt}')
        n += 1

with open(f'f_{no}.csv', 'w') as f:
    f.write('\n'.join(buf))
f.close()

with CLIENT.write(f"{TEMP_WEIGHTS_DIR}/f_{no}.csv", encoding ="utf-8", overwrite=True) as writer:
        print('\n'.join(buf), file=writer)

os.system(f'chmod 777 f_{no}.csv')

# os.system(f'hadoop fs -put f_{no}.csv {TEMP_WEIGHTS_DIR}/')

os.system(f'hadoop fs -mv {TEMP_WEIGHTS_DIR}/f_{no}.csv {WEIGHTS_DIR}/')