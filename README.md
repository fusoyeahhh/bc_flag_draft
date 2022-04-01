# bc_flag_draft
Flag Drafting Tools for FFVI BC

## Help / Show All Options

Use this to see all options.

```bash
python -m flag_draft --help
````

## Show Draft Flags / Codes

Add `-S` to see all codes and flags in the pool with other options.

```bash
python -m flag_draft --standard-draft --add-challenges -S
````

## Draft Flags

"Standard" means that inappropriate and aesthetic codes are dropped, and standard flags are not included in the pool.

```bash
python -m flag_draft --standard-draft
```

Do a "full" draft of 20 rounds, with 5 options per round, and two rerolls allowed. Codes in the `gamebreaking` category are omitted, and codes like `swdtechspeed` and boosts are included with their options.

```bash
python -m flag_draft --draft-length 20 --draft-size 5 --allow-undo ---allow-reroll 2 --ban-category gamebreaking --allow-suboptions
```

## Draft Flags (with Challenges)

Same as above, but adds in self-imposed challenges.

```bash
python -m flag_draft --standard-draft --add-challenges
```

## Random Flags

Just get a set of the specified number of flags.

```bash
python -m flag_draft -r 10
```
