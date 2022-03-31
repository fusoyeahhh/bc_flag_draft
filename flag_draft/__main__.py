import sys
import argparse
import pandas
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

def show_result(draft_codes):
    print("Draft complete, flag string follows:")
    print("".join(draft_codes.loc[draft_codes["is_flag"]]["name"].sort_values()))
    print("".join(draft_codes.loc[~draft_codes["is_flag"]]["name"]))

argp = argparse.ArgumentParser()
argp.add_argument("-S", "--show-flags", action="store_true",
                  help="Show available flags for draft.")
argp.add_argument("-a", "--always-on", action="append",
                  help="Code will not be presented as an option, "
                       " and always present in final result. "
                       "Prefix with '!' to ban code.")
# TODO: merge with above and use "-" as a removal
argp.add_argument("-B", "--ban-category", action="append",
                  help="Code category will not be presented as an option.")
argp.add_argument("-o", "--only-codes", action="store_true",
                  help="Only randomize over codes, not flags")
argp.add_argument("-r", "--randomize-flags", type=int,
                  help="Provided with numerical argument, give that many random flags.")
argp.add_argument("-s", "--draft-size", type=int, default=3,
                  help="Provided with numerical argument, do this many choices per round.")
argp.add_argument("-R", "--draft-rerolls", type=int, default=0,
                  help="Allow this many rerolls. Default is zero.")
argp.add_argument("-d", "--draft-length", type=int, default=5,
                  help="Provided with numerical argument, do this many draft rounds.")
args = argp.parse_args()

codes = pandas.DataFrame(options.NORMAL_CODES)
alpha_codes = pandas.DataFrame(options.ALL_FLAGS)
alpha_codes["is_flag"] = True
alpha_codes["long_description"] = alpha_codes["description"]
codes = pandas.concat((codes, pandas.DataFrame(alpha_codes)))
codes["is_flag"] = codes["is_flag"].fillna(False)
codes = codes.reset_index()

draft_codes = []
always_on = {code for code in args.always_on if not code.startswith("!")}
if always_on:
    turn_on = codes["name"].isin(always_on)
    draft_codes.extend(codes.loc[turn_on].index)
    codes = codes.loc[codes.index.difference(turn_on)]

ban_code = {code[1:] for code in args.always_on if code.startswith("!")}
if ban_code:
    turn_off = codes["name"].isin(ban_code)
    codes = codes.loc[codes.index.difference(turn_off)]
if args.ban_category:
    codes = codes.loc[~codes["category"].isin(args.ban_category)]
if args.only_codes:
    codes = codes.loc[~codes["is_flag"]]

if args.show_flags:
    print(codes)
    sys.exit()

if args.randomize_flags:
    draft_codes = codes.sample(min(args.randomize_flags, len(codes)))[["name", "is_flag"]]
    show_result(draft_codes)
    sys.exit()

#
# Main draft logic
#

rerolls = args.draft_rerolls or 0

i = 0
while len(draft_codes) < args.draft_length + len(args.always_on or []):
    pool = codes.index.difference(draft_codes)
    choices = codes.loc[pool].sample(args.draft_size)

    print(f"[Round {i+1}] Choices:")
    j = 1
    for _, choice in choices.iterrows():
        print(f"({j}) {choice['name']}: {choice['long_description']}")
        j += 1
    if rerolls > 0:
        print(f"({j}) reroll")

    while True:
        try:
            choice = int(input("choice> "))
        except ValueError:
            choice = None
        if rerolls > 0 and choice == 4:
            break
        elif choice not in (1, 2, 3):
            print("Invalid choice, just 1, 2, or 3 please.")
            continue

        choice = choices.index[choice - 1]
        draft_codes.append(choice)
        i += 1
        break

draft_codes = codes.loc[draft_codes]
show_result(draft_codes)