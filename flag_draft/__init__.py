import copy
import argparse
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
# TODO: move all this to init
# TODO: add weights: noeffect, easy, normal, hard
# TODO: note replacements
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

def maybe_replace_option(index, drafted_index, codes):
    opt = codes.loc[index]
    if not opt["is_suboption"]:
        return drafted_index

    _codes = codes.loc[drafted_index]
    opt = _codes.loc[opt["suboption_of"] == _codes["suboption_of"]]
    return list(set(drafted_index) - set(opt.index))

def show_result(draft_codes):
    flags = draft_codes.loc[draft_codes["is_flag"]]["name"].sort_values()
    subopts = draft_codes.loc[draft_codes["is_suboption"]]["name"].sort_values()
    codes = ~(draft_codes["is_flag"] | draft_codes["is_suboption"])
    print("Standard flags:")
    print("".join(flags))
    print("Standard codes:")
    print("".join(draft_codes.loc[codes]["name"]))
    print("Codes with options:")
    print(" ".join(subopts))

def construct_pool(args):
    codes = pandas.DataFrame(options.NORMAL_CODES)
    alpha_codes = pandas.DataFrame(options.ALL_FLAGS)
    alpha_codes["is_flag"] = True
    alpha_codes["long_description"] = alpha_codes["description"]
    alpha_codes["category"] = "flags"
    codes = pandas.concat((codes, pandas.DataFrame(alpha_codes)))

    if args.add_challenges:
        SUBOPTION_CODES.add("challenge")
        # will probably need weights for this
        new_code = {
            "name": "challenge",
            "category": "challenge",
            "long_description": "Self imposed challenge",
            "choices":  CHALLENGES
        }
        codes = codes.append(new_code, ignore_index=True)

    codes["is_flag"] = codes["is_flag"].fillna(False)
    codes = codes.reset_index(drop=True)

    codes["is_suboption"] = False
    if args.allow_suboptions:
        codes = split_suboptions(codes)
    else:
        # Drop multiplier codes
        codes = codes.loc[~codes["name"].isin(SUBOPTION_CODES)]

    draft_codes = []
    always_on = {code for code in args.always_on if not code.startswith("!")}
    if always_on:
        turn_on = codes["name"].isin(always_on)
        draft_codes.extend(codes.loc[turn_on].index)
        codes = codes.loc[codes.index.difference(turn_on)]
        print(f"Adding {always_on} into pool automatically.")

    ban_code = {code[1:] for code in (args.always_on or []) if code.startswith("!")}
    if ban_code:
        codes = codes.loc[~codes["name"].isin(ban_code)]
        print(f"Banning {ban_code} from pool.")
    if args.ban_category:
        codes = codes.loc[~codes["category"].isin(args.ban_category)]
        print(f"Banning category {args.ban_category} from pool.")
    if args.only_codes:
        codes = codes.loc[~codes["is_flag"]]
        print(f"Dropping standard flags from pool.")

    return draft_codes, codes

def pull_from_pool(codes, draft_codes, args):
    if args.allow_undo:
        pool = codes.index
    else:
        pool = codes.index.difference(draft_codes)

    choices = codes.loc[pool].sample(args.draft_size)[:]
    choices["selected"] = choices.index.isin(draft_codes)
    return choices

def display_choices(choices, draft_codes, round, rerolls=0):
    print(f"\n[Round {round + 1}]\ntotal choices so far: {len(draft_codes)}\nChoices:")

    j = 1
    for idx, choice in choices.iterrows():
        if choice["selected"]:
            print(f"({j}) [UNDO] {choice['name']} <{choice['category']}>: {choice['long_description']}")
        else:
            print(f"({j}) {choice['name']} <{choice['category']}>: {choice['long_description']}")
        j += 1
    if rerolls > 0:
        print(f"({j}) reroll")