import copy
import pandas
pandas.set_option("display.max_rows", 1000)
pandas.set_option("display.max_columns", 20)
pandas.set_option("display.max_colwidth", 200)
from . import options

# TODO: drop flags which potentially conflict
FLAG_CONFLICTS = {
    "strangejourney": "worringtriad"
}

# TODO: add termcolor (if possible)
# TODO: add weights: noeffect, easy, normal, hard
CHALLENGES = ("noultima", "noflare", "nomerton", "nolife3", "nolife2",
              "nodesperation", "nosummons", "noelemental", "nostatus",
              "noblitz", "notools", "noswdtech",
              "nothrow", "nomagic", "noitem")

SUBOPTION_CODES = {"expboost", "gpboost", "mpboost",
                   "randomboost", "swdtechspeed"}
GOOD_MULT, BAD_MULT = (1, 2, 3, 5, 10), (0.9, 0.75, 0.5, 0.25)
ALL_MULT = GOOD_MULT + BAD_MULT
def add_suboptions(codes):
    for code in SUBOPTION_CODES - {"swdtechspeed", "challenge", "randomboost"}:
        for idx in codes.loc[codes["name"] == code].index:
            codes.at[idx, "choices"] = ALL_MULT
    for code in {"randomboost"}:
        for idx in codes.loc[codes["name"] == code].index:
            codes.at[idx, "choices"] = (0, 1, 2)

def split_suboptions(codes):
    add_suboptions(codes)
    tmp = []
    for _, row in codes.iterrows():
        if pandas.notna(row["choices"]):
            print(f"Splitting {row['name']} into suboptions: {row['choices']}")
            for opt in row["choices"]:
                _row = copy.copy(row)
                _row["name"] += "=" + str(opt)
                _row["suboption_of"] = row["name"]
                _row["is_suboption"] = True
                tmp.append(_row)
        else:
            tmp.append(row)
    codes = pandas.DataFrame(tmp).reset_index(drop=True)
    codes["is_suboption"] = codes["is_suboption"].fillna(False)
    return codes

def construct_pool():
    codes = pandas.DataFrame(options.NORMAL_CODES)
    alpha_codes = pandas.DataFrame(options.ALL_FLAGS)
    alpha_codes["is_flag"] = True
    alpha_codes["long_description"] = alpha_codes["description"]
    alpha_codes["category"] = "flags"
    return pandas.concat((codes, pandas.DataFrame(alpha_codes)))