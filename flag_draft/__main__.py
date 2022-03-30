import sys
import argparse
import random
import pandas

codes = pandas.read_excel("Codes_v5.2.xls")
alpha_codes = [{"Code": chr(c), "Effect": None, "IsAlpha": True}
                    for c in range(ord("a"), ord("z"))]
codes = pandas.concat((codes, pandas.DataFrame(alpha_codes)))
codes["IsAlpha"] = codes["IsAlpha"].fillna(False)

def show_result(draft_codes):
    print("Draft complete, flag string follows:")
    print("".join(draft_codes.loc[draft_codes["IsAlpha"]]["Code"]))
    print("".join(draft_codes.loc[~draft_codes["IsAlpha"]]["Code"]))

argp = argparse.ArgumentParser()
argp.add_argument("-s", "--show-flags", action="store_true",
                  help="Show available flags for draft.")
argp.add_argument("-r", "--randomize-flags", type=int,
                  help="Provided with numerical argument, give that many random flags.")
argp.add_argument("-d", "--draft-length", type=int, default=5,
                  help="Provided with numerical argument, do this many draft rounds.")
args = argp.parse_args()


if args.show_flags:
    print(codes)

if args.randomize_flags:
    draft_codes = codes.sample(min(args.randomize_flags, len(codes)))[["Code", "IsAlpha"]]
    show_result(draft_codes)
    sys.exit()

#
# Main draft logic
#

draft_codes = []
for i in range(args.draft_length):
    choices = codes.sample(3)
    print(f"[Round {i+1}] Choices:")
    j = 1
    for _, choice in choices.iterrows():
        print(f"({j}) {choice['Code']}: {choice['Effect']}")
        j += 1

    while True:
        try:
            choice = int(input("choice> "))
        except ValueError:
            choice = None
        if choice not in (1, 2, 3):
            print("Invalid choice, just 1, 2, or 3 please.")
            continue

        choice = choices.index[choice - 1]
        draft_codes.append(choice)
        print(draft_codes)
        break

draft_codes = codes.loc[draft_codes]
show_result(draft_codes)
