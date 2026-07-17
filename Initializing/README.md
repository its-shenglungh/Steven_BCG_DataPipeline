# Preliminary Check on BCG Spectral Cubes

This is the beginning of a series of steps for the project. In this section, I will be going over what to do once you obtain the BCG spectral cube. If you want to go straight into the reimaging, please visit my [Notion](https://petite-year-f89.notion.site/ALMA-Data-MacOS-ARM64Pipeline-Related-Info-20a5d039952c80b9b529c5e07e5c17e8) page on what to do with the iclean function as well as regenerating the MS of the data.
---

## CARTA
Before starting the data processing for the targets, we will first  perform a visual preliminary assessment of our targets in order to separate detected from non-detected targets at this stage. This allows us to streamline the subsequent data analysis.

To do so, we use [**CARTA**](https://cartavis.org) which is a great image visualization and analysis tool. What we are looking for is the spectral profiler functions in the interface. To generate a spectrum, draw a circular aperture at the image centre (or where you expect the signal to be), and a spectral profile should show up at the profiler window.

A target is considered *detected* when the following conditions are met:
- The spectrum shows a clear peak feature
- Spatially coincident bright emission is visible across several velocity channels in the image cube

---

## CASA Reimaging
If the pipeline delivered product has bright emission, this section can be ignored and move to the **Detected-BCG** folder to start doing data processing. If the signal is weak or not visible, reimaging will be necessary.

The CASA version used in this project is consistent to the version that was used in the pipeline-delivered products (version 6.6.5.31). In the case where other version of CASA is in need of use, please refer to the offical [**CASA**](https://casa.nrao.edu/casa_obtaining.shtml) website for the correct version as well as software control.

---

## Manual Re-Imaging Using *iclean*
As of now (July of 2026), the original **tclean** function is not supported and used on the silicon chip for Mac, so we will be using [***iclean***](https://github.com/casangi/casagui/wiki/Interactive-Clean#startup) function. One important note is that this feature is still currently under active development even if the feature itself has passed the test on the CASA development team. If there are issues regarding the function, please submit a ticket to the [ALMA helpdesk](https://help.almascience.org) for more information.

### Installing the iclean package
Assuming the CASA version is all set up on the computer, please move to the terminal screen. We will be launching CASA from there for the reimaging.
```
# Launch the CASA version
/Applications/CASA-6.7-arm64.app/Contents/MacOS/casa
/Applications/CASA-6.6.5.31.app/Contents/MacOS/casa

# Installing the casagui and iclean function
!pip3 install casagui==0.3.70
from casagui.apps import run_iclean
```
There are a lot of arguments for the iclean functions, but most will be familiar to those who have used tclean before. For example;
```
run_iclean( vis='test.ms', imagename='try1', imsize=512, cell='12.0arcsec', specmode='cube', 
interpolation='nearest', nchan=5, start='1.0GHz', width='0.2GHz', pblimit=-1e-05, 
deconvolver='hogbom', threshold='0.001Jy', niter=50, cycleniter=10, cyclefactor=3 );
```

### Work Flow for iclean
Below is the general workflow with iclean:
- The MS folder that will be used in ending with "**_target.ms.contsub**"
    - We will launch CASA from the working directory in the calibrated directory
- The example is in the cell below; the arugments are taken based on the supplied **log folder** from the pipeline since this gives a good idea on roughly where the starting parameters should be:
    - Go to the log folder and open it (should open with Console app on Mac)
    - From there, use the 'find keyword' feature and lookd for "**targets_line.ms**", and the image name should be something like "**sci_spw[].cube**"
    - Copy the command from the script, and follow the example below and enter it to the terminal where the CASA is launched
```
run_iclean( vis='uid___A002_X1130247_X1db72_targets.ms.contsub2',
imagename='D32_revised', imsize=[270, 270], cell='0.29arcsec', usemask='user', 
phasecenter='ICRS 03:31:32.1698 -027.32.06.976', stokes='I', specmode='cube', 
interpolation='nearest', nchan=237, start='129.69ex71041723GHz', width='7.8135626MHz', outframe='LSRK',
pblimit=0.2, deconvolver='hogbom', restoringbeam='common', pbcor=True,  
gridder='standard', niter=200, threshold='0.0mJy', weighting='briggs', 
robust=0.5, nsigma=0.0)
```
After running the above in the CASA terminal, the interactive screen should appear after some initial setup within the terminal (interactive screen will open based on your preferred browser)
- The interactive screen allows you to manually draw your mask and perform the cleaning process
- Our goal is to clean in a way that the peak residual value and the total flux value is close to zero
- For channels with signals we want to clean the signal away as much as possible, while off channel should remain roughly the same

### After Cleaning
After the desired cleaning is achieved, we can the stop botton on the interactive screen, and the results will be saved and folders generated as well. 

**Very Important**: iclean function does not automatically perform the primary beam correction during the cleaning and extracting process even if the pbcor argument is set to True.

To perform pbcor function manually, in the same terminal that you have been working on, input the following code:
```
# Manually operating the pbcor
impbcor(imagename='[ ].image', pbimage='[ ].pb', 
				outfile='[ ].pbcor', mode='divide', cutoff=0.2)
```
From here, we can use the exportfit() function to convert a CASA image to fits file.
```
# Using exportfits to convert CASA image to fits file
exportfits('imagename', fitsimage='', velocity=False, optical=False, bitpix=-32, 
					minpix=0, maxpix=-1, overwrite=False, dropstokes=False, 
					stokeslast=True, history=True, dropdeg=False)
```
Once the fits file is exported, use CARTA to do some checking if something is wrong. If there are confusion, please refer to my [Notion](https://petite-year-f89.notion.site/ALMA-Data-MacOS-ARM64Pipeline-Related-Info-20a5d039952c80b9b529c5e07e5c17e8#20e5d039952c801b8658df478fbb2f4a) page for more details.

---
## Preparing BCG Data (Under construction)

After the targets are reimaged, we will be preparing them for the first passing spectral profile which is neccessary for categorizing them. This will be done via the first part of the pipeline, and a folder containing all the BCG data as well as a csv file containing the basic information is needed. The folder structure should look like the following:

```
project/
├── BCG Data/
│   ├── Origin/
│   │   ├── member....fits
│   │   └── ...
│   └── Updated/
│
├── pipeline/
│   ├── prepare_bcg_data.py
│
├── notebooks/
│   └── Preparing BCG.ipynb
│
└── requirements.txt
```

A notebook example can be found within the Initializing folder itself, so please refer to it for the correct import and a check on the output.

---
## First Passing Spectral Profile (In progress)

---

## Final Note
Congradulation! You now have a fits file that can be used for the data analysis. Remember to follow the correct processing steps depending on the category that the BCG belongs to.
