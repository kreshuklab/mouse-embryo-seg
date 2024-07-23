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
1. Download the 3D UNet model files, trained to predict the nuclei (foreground + outlines) from [here](https://oc.embl.de/index.php/s/nV10v55nbfz8kX1)
2. Add model to PlantSeg: Create directory `~/.plantseg_models/confocal_unet_mouse_embryo_nuclei` and copy the downloaded files (`config_train.yml`, `last_checkpoint.pytorch`, `best_checkpoint.pytorch`) into it.
3. Update `path` attribute in the plantseg's [YAML config](configs/plantseg_nuclei/plantseg_pmaps.yaml) to point to the directory containing the nuclei stained images
4. Predict nuclei masks and outlines with PlantSeg:
```bash
plantseg --config configs/plantseg_nuclei/plantseg_pmaps.yaml
``` 
4. Assuming the nuclei stained images were in `~/embryo_nuclei` directory, extract the 2nd channel from the predictions using the script:
```bash
python extract_channel.py --channel 1 --input-dir ~/embryo_nuclei --output-dir ~/nuclei_boundaries
```
5. Update `path` attribute in the [YAML config](configs/plantseg_nuclei/plantseg_seg.yaml) to point to the directory containing the predicted boundaries and segment the nuclei using PlantSeg:
```bash
plantseg --config configs/plantseg_nuclei/plantseg_seg.yaml
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
1. Download the 3D UNet model files, trained to predict the membranes from [here](https://oc.embl.de/index.php/s/Z7XUdh67FT5N70i)
2. Add model to PlantSeg: Create directory `~/.plantseg_models/lightsheet_unet_mouse_embryo_membranes` and copy the downloaded files (`config_train.yml`, `last_checkpoint.pytorch`, `best_checkpoint.pytorch`) into it.
3. Update `path` attribute in the plantseg's [YAML config](configs/plantseg_membranes/plantseg_config.yaml) to point to the directory containing the membrane stained images
4. Segment the nuclei using PlantSeg:
```bash
plantseg --config configs/plantseg_membranes/plantseg_config.yaml
``` 
The segmentation results will be saved with the hdf5 format inside the image directory. 


## Network training
UNet models were trained with the [pytorch-3dunet](https://github.com/wolny/pytorch-3dunet) package. The data used for training can be donwloaded [here](https://doi.org/10.5281/zenodo.6546550).

## Cite
```
@article{https://doi.org/10.15252/embj.2022113280,
author = {Bondarenko, Vladyslav and Nikolaev, Mikhail and Kromm, Dimitri and Belousov, Roman and Wolny, Adrian and Blotenburg, Marloes and Zeller, Peter and Rezakhani, Saba and Hugger, Johannes and Uhlmann, Virginie and Hufnagel, Lars and Kreshuk, Anna and Ellenberg, Jan and van Oudenaarden, Alexander and Erzberger, Anna and Lutolf, Matthias P and Hiiragi, Takashi},
title = {Embryo‐uterine interaction coordinates mouse embryogenesis during implantation},
journal = {The EMBO Journal},
volume = {42},
number = {17},
pages = {e113280},
keywords = {biophysical modeling, embryo, engineering, Implantation, uterus},
doi = {https://doi.org/10.15252/embj.2022113280},
url = {https://www.embopress.org/doi/abs/10.15252/embj.2022113280},
eprint = {https://www.embopress.org/doi/pdf/10.15252/embj.2022113280},
year = {2023}
}
```
