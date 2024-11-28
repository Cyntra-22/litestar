'''from litestar import Litestar, get, post, put
from dataclasses import dataclass
from typing import Any
from litestar.exceptions import NotFoundException


@dataclass
class TodoItem:
    title: str
    done: bool

TODO_LIST: list[TodoItem] = [
    TodoItem(title="Start writing TODO list", done=True),
    TodoItem(title="???", done=False),
    TodoItem(title="Profit", done=False),
]



@get("/")
async def get_list(done:bool | None = None) -> list[TodoItem]:
    if done is None:
        return TODO_LIST
    return [item for item in TODO_LIST if item.done==done]
    

TODO_LIST1: list[TodoItem] = []
@post("/")
async def add_item(data: TodoItem) -> list[TodoItem]:
    TODO_LIST1.append(data)
    return TODO_LIST1


def get_todo_by_title(todo_name) -> TodoItem:
    for item in TODO_LIST:
        if item.title == todo_name:
            return item
    raise NotFoundException(detai=f"TODO {todo_name!r} not found")

@put("/{item_title:str}")
async def update_item(item_title: str, data:TodoItem) -> list[TodoItem]:
    todo_item = get_todo_by_title(item_title)
    todo_item.title = data.title
    todo_item.done = data.done
    return TODO_LIST


app = Litestar([update_item])
#app = Litestar([get_list])

'''


from litestar import Litestar, get, post, put
from dataclasses import dataclass
from litestar.exceptions import NotFoundException

@dataclass
class TodoItem: 
    title: str
    done: bool

TODO_LIST: list[TodoItem] = [
    TodoItem(title="Title 1", done= True),
    TodoItem(title="Title 2", done= False),
    TodoItem(title="Title 3", done=False),
]

@get("/")
async def get_list(done: bool | None=None) -> list[TodoItem]:
    if done is None:
        return TODO_LIST
    return [item for item in TODO_LIST if item.done == done]


@post("/")
async def add_item(data:TodoItem) -> list[TodoItem]:
    TODO_LIST.append(data)
    return TODO_LIST


def get_todo_by_title(todo_name) -> TodoItem:
    for item in TODO_LIST:
        if item.title == todo_name:
            return item
    raise NotFoundException(detail=f"TODO {todo_name!r} not found")


@put("/{item_title:str}")
async def update_item(item_title: str, data: TodoItem) -> list[TodoItem]:
    todo_item = get_todo_by_title(item_title)
    todo_item.title = data.title
    todo_item.done = data.done
    return TODO_LIST


app = Litestar([get_list,add_item,update_item])