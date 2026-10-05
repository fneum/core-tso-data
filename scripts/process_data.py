"""Process core TSO dataset."""

__author__ = "Fabian Neumann"
__copyright__ = "Copyright 2022, Fabian Neumann (TUB)"
__license__ = "MIT"


import pandas as pd
from math import isnan
import uuid
import re

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

import country_converter as coco

cc = coco.CountryConverter()


def geocoder(delay=2):
    locator = Nominatim(user_agent=str(uuid.uuid4()))
    return RateLimiter(locator.geocode, min_delay_seconds=delay)


geocode = geocoder()


def load_data(fn):
    return pd.read_excel(
        fn,
        header=[0, 1],
        na_values=["-", ";"],
        sheet_name=None,
    )


def clean_symmetrical(s):
    if isinstance(s, float) and isnan(s):
        return s
    if "asym" in s.lower():
        return False
    else:
        return True


def clean_taps(s):
    if isinstance(s, float) and isnan(s) or s == 0:
        taps = [s, s]
    else:
        clean_s = (
            s.replace("<", "").replace(">", "").replace("/", ";").strip().split(";")
        )
        taps = [int(i) for i in clean_s]
    return pd.Series(taps, index=["taps_lower", "taps_upper"])


def retrieve_lines(df, country=None):

    lines = pd.DataFrame()

    lines["name"] = df.xs("NE_name", level=1, axis=1).squeeze()
    lines["EIC_Code"] = df.xs("EIC_Code", level=1, axis=1).squeeze()
    lines["TSO"] = df.xs("TSO", level=1, axis=1).squeeze()
    lines["bus0"] = df[("Substation_1", "Full_name")]
    lines["bus1"] = df[("Substation_2", "Full_name")]
    lines["v_nom"] = df.xs("Voltage_level(kV)", level=1, axis=1).squeeze()  # kV
    lines["i_nom_fixed"] = df[("Maximum Current Imax (A)", "Fixed")] / 1e3  # kA
    for i in range(1, 7):
        lines[f"i_nom_{i}"] = (
            df[("Maximum Current Imax (A)", f"Period {i}")] / 1e3
        )  # kA
    lines["i_nom_dlr_min"] = df.xs("DLRmin(A)", level=1, axis=1).squeeze() / 1e3  # kA
    lines["i_nom_dlr_max"] = df.xs("DLRmax(A)", level=1, axis=1).squeeze() / 1e3  # kA
    lines["r"] = df.xs("Resistance_R(Ω)", level=1, axis=1).squeeze()  # Ohm
    lines["x"] = 1 / df.xs("Reactance_X(Ω)", level=1, axis=1).squeeze()  # Siemens
    lines["b"] = df.xs("Susceptance_B(μS)", level=1, axis=1).squeeze() / 1e6  # Siemens
    lines["length"] = df.xs("Length_(km)", level=1, axis=1).squeeze()
    lines["tag"] = df.xs("Comment", level=1, axis=1).squeeze()
    if country is not None:
        lines["country"] = country

    return lines


