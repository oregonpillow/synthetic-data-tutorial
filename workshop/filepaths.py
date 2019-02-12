import os
from pathlib import Path

this_filepath = Path(os.path.realpath(__file__))
project_root = str(this_filepath.parents[1])
data_dir = os.path.join(project_root, 'data/')

postcodes_london = os.path.join(data_dir, 'postcodes_london.csv')
nhs_hospitals_london = os.path.join(data_dir, 'nhs_hospitals_london.txt')