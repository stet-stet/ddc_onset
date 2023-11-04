import pathlib
import unittest # I have no idea how to test if a h5py as properly created
import os 
import h5py

from .paths import TEST_DATA_DIR
from .h5pyize import DatasetH5pyizer

_TEST_PATH = pathlib.Path( TEST_DATA_DIR )
_WHERE_TO_SAVE_TO = "temptemptemptemptemptemptemptemptemptemptemp.h5"

class TestH5pyize(unittest.TestCase):
    def setUp(self):
        self.h5pyizer = DatasetH5pyizer(_WHERE_TO_SAVE_TO)

    def test_h5pyize(self):        
        self.h5pyizer.h5pyize( _TEST_PATH, dataset_name="filename")
        # open file, and let's get checking.
        h5file = h5py.File(_WHERE_TO_SAVE_TO,'r')
        try:
            filenames = os.listdir(_TEST_PATH)
            accepted_extensions = self.h5pyizer.accepted_extensions
            dataset_names = [ filename for filename in os.listdir(_TEST_PATH) \
                                if os.path.splitext(filename)[1].lower() in accepted_extensions and len(filename)>=4 ]
            for dataset_name in dataset_names:
                self.assertTrue(h5file[dataset_name] is not None)
                print(f"{dataset_name} has shape {h5file[dataset_name].shape}")
        
        finally:
            os.remove( _WHERE_TO_SAVE_TO )