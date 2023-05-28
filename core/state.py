class StateManager:
    __routes = []

    @classmethod
    def get_current_route_name(cls):
        return " > ".join(cls.__routes)

    @classmethod
    def add_route_name(cls, name: str):
        if not len(cls.__routes) or cls.__routes[-1] != name:
            cls.__routes.append(name)

    @classmethod
    def delete_last_route_name(cls) -> None:
        cls.__routes.pop()
