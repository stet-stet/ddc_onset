import os
import json
import h5py
import numpy as np
from tqdm import tqdm

from .constants import SAMPLE_RATE, FRAME_RATE

_FEATS_HOP = SAMPLE_RATE // FRAME_RATE
_SECS_HOP = _FEATS_HOP / SAMPLE_RATE

class OnsetH5pyizer():
    """
    H5pyizes the onsets onto an array that is of the same length as the spectrograms.
    array has type bool.

    Requires the charts to be preprocessed with ddc-like code and have a corresponding json: 1 json file for each chart.
    """
    def __init__(self, where_to_save, music_h5_path, debug=False):
        assert where_to_save
        self.where_to_save = where_to_save
        self.music_h5_path = music_h5_path
        self.debug=debug

    def _pbar(self, biggest_dir, chart_file_ext=".osu.json"):
        """
        makes an iterable (doubles as a progress bar) of processed-chart file paths.
        """
        filepaths = []
        self.debug: print("making pbar (seconds ~ minutes depending on size)")
        for root, _, files in os.walk(biggest_dir):
            for file in files:
                if file.endswith(chart_file_ext):
                    filepaths.append(os.path.join(root,file))
        return tqdm(filepaths)

    def _dataset_name(self, chartpath, biggest_dir, dataset_name):
        ret = None
        dataset_name = dataset_name.strip().lower()
        if dataset_name == "foldername":
            ret = str(os.path.dirname(chartpath))
        elif dataset_name == "filename": #default
            ret = str(chartpath)
        
        ret = ret.replace( str(biggest_dir), "")
        if ret[0] == '/': ret = ret[1:]
        return ret
    
    def _get_onset_frame_nums_from_chart(self, chartpath):
        with open(chartpath,'r') as file:
            rawchart = json.load(file)
        times = [float(e[2]) + float(rawchart['offset'])/1000 for e in rawchart['charts'][0]['notes']]
        times = [int(e/_SECS_HOP) for e in times]
        return times
    
    def _get_audio_filename(self, chartpath):
        with open(chartpath,'r') as file:
            rawchart = json.load(file)
        return os.path.join(os.path.dirname(chartpath),rawchart['music_fp'])
    
    def _get_audio_dsetname(self, audiopath, biggest_dir, dataset_name="foldername"):
        ret = None
        dataset_name = dataset_name.strip().lower()
        if dataset_name == "foldername":
            ret = str(os.path.dirname(audiopath))
        elif dataset_name == "filename":
            ret = str(audiopath)
        
        ret = ret.replace( str(biggest_dir), "")
        if ret[0] == '/': ret = ret[1:]
        return ret
    
    def h5pyize(self, biggest_dir, dataset_name_for_onset="filename", dataset_name_for_audio="foldername"):
        pbar = self._pbar(biggest_dir)
        h5file = h5py.File(self.where_to_save,'w')
        musich5 = h5py.File(self.music_h5_path, 'r')

        for chartpath in pbar:
            musicpath = self._get_audio_filename(chartpath)
            musicdsetname = self._get_audio_dsetname(musicpath, biggest_dir, dataset_name_for_audio)
            specframes = musich5[musicdsetname].shape[0]
            ret = np.zeros( (specframes,) , dtype=np.bool)
            onset_framenums = self._get_onset_frame_nums_from_chart(chartpath)
            try:
                assert(max(onset_framenums) < specframes + 2)
            except AssertionError as e:
                print(onset_framenums)
                print(chartpath)
                print(specframes)
                raise e 
            
            for num in onset_framenums:
                try:
                    ret[num] = 1
                except IndexError:
                    pass
            name = self._dataset_name(chartpath, biggest_dir, dataset_name_for_onset)
            h5file.create_dataset(name, data=ret)
        h5file.close()
        musich5.close()