def retrieve_transformers(df, country=None):

    transformers = pd.DataFrame()

    transformers["name"] = df.xs("Full Name", level=1, axis=1).squeeze()
    transformers["EIC_Code"] = df.xs("EIC_Code", level=1, axis=1).squeeze()
    transformers["TSO"] = df.xs("TSO", level=1, axis=1).squeeze()
    transformers["i_nom"] = (
        df[("Maximum Current Imax (A) primary", "Fixed")] / 1e3
    )  # kA
    transformers["i_nom_min"] = (
        df[("Maximum Current Imax (A) primary", "Min")] / 1e3
    )  # kA
    transformers["i_nom_max"] = (
        df[("Maximum Current Imax (A) primary", "Max")] / 1e3
    )  # kA

    transformers["r"] = df.xs(
        "Resistance_R(Ω)", level=1, axis=1
    ).squeeze()  # Ohm (primary, neutral tap)
    transformers["x"] = (
        1 / df.xs("Reactance_X(Ω)", level=1, axis=1).squeeze()
    )  # Siemens (primary, neutral tap)
    transformers["b"] = (
        df.xs("Susceptance_B (µS)", level=1, axis=1).squeeze() / 1e6
    )  # Siemens (primary, neutral tap)
    transformers["g"] = (
        df.xs("Conductance_G (µS)", level=1, axis=1).squeeze() / 1e6
    )  # Siemens (primary, neutral tap)

    taps = df.xs("Taps used for RAO", level=1, axis=1).squeeze().apply(clean_taps)
    transformers = pd.concat([transformers, taps], axis=1)

    transformers["phase_shift"] = df.xs("Theta θ (°)", level=1, axis=1).squeeze()
    transformers["symmetrical"] = (
        df.xs("Symmetrical/Asymmetrical", level=1, axis=1)
        .squeeze()
        .apply(clean_symmetrical)
    )
    transformers["phase_regulation"] = df.xs(
        "Phase Regulation δu (%)", level=1, axis=1
    ).squeeze()
    transformers["angle_regulation"] = df.xs(
        "Angle Regulation δu (%)", level=1, axis=1
    ).squeeze()

    transformers["tag"] = df.xs("Comment", level=1, axis=1).squeeze()
    if country is not None:
        transformers["country"] = country

    return transformers


def locate(s):
    fail = pd.Series(dict(x=pd.NA, y=pd.NA))
    if isinstance(s, float) and isnan(s):
        return fail
    if isinstance(s, str):
        s = s.split(" ")
    if cc.convert(s[-1], src="iso2") != "not found":
        s[-1] = cc.convert(s[-1], to="name")
    loc = geocode(s, geometry="wkt")
    if loc is not None:
        print(f"Found:\t{loc}\nFor:\t{s}\n")
        return pd.Series(dict(x=loc.longitude, y=loc.latitude, address=loc.address))
    elif len(s) > 2:
        s.pop(-2)
        return locate(s)
    else:
        print(f"{s} not found\n")
        return fail


def buses_from_lines(lines, geocode=True):
    bus0 = lines.bus0.str.strip() + " " + lines.country
    bus1 = lines.bus1.str.strip() + " " + lines.country
    buses = pd.DataFrame(set(bus0).union(bus1), columns=["name"])
    buses.sort_values(by="name", inplace=True, ignore_index=True)
    buses["name"] = (
        buses.name.str.replace("/", " ")
        .str.replace("Y-", "")
        .str.replace(" - ", " ")
        .str.replace("(", "")
        .str.replace(")", "")
    )
    buses["name"] = buses.name.apply(
        lambda s: re.sub(r"([a-z])([A-Z])", r"\1 \2", s) if isinstance(s, str) else s
    )
    buses["name"] = buses.name.apply(
        lambda s: (
            s.replace("ue", "ü")
            .replace("ae", "ä")
            .replace("oe", "ö")
            .replace("Itzehö", "Itzehoe")
            .replace("Daürsberg", "Dauersberg")
            if isinstance(s, str) and s[-2:] in ["DE", "AT"]
            else s
        )
    )
    if geocode:
        buses = pd.concat([buses, buses.name.apply(locate)], axis=1)
    return buses


if __name__ == "__main__":
    if "snakemake" not in globals():
        from _helpers import mock_snakemake

        snakemake = mock_snakemake("process_data")

    config = snakemake.config

    lines = []
    transformers = []
    for region, country in config["regions"].items():
        xls = load_data(snakemake.input[region])
        for line_category in ["Lines", "Tielines"]:
            lines.append(retrieve_lines(xls[line_category], country))
        transformers.append(retrieve_transformers(xls["Transformers"], country))

    lines = pd.concat(lines, ignore_index=True)
    transformers = pd.concat(transformers, ignore_index=True)

    buses = buses_from_lines(lines, geocode=config["geocode"])

    lines.to_csv(snakemake.output.lines)
    transformers.to_csv(snakemake.output.transformers)
    buses.to_csv(snakemake.output.buses)
