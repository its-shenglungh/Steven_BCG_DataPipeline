# Steven_BCG_DataPipeline

Welcome to an overview and complete guide to the ALMA BCG data processing for Steven's master project. The ALMA program ID is 2023.1.01066.S (P.I. Tracy Webb). There are multiple steps in the data processing, and each step will have its own folder as well as their README files and instructions. Here will just be an overview of the pipeline itself, and the details will be in individual folder.

**Disclaimer:** This project is done on Apple MacBook Pro with Apple M3 Pro chip. The following instructions are tailored for this particular machine, so CASA will be running on the Mac version instead of the usual version.


## Environments and CASA Versions
Other than the reimaging from the CASA pipeline itself, all data processing will be working in a specific environment that I have tailored for this project. While the packages should not be outdated anytime soon, please double check ahead of time just in case.

If you also have questions on how to create or delete an enviroment (or duplicating, etc), please go and refer to the **Environment** folder.

## Preliminary Check on the BCG Spectral Cubes
Before we start, we need to first categorize our BCG into two groups: detected and non-detected. To do so, we can use the **CARTA** software and look at the spectrum window to do a visual assessment. From here, we can use **CASA** to do reimaging for the desired bin values for velocity channel for the spectral cube. The reimaged products are now ready for the data processing.

## Data Processing for Detected BCG
For the detected BCGs, the data processing is roughly as follows:
  - Identifying velocity channels that show significant emission
  - Collapsing over the selected velocity range to produce an integrated-intensity (moment-0) map
  - Generating a 2D Gaussian profile to maximize captured flux density
  - Producing a spectral profile for the target

## Data Processing for Non-detected BCG
For the non-detected BCGs, the data processing is roughly as follows:
- Collapsing over a chosen fixed velocity range to produce an integrated-intensity (moment-0) map
- Calculating channel-to-channel RMS values 
- Adopting RMS values as upper limits

## Stacking Procedure
This section is used if a better signal is desired for non-detected (or general) targets. By stacking their moment-0 map, the averaged signal can serve as a good constraints to future analysis.

## Data Analysis
This section shows all the analysis that was done in this project. All analysis are heavily dependent on **Hierarchical Bayseian Linear Regression** method due to a large population of upper limits in the data. This is a modified version of censored fitting or surivial analysis.
