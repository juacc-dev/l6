# Vibe-coded so there's that

"""
Convert Wyko/Veeco binary OPD files to CSV.

The CSV contains:
    - Pixel_size in the header
    - other useful calibration information
    - a 2-D matrix of Z values

No external Python packages are required.

Usage:

    python opd2csv.py sample.opd

    python opd2csv.py sample.opd -o sample.csv

    python opd2csv.py sample.opd --precision 12
"""

from __future__ import annotations

import argparse
import csv
import math
import struct
from dataclasses import dataclass
from pathlib import Path


# ----------------------------------------------------------------------
# OPD constants
# ----------------------------------------------------------------------

BLOCK_SIZE = 24
BLOCK_NAME_SIZE = 16

MAGIC = b"\x01\x00Directory"

OPD_DIRECTORY = 1
OPD_ARRAY = 3
OPD_SHORT = 6
OPD_FLOAT = 7
OPD_LONG = 12

OPD_ARRAY_BYTE = 1
OPD_ARRAY_INT16 = 2
OPD_ARRAY_FLOAT = 4

OPD_BAD_FLOAT = 1e38
OPD_BAD_INT16 = 32766


# Image/data block names encountered in Wyko OPD files.
DATA_NAMES = {
    "OPD",
    "SAMPLE_DATA",
    "RAW_DATA",
    "RAW DATA",
    "Image",
    "Intensity",
    "SecArr_0",
    "Raw",
}

INTENSITY_NAMES = {
    "Image",
    "Intensity",
    "SecArr_0",
}


# ----------------------------------------------------------------------
# OPD block
# ----------------------------------------------------------------------

@dataclass
class Block:
    name: str
    type: int
    size: int
    flags: int
    data_offset: int


# ----------------------------------------------------------------------
# Binary readers
# ----------------------------------------------------------------------

def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def i16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<h", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def f32(data: bytes, offset: int) -> float:
    return struct.unpack_from("<f", data, offset)[0]


# ----------------------------------------------------------------------
# Read an OPD block descriptor
# ----------------------------------------------------------------------

def read_block_header(
    data: bytes,
    offset: int,
) -> tuple[Block, int]:

    if offset + BLOCK_SIZE > len(data):
        raise ValueError("Truncated OPD block header")

    raw_name = data[
        offset:offset + BLOCK_NAME_SIZE
    ]

    name = (
        raw_name
        .rstrip(b"\x00")
        .decode("latin-1", errors="replace")
        .strip()
    )

    block_type = u16(data, offset + 16)
    size = u32(data, offset + 18)
    flags = u16(data, offset + 22)

    block = Block(
        name=name,
        type=block_type,
        size=size,
        flags=flags,
        data_offset=0,
    )

    return block, offset + BLOCK_SIZE


# ----------------------------------------------------------------------
# Parse OPD directory
# ----------------------------------------------------------------------

def parse_opd(
    path: Path,
) -> tuple[list[Block], bytes]:

    data = path.read_bytes()

    if len(data) < 2 + BLOCK_SIZE:
        raise ValueError(
            "File is too short to be an OPD file"
        )

    if not data.startswith(MAGIC):
        raise ValueError(
            "Not a binary Wyko OPD file: "
            "missing OPD Directory signature"
        )

    directory, _ = read_block_header(data, 2)

    if directory.name != "Directory":
        raise ValueError(
            f"Unexpected directory name: "
            f"{directory.name!r}"
        )

    if directory.type != OPD_DIRECTORY:
        raise ValueError(
            f"Unexpected directory type: "
            f"{directory.type}"
        )

    if directory.flags != 0xFFFF:
        raise ValueError(
            f"Unexpected directory flags: "
            f"0x{directory.flags:04x}"
        )

    if directory.size % BLOCK_SIZE:
        raise ValueError(
            f"Invalid directory size: "
            f"{directory.size}"
        )

    nblocks = directory.size // BLOCK_SIZE

    directory_end = 2 + directory.size

    if directory_end > len(data):
        raise ValueError("Truncated OPD directory")

    blocks = []

    descriptor_offset = 2 + BLOCK_SIZE
    data_offset = directory_end

    for _ in range(nblocks - 1):

        block, descriptor_offset = read_block_header(
            data,
            descriptor_offset,
        )

        block.data_offset = data_offset

        end = data_offset + block.size

        if end > len(data):
            raise ValueError(
                f"Block {block.name!r} extends "
                "beyond the end of the file"
            )

        data_offset = end

        if block.size:
            blocks.append(block)

    # Compatibility corrections used by Gwyddion.
    for block in blocks:

        if (
            block.name.startswith("AdjustVSI_")
            and block.type == OPD_FLOAT
            and block.size == 2
        ):
            block.type = OPD_SHORT

        elif (
            block.name == "ImageModificat~0"
            and block.type == OPD_FLOAT
            and block.size == 40
        ):
            block.size = 4

        elif (
            block.type == OPD_SHORT
            and block.size == 4
        ):
            block.type = OPD_LONG

    return blocks, data


