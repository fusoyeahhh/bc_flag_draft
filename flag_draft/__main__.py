import argparse
import random
import pandas

codes = pandas.read_excel("Codes_v5.2.xls")
alpha_codes = [{"Code": chr(c), "Effect": None, "IsAlpha": True}
                    for c in range(ord("a"), ord("z"))]
codes = pandas.concat((codes, pandas.DataFrame(alpha_codes)))
codes["IsAlpha"] = codes["IsAlpha"].fillna(False)

argp = argparse.ArgumentParser()
argp.add_argument("-s", "--show-flags", action="store_true",
                  help="Show available flags for draft.")
argp.add_argument("-r", "--randomize-flags", type=int,
                  help="Provided with numerical argument, give that many random flags.")
args = argp.parse_args()

if args.show_flags:
    print(codes)

draft_codes = ""
alpha_draft_codes = ""
if args.randomize_flags:
    draft_codes = codes.sample(min(args.randomize_flags, len(codes)))[["Code", "IsAlpha"]]

print("Draft complete, flag string follows:")
print("".join(draft_codes.loc[draft_codes["IsAlpha"]]["Code"]))
print("".join(draft_codes.loc[~draft_codes["IsAlpha"]]["Code"]))
