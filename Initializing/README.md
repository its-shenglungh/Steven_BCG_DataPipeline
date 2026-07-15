# Preliminary Check on BCG Spectral Cubes

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

