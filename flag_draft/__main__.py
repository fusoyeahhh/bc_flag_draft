import sys
import copy
import argparse
import pandas
pandas.set_option("display.max_rows", 1000)
pandas.set_option("display.max_columns", 20)
pandas.set_option("display.max_colwidth", 200)
from . import options

# Available modes:
"""
1. normal - Play through the normal story.
2. ancientcave - Play through a long randomized dungeon.
3. speedcave - Play through a medium-sized randomized dungeon.
4. racecave - Play through a short randomized dungeon.
5. katn - Play the normal story up to Kefka at Narshe. Intended for racing.
6. dragonhunt - Kill all 8 dragons in the World of Ruin. Intended for racing.
"""

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
    print("Draft complete, flag string follows:")
    flags = draft_codes.loc[draft_codes["is_flag"]]["name"].sort_values()
    subopts = draft_codes.loc[draft_codes["is_suboption"]]["name"].sort_values()
    codes = ~(draft_codes["is_flag"] | draft_codes["is_suboption"])
    print("Standard flags:")
    print("".join(flags))
    print("Standard codes:")
    print("".join(draft_codes.loc[codes]["name"]))
    print("Codes with options:")
    print(" ".join(subopts))

argp = argparse.ArgumentParser()
argp.add_argument("-S", "--show-flags", action="store_true",
                  help="Show available flags for draft.")
argp.add_argument("-r", "--randomize-flags", type=int,
                  help="Provided with numerical argument, give that many random flags.")
argp.add_argument("-a", "--always-on", action="append",
                  help="Code will not be presented as an option, "
                       " and always present in final result. "
                       "Prefix with '!' to ban code.")
argp.add_argument("-O", "--allow-suboptions", action="store_true",
                  help="Pool codes into the pool which have options, "
                       "one for each suboption.")
argp.add_argument("-u", "--allow-undo", action="store_true",
                  help="Allow selected choices to go back into pool. "
                       "A subsequent appearance and selection will remove flag from draft.")
argp.add_argument("-B", "--ban-category", action="append",
                  help="Code category will not be presented as an option.")
argp.add_argument("-o", "--only-codes", action="store_true",
                  help="Only randomize over codes, not flags")
argp.add_argument("-c", "--add-challenges", action="store_true",
                  help="Add self-imposed challenges to pool.")
argp.add_argument("-s", "--draft-size", type=int, default=3,
                  help="Provided with numerical argument, do this many choices per round.")
argp.add_argument("-R", "--draft-rerolls", type=int, default=0,
                  help="Allow this many rerolls. Default is zero.")
argp.add_argument("-d", "--draft-length", type=int, default=5,
                  help="Provided with numerical argument, do this many draft rounds.")
argp.add_argument("--standard-draft", action="store_true",
                  help="Remove codes which are unsafe, not gameplay related "
                       "or standard mode inappropriate. "
                       "Implies --only-codes and --allow-suboptions.")
args = argp.parse_args()

if args.standard_draft:
    args.only_codes = True
    args.allow_suboptions = True
    args.ban_categories = ["gamebreaking"]
    # TODO: check what the standard should be
    args.always_on = ["!bingoboingo", "!sketch", "!playsitself", "!makeover",
                      "!removeflashing", "!sprint",
                      "!johnnyachaotic", "!johnnydmad"]

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

if args.allow_suboptions:
    codes = split_suboptions(codes)
else:
    # Drop multiplier codes
    codes = codes.loc[~codes["name"].isin(SUBOPTION_CODES)]
    codes["is_suboption"] = False

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

if args.show_flags:
    print(codes.sort_values(by="category").set_index(["name", "category"])[["long_description"]])
    sys.exit()

print(f"Pool size (does not count overlapping suboptions: {len(codes)}")
if len(codes) < args.draft_length + args.draft_size:
    print("WARNING: there may not be enough codes to complete draft")

if args.randomize_flags:
    draft_codes = codes.sample(min(args.randomize_flags, len(codes)))[["name", "is_flag"]]
    show_result(draft_codes)
    sys.exit()

#
# Main draft logic
#

rerolls = args.draft_rerolls or 0

i = 0
start_flags = len(draft_codes)
while len(draft_codes) < args.draft_length + start_flags:
    if args.allow_undo:
        pool = codes.index
    else:
        pool = codes.index.difference(draft_codes)

    choices = codes.loc[pool].sample(args.draft_size)[:]
    choices["selected"] = choices.index.isin(draft_codes)

    print(f"\n[Round {i+1}]\ntotal choices so far: {len(draft_codes)}\nChoices:")
    j = 1
    for idx, choice in choices.iterrows():
        if choice["selected"]:
            print(f"({j}) [UNDO] {choice['name']} <{choice['category']}>: {choice['long_description']}")
        else:
            print(f"({j}) {choice['name']} <{choice['category']}>: {choice['long_description']}")
        j += 1
    if rerolls > 0:
        print(f"({j}) reroll")

    while True:
        try:
            choice = int(input("choice> "))
        except ValueError:
            choice = None
        if choice == 0:
            show_result(codes.loc[draft_codes])
            continue

        allowed_choices = list(range(1, args.draft_size + int(rerolls > 0) + 1))
        if rerolls > 0 and choice == allowed_choices[-1]:
            rerolls -= 1
            break
        elif choice not in allowed_choices:
            print(f"Invalid choice, just 1 - {allowed_choices[-1]} please.")
            continue

        choice = choices.index[choice - 1]
        draft_codes = maybe_replace_option(choice, draft_codes, codes)
        if choices.loc[choice]["selected"]:
            draft_codes.remove(choice)
        else:
            draft_codes.append(choice)
        i += 1
        break

draft_codes = codes.loc[draft_codes]
show_result(draft_codes)