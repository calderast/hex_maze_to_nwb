import argparse
from pathlib import Path
import yaml

from pynwb import NWBFile, NWBHDF5IO
from datetime import datetime
from dateutil import tz

from .convert_raw_ephys import add_raw_ephys
from .convert_spikes import add_spikes
from .convert_behavior import add_behavior
from .convert_photometry import add_photometry


def create_nwbs(
    metadata_file_path: Path,
    output_nwb_file_path: Path,
):
    with open(metadata_file_path, "r") as f:
        metadata = yaml.safe_load(f)

    # parse surgery metadata
    surgery = "..."  # TODO parse from structured metadata

    # TODO: read these from metadata
    nwbfile = NWBFile(
        session_description="Mock session",  # TODO: generate this from metadata
        session_start_time=datetime.now(tz.tzlocal()),  # TODO: update this 
        identifier="mock_session",  # TODO: update this
        session_id=metadata.get("session_id"),
        surgery=surgery,
        notes=metadata.get("notes"),
        experimenter=metadata.get("experimenter"),
        institution=metadata.get("institution"),
        lab=metadata.get("lab"),
        keywords=metadata.get("keywords"),
        experiment_description=metadata.get("experiment_description"),
        related_publications=metadata.get("related_publications"),
    )

    add_raw_ephys(nwbfile=nwbfile, metadata=metadata)
    add_spikes(nwbfile=nwbfile, metadata=metadata)
    photometry_start_in_arduino_time = add_behavior(nwbfile=nwbfile, metadata=metadata)
    add_photometry(nwbfile=nwbfile, metadata=metadata)

    print(f"Writing file, including iterative read from raw ephys data...")

    with NWBHDF5IO(output_nwb_file_path, mode="w") as io:
        io.write(nwbfile)

    print(f"NWB file created successfully at {output_nwb_file_path}")


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata_file_path", type=Path, help="Path to the metadata YAML file.")
    parser.add_argument("output_nwb_file_path", type=Path, help="Path to the output NWB file.")
    args = parser.parse_args()

    create_nwbs(args.metadata_file_path, args.output_nwb_file_path)