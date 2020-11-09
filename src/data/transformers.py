
import sys
import pathlib
import os
from sklearn.model_selection import train_test_split
from .datasets import Dataset
from ..log import logger

__all__ = [
    'available_transformers'
]

_MODULE = sys.modules[__name__]
_MODULE_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

def available_transformers(keys_only=True):
    """Valid transformation functions

    This function simply returns a dict of known
    tranformer algorithms strings and their corresponding
    function call

    It exists to allow for a description of the mapping for
    each of the valid strings as a docstring

    The valid algorithm names, and the function they map to, are:

    ============                ====================================
    string                      Transformer Function
    ============                ====================================
    train_test_split            train_test_split_xform
    pivot                       pivot
    index_to_date_time          index_to_date_time
    sklearn_transform           sklearn_transform
    ============                ====================================

    Parameters
    ----------
    keys_only: boolean
        If True, return only keys. Otherwise, return a dictionary mapping keys to algorithms
    """
    _TRANSFORMERS = {
        "add_srm_to_reviews": add_srm_to_reviews,
        "groupby_beer_to_reviewers": groupby_beer_to_reviewers,
        "groupby_breweries": groupby_breweries,
        "groupby_breweries_by_style": groupby_breweries_by_style,
        "groupby_style_to_reviewers": groupby_style_to_reviewers,
        "index_to_date_time": index_to_date_time,
        "pivot": pivot,
        "sklearn_transform": sklearn_transform,
        "train_test_split": split_dataset_test_train,
    }

    if keys_only:
        return list(_TRANSFORMERS.keys())
    return _TRANSFORMERS


def sklearn_transformers(keys_only=True):
    """Valid sklearn-style transformers

    This function simply returns a dict of known
    tranformer algorithms strings and their corresponding
    function call

    It exists to allow for a description of the mapping for
    each of the valid strings as a docstring

    The valid algorithm names, and the function they map to, are:

    ============                ====================================
    string                      Transformer Function
    ============                ====================================
    CountVectorizer             sklearn.feature_extraction.text.CountVectorizer
    TfidfVectorizer             sklearn.feature_extraction.text.TfidfVectorizer
    ============                ====================================

    Parameters
    ----------
    keys_only: boolean
        If True, return only keys. Otherwise, return a dictionary mapping keys to algorithms
    """
    _SK_TRANSFORMERS = {
        "CountVectorizer": CountVectorizer,
        "TfidfVectorizer": TfidfVectorizer,
    }

    if keys_only:
        return list(_SK_TRANSFORMERS.keys())
    return _SK_TRANSFORMERS


def split_dataset_test_train(dset,
                             dump_path=None, dump_metadata=True,
                             force=True, create_dirs=True,
                             **split_opts):
    """Transformer that performs a train/test split.

    This transformer passes `dset` intact, but creates and dumps two new
    datasets as a side effect: {dset.name}_test and {dset.name}_train

    Parameters
    ----------
    dump_metadata: boolean
        If True, also dump a standalone copy of the metadata.
        Useful for checking metadata without reading
        in the (potentially large) dataset itself
    dump_path: path. (default: `processed_data_path`)
        Directory where data will be dumped.
    force: boolean
        If False, raise an exception if any dunp files already exists
        If True, overwrite any existing files
    create_dirs: boolean
        If True, `dump_path` will be created (if necessary)
    **split_opts:
        Remaining options will be passed to `train_test_split`

    """
    new_ds = {}
    for kind in ['train', 'test']:
        dset_name = f"{dset.name}_{kind}"
        dset_meta = {**dset.metadata, 'split':kind, 'split_opts':split_opts}
        new_ds[kind] = Dataset(dataset_name=dset_name, metadata=dset_meta)
    X_train, X_test, y_train, y_test = train_test_split(dset.data, dset.target, **split_opts)

    new_ds['train'].data = X_train
    new_ds['train'].target = y_train
    logger.info(f"Writing Transformed Dataset: {new_ds['train'].name}")
    new_ds['train'].dump(force=force, dump_path=dump_path, dump_metadata=dump_metadata, create_dirs=create_dirs)

    new_ds['test'].data = X_test
    new_ds['test'].target = y_test
    logger.info(f"Writing Transformed Dataset: {new_ds['test'].name}")
    new_ds['test'].dump(force=force, dump_path=dump_path, dump_metadata=dump_metadata, create_dirs=create_dirs)
    return dset

def pivot(dset, **pivot_opts):
    """Pivot data stored as a Pandas Dataframe

    pivot_opts:
        keyword arguments passed to pandas.Dataframe.pivot_table
    """
    pivoted = dset.data.pivot_table(**pivot_opts)
    ds_pivot = Dataset(dataset_name=f"{dset.name}_pivoted", metadata=dset.metadata, data=pivoted, target=None)
    ds_pivot.metadata['pivot_opts'] = pivot_opts

    return ds_pivot

def index_to_date_time(dset, suffix='dt'):
    """Transformer: Extract a datetime index into Date and Time columns"""
    df = dset.data.copy()
    df['Time']=df.index.time
    df['Date']=df.index.date
    df.reset_index(inplace=True, drop=True)
    new_ds = Dataset(dataset_name=f"{dset.name}_{suffix}", metadata=dset.metadata, data=df)
    return new_ds

def sklearn_transform(dset, transformer_name, transformer_opts=None, subselect_column=None, **opts):
    """
    Wrapper for any 1:1 (data in to data out) sklearn style transformer. Will run the .fit_transform
    method of the transformer on dset.data. If subselect_column is not None, it will treat the data
    like a dataframe and will subselect dset.data[subselect_column] to run the transformer on.

    Parameters
    ----------
    dset:
        Dataset
    transformer_name: string
        sklearn style transformer with a .fit_transform method avaible via sklearn_transformers.
    transformer_opts: dict
        options to pass on to the transformer
    subselect_column: string
        column name for dset.data to run the transformer on
    return_whole: boolean
        return the whole dataframe with a new column named "transformed"
    **opts:
        options to pass on to the fit_transform method

    Returns
    -------
    Dataset whose data is the result of the transformer.fit_transform
    """
    if transformer_name in sklearn_transformers():
        transformer = sklearn_transformers(keys_only=False).get(transformer_name)(**transformer_opts)
    else:
        raise ValueError(f"Invalid transformer name: {transformer_name}. See sklearn_transformers for available names.")
    if subselect_column:
        new_data = transformer.fit_transform(dset.data[subselect_column], **opts)
    else:
        new_data = transformer.fit_transform(dset.data, **opts)

    ds = Dataset(dataset_name=f"{dset.name}_{transformer.__class__.__name__}", metadata=dset.metadata, data=new_data)
    return ds