# ----------------------------------------------------------------------
# Find a block
# ----------------------------------------------------------------------

def find_block(
    blocks: list[Block],
    name: str,
) -> Block | None:

    for block in blocks:
        if block.name == name:
            return block

    return None


# ----------------------------------------------------------------------
# Read scalar values
# ----------------------------------------------------------------------

def get_float(
    data: bytes,
    blocks: list[Block],
    name: str,
) -> float:

    block = find_block(blocks, name)

    if block is None:
        raise ValueError(
            f"Required OPD field {name!r} is missing"
        )

    if block.type != OPD_FLOAT:
        raise ValueError(
            f"OPD field {name!r} has type "
            f"{block.type}, expected float"
        )

    return f32(data, block.data_offset)


def get_int16(
    data: bytes,
    blocks: list[Block],
    name: str,
    default: int = 1,
) -> int:

    block = find_block(blocks, name)

    if block is None:
        return default

    if block.type != OPD_SHORT:
        raise ValueError(
            f"OPD field {name!r} has type "
            f"{block.type}, expected int16"
        )

    return i16(data, block.data_offset)


# ----------------------------------------------------------------------
# Pixel_size
# ----------------------------------------------------------------------

def get_pixel_size(
    data: bytes,
    blocks: list[Block],
) -> float:

    block = find_block(blocks, "Pixel_size")

    if block is None:
        raise ValueError(
            "OPD file does not contain a "
            "'Pixel_size' field"
        )

    if block.type == OPD_FLOAT:
        return f32(data, block.data_offset)

    raise ValueError(
        f"'Pixel_size' has unsupported OPD type "
        f"{block.type}; expected float"
    )


# ----------------------------------------------------------------------
# Read image array
# ----------------------------------------------------------------------

def get_array_params(
    data: bytes,
    block: Block,
) -> tuple[int, int, int, int]:

    p = block.data_offset

    if block.size < 6:
        raise ValueError(
            f"Array block {block.name!r} "
            "is too small"
        )

    xres = u16(data, p)
    yres = u16(data, p + 2)
    array_type = u16(data, p + 4)

    payload = p + 6

    bytes_per_value = {
        OPD_ARRAY_BYTE: 1,
        OPD_ARRAY_INT16: 2,
        OPD_ARRAY_FLOAT: 4,
    }.get(array_type)

    if bytes_per_value is None:
        raise ValueError(
            f"Unsupported OPD array type "
            f"{array_type} in {block.name!r}"
        )

    expected_size = (
        6
        + xres * yres * bytes_per_value
    )

    if block.size < expected_size:
        raise ValueError(
            f"Array block {block.name!r} is truncated"
        )

    return (
        xres,
        yres,
        array_type,
        payload,
    )


def read_data_block(
    data: bytes,
    block: Block,
    wavelength_m: float,
) -> tuple[
    int,
    int,
    list[list[float]],
    list[list[bool]],
]:

    xres, yres, array_type, p = (
        get_array_params(data, block)
    )

    values = [
        [math.nan for _ in range(xres)]
        for _ in range(yres)
    ]

    valid = [
        [False for _ in range(xres)]
        for _ in range(yres)
    ]

    # OPD stores the image column-by-column.
    #
    # The Y direction is reversed relative to the
    # orientation used by Gwyddion.

    for x in range(xres):

        for j in range(yres, 0, -1):

            y = j - 1

            if array_type == OPD_ARRAY_FLOAT:

                value = f32(data, p)
                p += 4

                if value < OPD_BAD_FLOAT:

                    values[y][x] = (
                        wavelength_m * value
                    )

                    valid[y][x] = True

            elif array_type == OPD_ARRAY_INT16:

                value = i16(data, p)
                p += 2

                if value < OPD_BAD_INT16:

                    values[y][x] = (
                        wavelength_m * value
                    )

                    valid[y][x] = True

            elif array_type == OPD_ARRAY_BYTE:

                value = data[p]
                p += 1

                values[y][x] = (
                    wavelength_m * value
                )

                valid[y][x] = True

    return (
        xres,
        yres,
        values,
        valid,
    )


# ----------------------------------------------------------------------
# Write CSV
# ----------------------------------------------------------------------

