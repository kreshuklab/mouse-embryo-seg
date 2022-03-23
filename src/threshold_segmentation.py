import argparse
import os
from skimage import measure

import h5py
import numpy as np


def segment_volume(pmaps, th):
    print(f'Threshold: {th}')
    mask = pmaps > th
    mask = mask.astype(np.uint8)

    seg = measure.label(mask, connectivity=1)
    seg = seg.astype('uint16')
    return seg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TH seg')
    parser.add_argument('--pmaps', type=str, required=True, help='path to the network predictions')
    parser.add_argument("--threshold", type=float, default=0.9, help="nuclei mask threshold")
    parser.add_argument('--channel', type=int, required=False, default=0, help='Nuclei pmaps channel')
    args = parser.parse_args()

    in_file = args.pmaps
    out_file = os.path.splitext(in_file)[0] + '_threshold.h5'
    c = args.channel

    with h5py.File(in_file, 'r') as f:
        print(f'Extracting pmaps from: {in_file}')
        pmaps = f['predictions'][c]

    seg = segment_volume(pmaps, args.threshold)
    print(f'Saving results to: {out_file}')
    with h5py.File(out_file, 'w') as f:
        output_dataset = 'cc_segmentation'
        if output_dataset in f:
            del f[output_dataset]
        f.create_dataset(output_dataset, data=seg, compression='gzip')
