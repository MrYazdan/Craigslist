from typing import Callable
from core.utils import banner
from core.state import StateManager
from importlib import import_module


class CallBack:
    def __init__(self, func: str | Callable, package: None | str = None, *args, **kwargs):
        self.func = func
        self.package = package

        self.kwargs = kwargs
        self.args = args

        self.func = getattr(
            import_module(self.package or __name__),
            self.func if isinstance(self.func, str) else self.func.__name__
        )

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


class Route:
    def __init__(self, name, description=None, callback=None, children=None, condition=lambda: True):
        self.parent = None
        self.children = None

        self.name = name
        self.description = description
        self.callback = callback
        self.condition = condition

        children and self._set_parent(children)

    def _set_parent(self, children):
        for child in children:
            child.parent = self
        self.children = children

    def _get_route(self):
        try:
            banner(StateManager.get_current_route_name())
            print(self.description or "", end="\n\n")

            if children := [child for child in self.children if child.condition()]:
                for child in children:
                    print(f"\t{children.index(child) + 1}. {child.name}")
                print(f"\n\t0. " + ("Exit" if not self.parent else f"Back to {self.parent.name}"))

                index = int(input("\n> ")) - 1
                route = children[index] if index != -1 else self.parent

                if not route:
                    banner("Exit")

                    if input("Do you want to exit ? [y|N] ").strip().lower()[0] == "y":
                        print("Goodbye !")
                        exit()
                    else:
                        self()
                return route
            else:
                return self
        except (IndexError, ValueError, KeyboardInterrupt):
            banner("Error")
            input("Please enter a valid item\n\nPress Enter to continue ... ")
            self()

    def __call__(self, *args, **kwargs):
        StateManager.add_route_name(self.name)

        route = self._get_route()

        if self.parent == route:
            StateManager.delete_last_route_name()
            route()
        elif route.children:
            route()
        else:
            try:
                banner(route.name)
                route.callback and route.callback(route)
            except Exception as e:
                banner("Error")
            input("\nPress Enter to continue ... ")
            StateManager.delete_last_route_name()
            route.parent()


class Router:
    def __init__(self, route):
        self.route = route
        StateManager.add_route_name(route.name)

    def __call__(self, *args, **kwargs):
        self.route(*args, **kwargs)
