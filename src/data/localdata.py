"""
Custom dataset processing/generation functions should be added to this file
"""

import pandas as pd
import pathlib

__all__ = [
    'process_wine_reviews',
]

def process_wine_reviews(*, unpack_dir, kind='130k', extract_dir='wine_reviews',
                         metadata=None):
    """
    Process wine reviews into (data, target, metadata) format. Since we plan to use Pandas
    for further processing, data will be a pandas dataframe.

    Parameters
    ----------
    unpack_dir:
        The directory the reviews have been unpacked into
    kind: {'130k' , '150k'}
        This is an unsupervised learning example. There are no labels. We will only work
        with the whole dataset. There are two versions, the 130k version of 150k version.
    extract_dir:
        Name of the directory of the unpacked zip file containing the raw data files.


    Returns
    -------
    A tuple:
        (data, target, additional_metadata)

    """
    if metadata is None:
        metadata = {}

    unpack_dir = pathlib.Path(unpack_dir)
    data_dir = unpack_dir / extract_dir
    if kind == '130k':
        data = pd.read_csv(data_dir/"winemag-data-130k-v2.csv", index_col=0)
    elif kind == '150k':
        data = pd.read_csv(data_dir/"winemag-data_first150k.csv", index_col=0)
    else:
        raise ValueError(f'kind: {kind} must be one of "130k" or "150k"')

    target = None

    return data, target, metadata
