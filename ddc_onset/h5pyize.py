from tqdm import tqdm 
import torch
import torchaudio
import torchaudio.transforms as T
import soundfile
import h5py
import librosa
import os
from .spectral import SpectrogramExtractor
from .constants import SAMPLE_RATE


class DatasetH5pyizer():
    """
    Utility for h5pyizing the dataset.
    """
    def __init__(self, where_to_save, debug=False, accepted_extensions = [".mp3",".wav",".ogg",".aiff",".flac",".m4a",".opus"]):
        self.spec_extractor = SpectrogramExtractor()
        assert where_to_save
        self.where_to_save = where_to_save
        self.debug = debug
        self.accepted_extensions = accepted_extensions
        self.resamplers = { }
    
    def _pbar(self, biggest_dir):
        """
        makes an iterable (doubles as a progress bar) of audio file paths.
        """
        filepaths = []
        if self.debug: print("making pbar (seconds ~ minutes depending on size )")
        for root, _, files in os.walk(biggest_dir):
            for file in files:
                for ext in self.accepted_extensions:
                    if file.lower().endswith(ext):
                        filepaths.append(os.path.join(root,file))
                        break
        return tqdm(filepaths)   

    def _get_spec(self, filename):
        # x, sr = torchaudio.load(filename) torchaudio seems to be quite brittle
        # x, sr = soundfile.read(filename) 
        x , sr = librosa.load(filename,sr=SAMPLE_RATE) # torchaudio resampler crashes when sr = 44099.
        #print("sr is ",sr)
        #print("x shape is", x.shape)
        # if len(x.shape) >= 2:
        #     x = x.mean(axis=1) # axis=0 for torchaudio.
        x = torch.Tensor(x)
        if sr != SAMPLE_RATE:
            try:
                resampler = self.resamplers[int(sr)]
            except KeyError:
                self.resamplers[int(sr)] = T.Resample(sr, SAMPLE_RATE, dtype=x.dtype)
                resampler = self.resamplers[int(sr)]
                if self.debug:
                    print(f"file {filename} has sr {sr}")
            x = resampler(x)
        
        x = x.unsqueeze(0)
        with torch.no_grad():
            ret = self.spec_extractor(x).squeeze(0)
        return ret # [num_frames, num_mel_bands, num_fft_frame_lengths]

    def _dataset_name(self, audiopath, biggest_dir, dataset_name):
        ret = None
        dataset_name = dataset_name.strip().lower()
        if dataset_name == "foldername":
            ret = str(os.path.dirname(audiopath))
        elif dataset_name == "filename":
            ret = str(audiopath)
        
        ret = ret.replace( str(biggest_dir), "")
        if ret[0] == '/': ret = ret[1:]
        return ret

    def h5pyize(self, biggest_dir, dataset_name="foldername"):
        """
        > "dataset_name" determines what we use as the dataset name,
        - "foldername" : use the folder where the audio is located
        - "filename" : use the filename of the audio.
        """
        pbar = self._pbar(biggest_dir)
        h5file = h5py.File(self.where_to_save,'w')
        for filename in pbar:
            pbar.set_description(filename)
            mels = self._get_spec(filename)
            # get h5py dset name
            name = self._dataset_name(filename, biggest_dir, dataset_name)
            h5file.create_dataset(name, data=mels)

            

                





