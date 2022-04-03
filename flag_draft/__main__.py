import sys
import argparse
import pandas
pandas.set_option("display.max_rows", 1000)
pandas.set_option("display.max_columns", 20)
pandas.set_option("display.max_colwidth", 200)
from . import options
from . import *

# Available modes:
"""
1. normal - Play through the normal story.
2. ancientcave - Play through a long randomized dungeon.
3. speedcave - Play through a medium-sized randomized dungeon.
4. racecave - Play through a short randomized dungeon.
5. katn - Play the normal story up to Kefka at Narshe. Intended for racing.
6. dragonhunt - Kill all 8 dragons in the World of Ruin. Intended for racing.
"""

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
    args.always_on = args.always_on or []
    args.always_on += ["!bingoboingo", "!sketch", "!playsitself", "!makeover",
                       "!removeflashing", "!sprint",
                       "!johnnyachaotic", "!johnnydmad"]

draft_codes, codes = construct_pool(args)

if args.show_flags:
    print(codes.sort_values(by="category").set_index(["name", "category"])[["long_description"]])
    sys.exit()

print(f"Pool size (does not count overlapping suboptions: {len(codes)}")
if len(codes) < args.draft_length + args.draft_size:
    print("WARNING: there may not be enough codes to complete draft")

if args.randomize_flags:
    draft_codes = codes.sample(min(args.randomize_flags, len(codes)))
    print("Draft complete, flag string follows:")
    show_result(draft_codes)
    sys.exit()

#
# Main draft logic
#

rerolls = args.draft_rerolls or 0

i = 0
start_flags = len(draft_codes)
while len(draft_codes) < args.draft_length + start_flags:
    choices = pull_from_pool(codes, draft_codes, args)

    display_choices(choices, draft_codes, i, rerolls)

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
        i += 1
        break

draft_codes = codes.loc[draft_codes]
print("Draft complete, flag string follows:")
show_result(draft_codes)