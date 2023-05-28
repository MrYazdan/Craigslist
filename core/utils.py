from os import system as terminal, name as os_name


def clear():
    terminal("cls" if os_name.lower() == "nt" else "clear")


def banner(name):
    clear()
    print("=" * 30, name.title().center(30), "=" * 30, sep="\n")


def try_again(route, function):
    if input("\nTry again ? [Y|n] ").strip().lower()[0] == "n":
        route.parent()
    else:
        banner(route.name)
        function(route)
