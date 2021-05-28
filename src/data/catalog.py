import json
import pathlib
import os

from collections.abc import MutableMapping
from ..log import logger
from ..utils import load_json, save_json
from .. import paths
#from ..exceptions import ParameterError


__all__ = [
    'Catalog',
]


class Catalog(MutableMapping):
    """A catalog is a disk-backed dictionary of objects, each serializable as JSON.

    On disk, a Catalog is stored as a directory of JSON files, one file per object
    The stem of the filename (e.g. stem.json) is the key (name) of the catalog entry
    in the dictionary, so `catalog/key.json` is accessible via catalog['key'].
    """

    def __init__(self,
                 catalog_data=None,
                 catalog_dir="catalog",
                 catalog_path=None,
                 create=True,
                 entry_extension="json",
                 replace=False,
                 merge=True,
                 merge_priority="disk",
                 ):
        """
        catalog_data: Dict-like object containing data to be merged into the catalog
        catalog_dir: str, default 'catalog'
            Name of directory containing JSON catalog files. relative to `catalog_path`
        catalog_path: path. (default: paths['catalog_dir'])
            Location of `catalog_dir`
        create: Boolean
            if True, create the catalog if needed
        entry_extension: string
            file extension to use for serialized JSON files.
        replace: boolean
            If catalog exists on disk, delete and recreate it.
            If false, load existing data from disk
        merge: boolean
            If True, merge on-disk data with catalog_data using `merge_priority`
        merge_priority: {"disk", "data"}
            If using `catalog_data` with an existing repo, this indicates how to merge the two
            If disk, values already stored in the catalog will be retained
            If data, contents of `catalog_data` will override existing items on disk.

        """
        if catalog_path is None:
            self.catalog_path = paths['catalog_path']
        else:
            self.catalog_path = pathlib.Path(catalog_path)

        if replace is True and  merge is True and catalog_data:
            logger.warning("replace=True and merge=True with catalog_data is nonsensical. Setting merge=False")
            merge = False

        if replace is True and create is False:
            logger.warning("replace=True but create=False is nonsensical. Setting create=True")
            create = True

        self.catalog_dir = catalog_dir
        self.extension = entry_extension
        self.create = create
        self.replace = replace

        if self.catalog_dir_fq.exists():
            # Catalog exists on disk
            if catalog_data is not None and merge is False and replace is False:
                raise AttributeError("Must specity `merge=True` or `replace=True` if using `catalog_data` with an existing Catalog")
            if replace is True:
                logger.debug(f"Catalog {self.catalog_dir} found on-disk. Overwriting...")

        else: # Catalog not on disk
            logger.debug(f"Catalog dir: {self.catalog_dir} missing (create={self.create}, replace={self.replace}).")
            if self.create is True or self.replace is True:
                logger.debug(f"Creating {self.catalog_dir}")
                os.makedirs(self.catalog_dir_fq)
                logger.debug(f"Setting merge_priority to data")
                merge_priority = 'data'
            else:
                raise AttributeError(f"Catalog: {self.catalog_dir} does not exist but `create/replace` is False")

        if catalog_data is None:
            catalog_data = {}
            merge_priority = "disk"

        on_disk_catalog = self.load(return_dict=True)
        if replace is True:
            self.data = catalog_data
            self.save()
        else:
            if not catalog_data:
                logger.info(f"Reading catalog:{self.catalog_dir} from disk.")
                self.data = on_disk_catalog
            else:
                logger.debug(f"Merging catalog_data with {merge_priority} priority")
                if merge_priority == "disk":
                    self.data = {**catalog_data, **on_disk_catalog}
                elif merge_priority == "data":
                    self.data = {**on_disk_catalog, **catalog_data}
                else:
                    raise AttributeError(f"Unknown merge_priority:{merge_priority}")
                self.save()

    @property
    def file_glob(self):
        """glob string that will match all key files in this catalog directory.
        """
        return f"*.{self.extension}"

    @property
    def catalog_dir_fq(self):
        """pathlib.Path returning fully qualified path to catalog directory.
        """
        return self.catalog_path / self.catalog_dir

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save_item(key)

    def __delitem__(self, key):
        del self.data[key]
        self.del_item(key)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"<Catalog:{list(self.data.keys())}>"

    def __eq__(self, other):
        """Two catalogs are equal if they have the same contents,
        regardless of where or how they are stored on-disk.
        """
        return self.data == other.data

    def load(self, return_dict=False):
        """reload an entire catalog from its on-disk serialization.

        if return_dict is True, return the data that would have been loaded,
        but do not change the contents of the catalog.

        """
        catalog_dict = {}
        for catalog_file in self.catalog_dir_fq.glob(self.file_glob):
            catalog_dict[catalog_file.stem] = load_json(catalog_file)

        if return_dict is True:
            return catalog_dict

        self.data = catalog_dict

    def del_item(self, key):
        """Delete the on-disk serialization of a catalog entry"""
        filename = self.catalog_dir_fq / f"{key}.{self.extension}"
        logger.debug(f"Deleting catalog entry: '{key}.{self.extension}'")
        filename.unlink()

    def save_item(self, key):
        """serialize a catalog entry to disk"""
        value = self.data[key]
        logger.debug(f"Writing catalog entry: '{key}.{self.extension}'")
        save_json(self.catalog_dir_fq / f"{key}.{self.extension}", value)

    def save(self, paranoid=True):
        """Save all catalog entries to disk

        if paranoid=True, verify serialization is equal to in-memory copy
        """
        for key in self.data:
            self.save_item(key)
        if paranoid:
            old = self.data
            self.load()
            if old != self.data:
                logger.error("Save failed. On-disk serialization differs from in-memory catalog")
                self.data = old

    @classmethod
    def from_disk(cls, name, create=False, catalog_data=None, replace=None, **kwargs):
        """Load a catalog from disk.

        Parameters are a subset of Catalog.__init__
        as `catalog_data`, `replace` are not permitted."""
        if catalog_data is not None:
            raise AttributeError("'catalog_data' may not be specified using 'from_disk'")
        if replace is not None:
            raise AttributeError("'replace' may not be specified using 'from_disk'")
        catalog = cls(catalog_dir=name, create=create, catalog_data=None, replace=False, **kwargs)
        return catalog


    @classmethod
    def from_old_catalog(cls, catalog_file_fq, catalog_dir=None, **kwargs):
        """Create a catalog from an old combined-format JSON file

        Converts an old-format (combined) JSON catalog file to a new format (directory
        of JSON files) catalog file.

        Parameters
        ----------
        catalog_file_fq: String or Path
            fully qualified (or valid relative) path to old-format JSON catalog file
        catalog_dir: None or String or Path
            if None, new-format catalog directory will be the stem (extensionless part)
            of `catalog_file_fq`

        Other parameters are the same as per `Catalog.__init__()`
        """
        catalog_file_fq = pathlib.Path(catalog_file_fq)

        if catalog_file_fq.exists():
            catalog_dict = load_json(catalog_file_fq)
        else:
            logger.warning(f"Old catalog file:'{catalog_file_fq}' does not exist.")
            catalog_dict = {}

        if catalog_dir is None:
            catalog_dir = pathlib.Path(catalog_file_fq).stem
        else:
            catalog_dir = pathlib.Path(catalog_dir)

        catalog = cls(catalog_dir=catalog_dir,
                      catalog_data=catalog_dict,
                      **kwargs)
        return catalog
