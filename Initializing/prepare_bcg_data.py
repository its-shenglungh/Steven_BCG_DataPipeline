from pathlib import Path
import logging
import shutil
from typing import Tuple

import numpy as np
import pandas as pd
import astropy.units as u

from astropy.coordinates import SkyCoord
from astropy.io import fits


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PROJECT_DIR = Path("..")
DATA_DIR = PROJECT_DIR / "BCG Data"

ORIGIN_DIR = DATA_DIR / "Origin"
UPDATED_DIR = DATA_DIR / "Updated"

INPUT_CATALOG = ORIGIN_DIR / "Basic BCG Info - origin.csv"
OUTPUT_CATALOG = UPDATED_DIR / "Basic BCG Info - updated.csv"

FITS_PATTERN = "member*.fits"

RA_COLUMN = "RA (deg)"
DEC_COLUMN = "DEC (deg)"

MAX_SEPARATION = 30 * u.arcsec

REQUIRED_FITS_KEYWORDS = [
    "OBSRA",
    "OBSDEC",
    "BMAJ",
    "BMIN",
    "BPA",
]


# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Processing functions
# ---------------------------------------------------------------------

def validate_catalog(
    catalog: pd.DataFrame,
    ra_column: str = RA_COLUMN,
    dec_column: str = DEC_COLUMN
) -> None:
    """Confirm that the required catalog columns exist."""

    required_columns = {ra_column, dec_column}
    missing_columns = required_columns - set(catalog.columns)

    if missing_columns:
        raise ValueError(
            "Input catalog is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if catalog[[ra_column, dec_column]].isna().any().any():
        raise ValueError(
            "The input catalog contains missing RA or Dec values."
        )


def read_fits_metadata(fits_file: Path) -> dict:
    """
    Read coordinates and synthesized-beam information from one FITS file.
    """

    with fits.open(fits_file) as hdul:
        header = hdul[0].header

        missing_keywords = [
            keyword
            for keyword in REQUIRED_FITS_KEYWORDS
            if keyword not in header
        ]

        if missing_keywords:
            raise KeyError(
                f"{fits_file.name} is missing FITS keywords: "
                + ", ".join(missing_keywords)
            )

        metadata = {
            "OBSRA": float(header["OBSRA"]),
            "OBSDEC": float(header["OBSDEC"]),
            "BMAJ (arcsec)": (
                float(header["BMAJ"]) * u.deg
            ).to_value(u.arcsec),
            "BMIN (arcsec)": (
                float(header["BMIN"]) * u.deg
            ).to_value(u.arcsec),
            "BPA (deg)": float(header["BPA"]),
        }

    return metadata


def create_sparcs_id(ra_deg: float, dec_deg: float) -> str:
    """
    Create an identifier in the form SpARCShhmm±ddmm.
    """

    coordinate = SkyCoord(
        ra=ra_deg * u.deg,
        dec=dec_deg * u.deg
    )

    ra_string = coordinate.ra.to_string(
        unit=u.hour,
        sep=":",
        pad=True,
        precision=3
    )

    dec_string = coordinate.dec.to_string(
        unit=u.deg,
        sep=":",
        alwayssign=True,
        pad=True,
        precision=3
    )

    ra_parts = ra_string.split(":")
    dec_parts = dec_string.split(":")

    ra_short = ra_parts[0] + ra_parts[1]
    dec_short = dec_parts[0] + dec_parts[1]

    return f"SpARCS{ra_short}{dec_short}"


def build_catalog_coordinates(
    catalog: pd.DataFrame,
    ra_column: str = RA_COLUMN,
    dec_column: str = DEC_COLUMN
) -> SkyCoord:
    """Create the SkyCoord catalog once for all target matching."""

    return SkyCoord(
        ra=catalog[ra_column].astype(float).to_numpy() * u.deg,
        dec=catalog[dec_column].astype(float).to_numpy() * u.deg
    )


def match_catalog_row(
    ra_deg: float,
    dec_deg: float,
    catalog: pd.DataFrame,
    catalog_coordinates: SkyCoord,
    max_separation: u.Quantity = MAX_SEPARATION
) -> Tuple[pd.Series, u.Quantity]:
    """
    Match one FITS coordinate to the nearest catalog row.
    """

    fits_coordinate = SkyCoord(
        ra=ra_deg * u.deg,
        dec=dec_deg * u.deg
    )

    # Direct separation calculation avoids match_to_catalog_sky()
    # compatibility problems in the CASA environment.
    separations = fits_coordinate.separation(catalog_coordinates)

    match_index = int(np.argmin(separations))
    minimum_separation = separations[match_index]

    if minimum_separation > max_separation:
        raise ValueError(
            f"No reliable catalog match. Nearest source is "
            f"{minimum_separation.to_value(u.arcsec):.3f} arcsec away; "
            f"maximum allowed separation is "
            f"{max_separation.to_value(u.arcsec):.3f} arcsec."
        )

    return catalog.iloc[match_index].copy(), minimum_separation


def process_target(
    fits_file: Path,
    catalog: pd.DataFrame,
    catalog_coordinates: SkyCoord,
    output_directory: Path,
    max_separation: u.Quantity = MAX_SEPARATION
) -> dict:
    """
    Process one FITS target and return its output-catalog row.
    """

    metadata = read_fits_metadata(fits_file)

    sparcs_id = create_sparcs_id(
        metadata["OBSRA"],
        metadata["OBSDEC"]
    )

    matched_row, separation = match_catalog_row(
        ra_deg=metadata["OBSRA"],
        dec_deg=metadata["OBSDEC"],
        catalog=catalog,
        catalog_coordinates=catalog_coordinates,
        max_separation=max_separation
    )

    output_fits = output_directory / f"{sparcs_id}.fits"

    # copy2 preserves file metadata.
    shutil.copy2(fits_file, output_fits)

    output_row = matched_row.to_dict()

    # Preserve provenance before replacing the original ID.
    if "ID" in output_row:
        output_row["Original ID"] = output_row["ID"]

    output_row["ID"] = sparcs_id

    output_row.update({
        "BMAJ (arcsec)": metadata["BMAJ (arcsec)"],
        "BMIN (arcsec)": metadata["BMIN (arcsec)"],
        "BPA (deg)": metadata["BPA (deg)"],
        "Match separation (arcsec)": separation.to_value(u.arcsec),
        "Original FITS file": fits_file.name,
        "Updated FITS file": output_fits.name,
    })

    return output_row


# ---------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------

def run_pipeline(
    origin_directory: Path = ORIGIN_DIR,
    output_directory: Path = UPDATED_DIR,
    input_catalog: Path = INPUT_CATALOG,
    output_catalog: Path = OUTPUT_CATALOG,
    fits_pattern: str = FITS_PATTERN,
    max_separation: u.Quantity = MAX_SEPARATION
) -> pd.DataFrame:
    """
    Run the FITS preparation pipeline for all available targets.
    """

    output_directory.mkdir(parents=True, exist_ok=True)

    if not input_catalog.exists():
        raise FileNotFoundError(
            f"Input catalog does not exist: {input_catalog}"
        )

    fits_files = sorted(origin_directory.glob(fits_pattern))

    if not fits_files:
        raise FileNotFoundError(
            f"No FITS files matching '{fits_pattern}' were found in "
            f"{origin_directory}"
        )

    catalog = pd.read_csv(input_catalog)
    validate_catalog(catalog)

    catalog_coordinates = build_catalog_coordinates(catalog)

    logger.info("Found %d FITS files.", len(fits_files))

    successful_rows = []
    failed_targets = []

    for index, fits_file in enumerate(fits_files, start=1):
        logger.info(
            "Processing %d/%d: %s",
            index,
            len(fits_files),
            fits_file.name
        )

        try:
            output_row = process_target(
                fits_file=fits_file,
                catalog=catalog,
                catalog_coordinates=catalog_coordinates,
                output_directory=output_directory,
                max_separation=max_separation
            )

            successful_rows.append(output_row)

        except Exception as error:
            logger.error(
                "Failed to process %s: %s",
                fits_file.name,
                error
            )

            failed_targets.append({
                "FITS file": fits_file.name,
                "Error": str(error)
            })

    if not successful_rows:
        raise RuntimeError(
            "The pipeline did not successfully process any targets."
        )

    updated_catalog = pd.DataFrame(successful_rows)

    preferred_columns = [
        "ID",
        "Original ID",
        RA_COLUMN,
        DEC_COLUMN,
        "z",
        "CO (2-1) (GHz)",
        "BMAJ (arcsec)",
        "BMIN (arcsec)",
        "BPA (deg)",
        "Match separation (arcsec)",
        "Original FITS file",
        "Updated FITS file",
    ]

    ordered_columns = [
        column
        for column in preferred_columns
        if column in updated_catalog.columns
    ]

    remaining_columns = [
        column
        for column in updated_catalog.columns
        if column not in ordered_columns
    ]

    updated_catalog = updated_catalog[
        ordered_columns + remaining_columns
    ]

    # Creates the CSV when absent and overwrites it when present.
    updated_catalog.to_csv(output_catalog, index=False)

    logger.info(
        "Saved %d processed targets to %s",
        len(updated_catalog),
        output_catalog
    )

    if failed_targets:
        failure_file = output_directory / "failed_targets.csv"
        pd.DataFrame(failed_targets).to_csv(failure_file, index=False)

        logger.warning(
            "%d targets failed. Details saved to %s",
            len(failed_targets),
            failure_file
        )

    return updated_catalog


# ---------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    result = run_pipeline()
    print(result)
