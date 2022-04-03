import sys
import argparse
import pandas
pandas.set_option("display.max_rows", 1000)
pandas.set_option("display.max_columns", 20)
pandas.set_option("display.max_colwidth", 200)

from .drafter import BCFlagDrafter
from . import args as args_
from . import *

__version__ = "0.0.2-beta"

def display_choices(choices, rerolls):
    for i, (idx, choice) in enumerate(choices.iterrows()):
        i += 1
        cstatus = ""
        cstatus += "UNDO" if choice["selected"] else ""
        # TODO: note replacements
        cstatus = f" [{cstatus}]" if cstatus else ""
        print(f"({i}){cstatus} {choice['name']} <{choice['category']}>: {choice['long_description']}")
    # FIXME: append as dummy choice
    if rerolls > 0:
        print(f"({i + 1}) reroll [{rerolls} remaining]")

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

drafter = BCFlagDrafter(only_codes=args.only_codes,
                        allow_suboptions=args.allow_suboptions,
                        add_challenges=args.add_challenges,
                        rerolls=args.draft_rerolls,
                        always_on=args.always_on,
                        ban_category=args.ban_categories)

if args.show_flags:
    drafter.show_flags()
    sys.exit()

print(f"Pool size (does not count overlapping suboptions): {len(drafter.codes)}")

if args.randomize_flags:
    drafter.randomize_flags(args.randomize_flags)
    print("Draft complete, flag string follows:")
    drafter.show_result()
    sys.exit()

#
# Main draft logic
#

for choices in drafter.draft(args.draft_length, args.draft_size):
    print(f"\n[Round {drafter.round + 1}]\ntotal choices so far: "
          f"{len(drafter.draft_codes)}\nChoices:")
    display_choices(choices, drafter.rerolls)

    while True:
        try:
            choice = int(input("choice> "))
        except ValueError:
            choice = None

        if choice == 0:
            drafter.show_result()
            continue
        elif choice == -1:
            drafter.show_flags()
            continue

        allowed_choices = list(range(1, args.draft_size + int(drafter.rerolls > 0) + 1))
        if choice not in allowed_choices:
            print(f"Invalid choice, just 1 - {allowed_choices[-1]} please.")
            continue

        is_reroll = choice == allowed_choices[-1] and drafter.rerolls > 0
        drafter.draft_code(idx=choices.index[choice - 1],
                           is_reroll=is_reroll)
        break

print("Draft complete, flag string follows:")
drafter.show_result()