import sys 
import os

from ddc_onset.h5pyize import DatasetH5pyizer
from ddc_onset.h5pyize_onsets import OnsetH5pyizer

def do(dir_of_dirs, where_to_save_to):
    h5pyizer = DatasetH5pyizer(where_to_save_to)
    h5pyizer.h5pyize( dir_of_dirs, dataset_name="foldername")

def do_onset(dir_of_dirs, where_to_save_to, music_h5_path):
    h5pyizer = OnsetH5pyizer(where_to_save_to, music_h5_path)
    h5pyizer.h5pyize( dir_of_dirs, dataset_name_for_onset="filename", dataset_name_for_audio="foldername")


if __name__=="__main__":
    print(sys.argv)
    if len(sys.argv) < 3: 
        print(f"""
            usage:
              python {sys.argv[0]} (do/clean) (root directory where music is) 
              """)
    
    if sys.argv[1] == "do":
        if len(sys.argv) < 4:
            print(f"""
            usage:
              python {sys.argv[0]} do (root directory where music is) (where_to_save_to)
              """)
        assert (os.path.isdir(sys.argv[2]))
        do(sys.argv[2], sys.argv[3])
        # 

    elif sys.argv[1] == "onset":
        if len(sys.argv) < 5:
            print(f"""
            usage:
              python {sys.argv[0]} do (root directory where charts are) (music_h5_path) (where_to_save_to) 
              """)
        do_onset(sys.argv[2], sys.argv[4], sys.argv[3])
        