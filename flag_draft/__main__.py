import sys
import argparse
import pandas
pandas.set_option("display.max_rows", 1000)
pandas.set_option("display.max_columns", 20)
pandas.set_option("display.max_colwidth", 200)
from . import args as args_
from . import *

__version__ = "0.0.2-beta"

# Ideas:
# Add gameplay mode options, see below
# Available modes:
"""
1. normal - Play through the normal story.
2. ancientcave - Play through a long randomized dungeon.
3. speedcave - Play through a medium-sized randomized dungeon.
4. racecave - Play through a short randomized dungeon.
5. katn - Play the normal story up to Kefka at Narshe. Intended for racing.
6. dragonhunt - Kill all 8 dragons in the World of Ruin. Intended for racing.
"""

argp = args_.construct_args(argparse.ArgumentParser())
args = argp.parse_args()

if args.standard_draft:
    args = args_.enable_standard_draft(args)

draft_codes, codes = construct_pool(args)

if args.show_flags:
    show_flags(codes)
    sys.exit()

print(f"Pool size (does not count overlapping suboptions: {len(codes)}")
if len(codes) < args.draft_length + args.draft_size:
    print("WARNING: there may not be enough codes to complete draft")

if args.randomize_flags:
    # TODO: use pull_from_pool
    draft_codes = codes.sample(min(args.randomize_flags, len(codes)))
    print("Draft complete, flag string follows:")
    show_result(draft_codes)
    sys.exit()

#
# Main draft logic
#

rerolls = args.draft_rerolls or 0

round = 0
start_flags = len(draft_codes)
while len(draft_codes) < args.draft_length + start_flags:
    choices = pull_from_pool(codes, draft_codes, args)

    display_choices(choices, draft_codes, round, rerolls)

    while True:
        try:
            choice = int(input("choice> "))
        except ValueError:
            choice = None

        if choice == 0:
            show_result(codes.loc[draft_codes])
            continue
        elif choice == -1:
            # TODO: make into function
            print(codes.sort_values(by="category").set_index(["name", "category"])[["long_description"]])
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
        round += 1
        break

draft_codes = codes.loc[draft_codes]
print("Draft complete, flag string follows:")
show_result(draft_codes)