def write_csv(
    path: Path,
    values: list[list[float]],
    valid: list[list[bool]],
    *,
    pixel_size: float,
    wavelength_nm: float,
    mult: int,
    block_name: str,
    bad_value: str = "nan",
    precision: int = 12,
) -> None:

    number_format = f".{precision}g"

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        # ----------------------------------------------------------
        # Header
        # ----------------------------------------------------------

        writer.writerow([
            f"# Pixel_size: {pixel_size:.15g}"
        ])

        writer.writerow([
            f"# Wavelength: {wavelength_nm:.15g} nm"
        ])

        writer.writerow([
            f"# Mult: {mult}"
        ])

        writer.writerow([
            f"# Data block: {block_name}"
        ])

        writer.writerow([
            "# Data below are Z values and rows are Y and columns are X"
        ])

        # ----------------------------------------------------------
        # Z matrix
        # ----------------------------------------------------------

        for row, good_row in zip(
            values,
            valid,
        ):

            output_row = []

            for value, good in zip(
                row,
                good_row,
            ):

                if not good:
                    output_row.append(
                        bad_value
                    )
                else:
                    output_row.append(
                        format(
                            value,
                            number_format,
                        )
                    )

            writer.writerow(output_row)


# ----------------------------------------------------------------------
# Filename handling
# ----------------------------------------------------------------------

def sanitize_filename(
    name: str,
) -> str:

    result = []

    for char in name:

        if char.isalnum() or char in "._-":
            result.append(char)
        else:
            result.append("_")

    return (
        "".join(result).strip("_")
        or "data"
    )


# ----------------------------------------------------------------------
# Conversion
# ----------------------------------------------------------------------

def convert(
    input_path: Path,
    output_path: Path | None,
    all_blocks: bool,
    bad_value: str,
    precision: int,
) -> None:

    blocks, data = parse_opd(input_path)

    # --------------------------------------------------------------
    # Z calibration
    # --------------------------------------------------------------

    wavelength_nm = get_float(
        data,
        blocks,
        "Wavelength",
    )

    mult = get_int16(
        data,
        blocks,
        "Mult",
        default=1,
    )

    if mult == 0:
        raise ValueError(
            "OPD Mult field is zero"
        )

    wavelength_m = (
        wavelength_nm
        * 1e-9
        / mult
    )

    # --------------------------------------------------------------
    # Lateral calibration
    # --------------------------------------------------------------

    pixel_size = get_pixel_size(
        data,
        blocks,
    )

    # --------------------------------------------------------------
    # Find image arrays
    # --------------------------------------------------------------

    image_blocks = [
        block
        for block in blocks
        if (
            block.name in DATA_NAMES
            and block.type == OPD_ARRAY
        )
    ]

    if not image_blocks:
        raise ValueError(
            "No image data block found "
            "in OPD file"
        )

    if not all_blocks:
        image_blocks = image_blocks[:1]

    # --------------------------------------------------------------
    # Process image(s)
    # --------------------------------------------------------------

    for index, block in enumerate(
        image_blocks
    ):

        (
            xres,
            yres,
            values,
            valid,
        ) = read_data_block(
            data,
            block,
            (
                1.0
                if block.name in INTENSITY_NAMES
                else wavelength_m
            ),
        )

        # ----------------------------------------------------------
        # Output filename
        # ----------------------------------------------------------

        if (
            output_path is not None
            and len(image_blocks) == 1
        ):
            out = output_path

        else:

            suffix = (
                f"_{index + 1}_"
                f"{sanitize_filename(block.name)}"
                ".csv"
            )

            out = input_path.with_name(
                input_path.stem + suffix
            )

        # ----------------------------------------------------------
        # Write CSV
        # ----------------------------------------------------------

        write_csv(
            out,
            values,
            valid,
            pixel_size=pixel_size,
            wavelength_nm=wavelength_nm,
            mult=mult,
            block_name=block.name,
            bad_value=bad_value,
            precision=precision,
        )

        print(
            f"{input_path} -> {out}"
        )

        print(
            f"  data block : {block.name}"
        )

        print(
            f"  resolution : "
            f"{xres} x {yres} pixels"
        )

        print(
            f"  Pixel_size : "
            f"{pixel_size:.15g}"
        )


# ----------------------------------------------------------------------
# Command-line interface
# ----------------------------------------------------------------------

def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Convert Wyko/Veeco binary OPD "
            "files to CSV."
        )
    )

    parser.add_argument(
        "input",
        type=Path,
        help="input .opd file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output CSV filename",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help=(
            "export every image-like "
            "data block"
        ),
    )

    parser.add_argument(
        "--bad-value",
        default="nan",
        help=(
            "CSV representation for "
            "invalid pixels (default: nan)"
        ),
    )

    parser.add_argument(
        "--precision",
        type=int,
        default=12,
        help=(
            "significant digits in output "
            "(default: 12)"
        ),
    )

    args = parser.parse_args()

    convert(
        args.input,
        args.output,
        args.all,
        args.bad_value,
        args.precision,
    )


if __name__ == "__main__":
    main()
