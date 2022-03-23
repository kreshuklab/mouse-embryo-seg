# mouse-embryo-seg
3D segmentation of nuclei (fixed) and cells (live) of the developing mouse embryo

## Prerequisites
- Linux
- modern NVIDIA GPU with 10+ GB of memory (e.g. Nvidia 2080Ti)
- CUDA

## Installation

1. Create conda environment with the required dependencies:
```bash
conda env create -f 
```
2. Activate conda environment:
```bash
conda activate embryo-seg
```
3. Checkout the repository:
```bash
git clone https://github.com/kreshuklab/mouse-embryo-seg.git
```
4. Add the repository directory to the PYTHONPATH environment variable (assumes that the repo was cloned to `~/mouse-embryo-seg`)
```bash
export PYTHONPATH="~/mouse-embryo-seg:$PYTHONPATH"
```

## Segmentation of fixed images of nuclei (confocal)

The pipeline for nuclei segmentation of the nuclei consists of 2-steps: 
1. semantic segmentation with a 3D U-Net, where the target task is predicting the nuclei mask (1st channel) together with the nuclei outlines (2nd channel)
2. instance segmentation with one of the following strategies:
    - using the 2nd channel (nuclei boundaries) + [plantseg](https://github.com/hci-unihd/plant-seg) segmentation
    - thresholding on the 1st channel (nuclei mask) + connected components (baseline)
    
### PlantSeg's nuclei segmentation (1)
1. Download the 3D UNet model, trained to predict the nuclei (foreground + outlines) from [here](todo)
2. Edit the network prediction [YAML config](todo):
    2.1 change `model_path` attribute to point to the downloaded model file
    2.2 add the correct paths to the nuclei images (`file_paths` section of the yaml config)
    2.3 change the `output_dir` attribute, i.e. path to the directory where the predictions will be saved
3. Run the network prediction:
```bash
predict3dunet --config experiments/3dunet_nuclei_confocal/config_predict.yml
```
4. Assuming the predictions were saved in `~/nuclei_predictions` directory, extract the 2nd channel from the predictions using the script:
```bash
python extract_channel.py --channel 1 --input-dir ~/nuclei_predictions --output-dir ~/nuclei_boundaries
```
5. Update `path` attribute in the plantseg's [YAML config](todo) to point to the `~/nuclei_boundaries` directory
6. Segment the nuclei using PlantSeg:
```bash
plantseg --config CONFIG_PATH experiments/plantseg_configs/nuclei_segmentation.yml
```  
The segmentation results will be saved with the hdf5 format inside the `~/nuclei_boundaries` directory.
By default GASP agglomeration strategy with MutexWatershed linkage criteria will be used. See [A. Bailoni et al.](https://arxiv.org/abs/1906.11713) for more info.

### Connected components baseline
In order to compare the above results with the connected components baseline:
Execute the steps 1-3 from above and then (assuming the network predictions were saved in `~/nuclei_predictions`) execute:
```bash
python threshold_segmentation.py --pmaps ~/nuclei_predictions
```
The segmentation results will be saved in the network prediction hdf5 files as a separate dataset called `cc_segmentation`.
     
## Segmentation of live membrane stained images (light-sheet)
1. Download the 3D UNet model files, trained to predict the boundaries from [here](todo)
2. Add model to PlantSeg: Create directory `~/.plantseg_models/lightsheet_unet_mouse_embryo` and copy the downloaded files (`config_train.yml`) into it.
3. Update `path` attribute in the plantseg's [YAML config](todo) to point to the directory containing the membrane stained images
4. Segment the nuclei using PlantSeg:
```bash
plantseg --config CONFIG_PATH experiments/plantseg_configs/membrane_segmentation.yml
``` 
The segmentation results will be saved with the hdf5 format inside the image directory. 
