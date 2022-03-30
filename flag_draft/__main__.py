import sys
import argparse
import random
import pandas

# Available modes:
"""
1. normal - Play through the normal story.
2. ancientcave - Play through a long randomized dungeon.
3. speedcave - Play through a medium-sized randomized dungeon.
4. racecave - Play through a short randomized dungeon.
5. katn - Play the normal story up to Kefka at Narshe. Intended for racing.
6. dragonhunt - Kill all 8 dragons in the World of Ruin. Intended for racing.
"""

# alpha explanations
_ALPHA = """b Make the game more balanced by removing known exploits.
c Randomize palettes and names of various things.
d Randomize final dungeon.
e Randomize esper spells and levelup bonuses.
f Randomize enemy formations.
g Randomize dances
h Your party in the Final Kefka fight will be random.
i Randomize the stats of equippable items.
j Randomize the phantom forest.
k Randomize the clock in Zozo
l Randomize blitz inputs.
m Randomize enemy stats.
n Randomize window background colors.
o Shuffle characters' in-battle commands
p Randomize the palettes of spells and weapon animations.
q Randomize what equipment each character can wear and character stats.
r Randomize character locations in the world of ruin.
s Swap character graphics around.
t Randomize treasure, including chests, colosseum, shops, and enemy drops.
u Umaro risk. (Random character will be berserk)
w Generate new commands for characters, replacing old commands.
y Shuffle magicite locations.
z Always have "Sprint Shoes" effect."""
_ALPHA = {s[0]: s[2:] for s in _ALPHA.split("\n")}

codes = pandas.read_excel("Codes_v5.2.xls")
alpha_codes = [{"Code": chr(c), "Effect": _ALPHA[chr(c)], "IsAlpha": True}
                    for c in range(ord("a"), ord("z")) if chr(c) in _ALPHA]
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
    sys.exit()

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
