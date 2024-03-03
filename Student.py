from State import State


class Student:
    __instance = None

    def __init__(self, name : str, id: str, catalog: str, degree_type: str, state: State):
        self.__name = name
        self.__id = id
        self.__catalog = catalog  # "2022-2023"
        self.__degree_type = degree_type  # "Computer Science"
        self.__state = state

        if Student.__instance is None:
            Student.__instance = self
        else:
            raise Exception("Student instance already exists")

    @staticmethod
    def get_instance():
        if Student.__instance is None:
            raise Exception("Student instance does not exist")
        return Student.__instance

    def get_name(self) -> str:
        return self.__name

    def get_id(self) -> str:
        return self.__id

    def get_catalog(self) -> str:
        return self.__catalog

    def get_degree_type(self) -> str:
        return self.__degree_type

    def set_new_state(self, new_state: State) -> None:
        self.__state = new_state

    def is_graduate(self) -> bool:
        return self.__state.is_graduate()

    def get_state(self) -> State:
        return self.__state
