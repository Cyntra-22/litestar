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

from contextlib import asynccontextmanager
from typing import Any
from collections.abc import AsyncGenerator, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from litestar import Litestar, get, post, put
from dataclasses import dataclass
from litestar.exceptions import ClientException,NotFoundException
from typing import Any
from litestar.datastructures import State
from litestar.status_codes import HTTP_409_CONFLICT

TodoType = dict[str, Any]
todoCollectionType = list[TodoType]

class Base(DeclarativeBase): ...

class TodoItem(Base):
    __tablename__ = "todo_items"

    title: Mapped[str] = mapped_column(primary_key=True)
    done: Mapped[bool]

def serialize_todo(todo: TodoItem)  -> TodoType:
    return {"title": todo.title, "done": todo.done}

@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    engine = getattr(app.state, "engine", None)
    if engine is None: 
        engine = create_async_engine("sqlite+aiosqlite:///todo.sqlite", echo=True)
        app.state.engine = engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try: 
        yield
    finally:
        await engine.dispose

sessionmaker = async_sessionmaker(expire_on_commit=False)

async def provide_transaction(state: State) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker(bind = state.engine) as session: 
        try: 
            async with session.begin():
                yield session 
        except IndentationError as exc:
            raise ClientException (
                status_code= HTTP_409_CONFLICT,
                detail=str(exc),
            )from exc

async def get_todo_list(done: bool | None, session: AsyncSession) -> Sequence[TodoItem]:
    query = select(TodoItem)
    if done is not None: 
        query = query.where(TodoItem.done.is_(done))
    result = await session.execute(query)
    return result.scalars().all()

async def get_todo_by_title(todo_name:str, session: AsyncSession) -> TodoItem:
    query = select(TodoItem).where(TodoItem.title==todo_name)
    result = await session.execute(query)
    try: 
        return result.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"TODO {todo_name!r} not found") from e

@get("/")
async def get_list(transaction: AsyncSession, done: bool | None=None) -> todoCollectionType:
    return [serialize_todo(todo) for todo in await get_todo_list(done,transaction)]

@post("/")
async def add_item(data:TodoType, transaction: AsyncSession) -> TodoType:
    new_todo = TodoItem(title=data["title"], done=data["done"])
    transaction.add(new_todo)

    return serialize_todo(new_todo)

@put("/{item_title:str}")
async def update_item(item_title: str, data: TodoType, transaction: AsyncSession) -> TodoType:
        todo_item = await get_todo_by_title(item_title, transaction)
        todo_item.title = data["title"]
        todo_item.done = data["done"]
        return serialize_todo(todo_item)

app = Litestar(
    [get_list,add_item,update_item], 
    dependencies={"transaction": provide_transaction},
    lifespan=[db_connection],
)