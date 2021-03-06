def construct_args(argp):
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
    argp.add_argument("-l", "--ban-list",
                      help="Codes listed in the ban list will be removed.")
    argp.add_argument("-D", "--dont-remove-alpha-flags", action="store_true",
                      help="Randomize over codes and alphabet flags.")
    argp.add_argument("-c", "--add-challenges", action="store_true",
                      help="Add self-imposed challenges to pool.")
    argp.add_argument("-s", "--draft-size", type=int, default=3,
                      help="Provided with numerical argument, do this many choices per round.")
    argp.add_argument("-R", "--draft-rerolls", type=int, default=0,
                      help="Allow this many rerolls. Default is zero.")
    argp.add_argument("-d", "--draft-length", type=int, default=10,
                      help="Provided with numerical argument, do this many draft rounds.")
    argp.add_argument("--standard-draft", action="store_true",
                      help="Remove codes which are unsafe, not gameplay related "
                           "or standard mode inappropriate. "
                           "Implies --only-codes and --allow-suboptions.")

    return argp

def enable_standard_draft(args):
    args.allow_suboptions = True
    args.ban_categories = ["gamebreaking"]
    # TODO: check what the standard should be
    args.always_on = args.always_on or []
    # TODO: Handle with banlist
    """
    args.always_on += ["!bingoboingo", "!sketch", "!playsitself", "!makeover",
                       "!removeflashing", "!sprint",
                       "!johnnyachaotic", "!johnnydmad"]
    """

    return args