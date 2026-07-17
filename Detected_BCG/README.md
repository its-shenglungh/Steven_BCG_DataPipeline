# Data Processing for Detected BCG
Once you have the fits files for the detected BCG, we can begin the processing of the file with the end goal of generating spectra and calculating molecular gas masses. There will be several steps before we can get there, but the outline is as such:
- Identifying the velocity channels with significant emissions
- Selecting the spectral cube with the best binned value (e.g. 50km/s, 75km/s, etc.), and adding beam information if not present
- Calculating channel-to-channel root-mean-squared (RMS) and variance values
- Collapsing the cube and generating a Moment-0 map
- Extracting best fit 2D Gaussian aperture for optimizing flux capture
- Generating final spectrum with inverse variance weighting
