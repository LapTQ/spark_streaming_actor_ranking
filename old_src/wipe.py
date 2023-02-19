from pathlib import Path
import os

WEIGHTS_DIR = '/user/hadoop/weight'

names = [name for name in os.listdir('.') if name[:2] == 'f_' and name[-4:] == '.csv']
for name in names:
    os.system(f'rm {name}')
    os.system(f'hadoop fs -rm {WEIGHTS_DIR}/{name}')