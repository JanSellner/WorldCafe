import numpy as np
import pandas as pd

from GroupSearch import GroupSearch

if __name__ == '__main__':
    df = pd.read_csv('example_data.csv')
    foreigners = df['Foreigner'].to_numpy().astype(np.int32)
    n_groups = 3

    group_search = GroupSearch(n_groups, len(df), foreigners)
    alloc, error = group_search.find_best_allocation()
    print(error)

# TODO: group statistics
# TODO: example csv file
# TODO: keep form data (this does currently nor work for the file upload)
# TODO: deterministic search
