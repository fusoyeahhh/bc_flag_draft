from . import SUBOPTION_CODES, CHALLENGES
from . import split_suboptions, construct_pool

class BCFlagDrafter:
    def __init__(self, only_codes=False, allow_suboptions=True,
                 allow_undo=False, rerolls=0,
                 add_challenges=False, always_on={}, ban_category={}):

        self.only_codes = only_codes
        self.allow_suboptions = allow_suboptions
        self.add_challenges = add_challenges
        self.always_on = always_on or {}
        self.ban_category = ban_category or {}
        self.allow_undo = allow_undo
        self._rerolls = rerolls or 0

        self.draft_codes = None
        self.round = None

        self.codes = construct_pool()
        self._init_pool()

    def _init_pool(self):
        if self.add_challenges:
            SUBOPTION_CODES.add("challenge")
            # will probably need weights for this
            new_code = {
                "name": "challenge",
                "category": "challenge",
                "long_description": "Self imposed challenge",
                "choices":  CHALLENGES
            }
            self.codes = self.codes.append(new_code, ignore_index=True)

        self.codes["is_flag"] = self.codes["is_flag"].fillna(False)
        self.codes = self.codes.reset_index(drop=True)

        self.codes["is_suboption"] = False
        if self.allow_suboptions:
            self.codes = split_suboptions(self.codes)
        else:
            # Drop multiplier codes
            self.codes = self.codes.loc[~self.codes["name"].isin(SUBOPTION_CODES)]

        always_on = {code for code in self.always_on
                                        if not code.startswith("!")}
        self.codes["status"] = None
        self._draft_codes = []
        if always_on:
            turn_on = self.codes["name"].isin(always_on)
            self._draft_codes = self.codes.loc[turn_on].index
            self.codes.loc[turn_on,"status"] = "always_on"
            print(f"Adding {always_on} into draft automatically.")

        ban_code = {code[1:] for code in self.always_on
                                        if code.startswith("!")}
        get_banned = self.codes["name"].isin(ban_code)
        if ban_code:
            print(f"Banning {ban_code} from pool.")
        if self.ban_category:
            get_banned |= self.codes["category"].isin(self.ban_category)
            print(f"Banning category {self.ban_category} from pool.")
        self.codes.loc[get_banned,"status"] = "banned"

        if self.only_codes:
            self.codes = self.codes.loc[~self.codes["is_flag"]]
            print(f"Dropping standard flags from pool.")

    def draft(self, rounds=1, draft_size=3):
        self.draft_codes = []
        self.round = 0
        self.rerolls = self._rerolls

        start_flags = len(self.draft_codes)
        self.draft_codes = list(self._draft_codes)
        while len(self.draft_codes) < rounds + start_flags:
            yield self.pull_from_pool(draft_size)

    def pull_from_pool(self, draft_size=3):
        if self.allow_undo:
            pool = self.codes.index
        else:
            pool = self.codes.index.difference(self.draft_codes)
        elig = self.codes["status"].isna()
        pool = pool.intersection(self.codes.loc[elig].index)

        self.codes["selected"] = self.codes.index.isin(self.draft_codes)
        return self.codes.loc[pool].sample(draft_size)[:]

    def randomize_flags(self, nflags):
        choices = self.pull_from_pool(min(nflags, len(self.draft_codes)))
        self.draft_codes = list(choices.index)

    def _maybe_replace_option(self, idx):
        opt = self.codes.loc[idx]
        if not opt["is_suboption"]:
            return idx

        _codes = self.codes.loc[self.codes.index.intersection([idx])]
        opt = _codes.loc[opt["suboption_of"] == _codes["suboption_of"]]
        return list(set([idx]) - set(opt.index))

    def draft_code(self, idx, is_reroll=False):
        self._maybe_replace_option(idx)

        if self.codes.loc[idx]["selected"]:
            self.draft_codes.remove(idx)
        else:
            self.draft_codes.append(idx)

        if is_reroll:
            import pdb; pdb.set_trace()
        self.rerolls -= int(is_reroll)
        assert self.rerolls >= 0
        self.round += int(not is_reroll)

    def show_flags(self):
        print(self.codes.sort_values(by="category").set_index(["name", "category"])[["long_description"]])

    def show_result(self):
        draft_codes = self.codes.loc[self.draft_codes]
        flags = draft_codes.loc[draft_codes["is_flag"]]["name"].sort_values()
        subopts = draft_codes.loc[draft_codes["is_suboption"]]["name"].sort_values()
        codes = ~(draft_codes["is_flag"] | draft_codes["is_suboption"])
        print("Standard flags:")
        print("".join(flags))
        print("Standard codes:")
        print("".join(draft_codes.loc[codes]["name"]))
        print("Codes with options:")
        print(" ".join(subopts))
