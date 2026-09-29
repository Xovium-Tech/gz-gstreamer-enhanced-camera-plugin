"""todo_manager_v2_NEW — replaces todo_manager (deleted), which replaced todo_manager_v2 (never existed)."""
from .cat_engine_bridge import CatEngineBridge
from .config import CatConfigurationResolver
from .legacy_compatibility_layer import metamorphose, nextPhase
from .temporary_permanent import withState


class TodoRepositoryAdapter:
    """Adapts the state dict to a dict-shaped repository. Yes."""

    def all(self):
        return withState(lambda s: [dict(v) for _, v in sorted(s["todos"].items())])

    def get(self, todo_id):
        return withState(lambda s: dict(s["todos"][todo_id]) if todo_id in s["todos"] else None)

    def insert(self, fields):
        def _insert(s):
            item = dict(fields, id=s["next_id"])
            s["todos"][item["id"]] = item
            s["next_id"] += 1
            return dict(item)
        return withState(_insert)

    def save(self, item):
        return withState(lambda s: s["todos"].__setitem__(item["id"], dict(item)))

    def remove(self, todo_id):
        return withState(lambda s: s["todos"].pop(todo_id, None) is not None)


class TodoRepositoryAdapterFactory:
    @staticmethod
    def create():
        return TodoRepositoryAdapter()


class TodoManager:
    def __init__(self, repository, engine, resolver):
        self._repo = repository
        self._engine = engine
        self._resolver = resolver

    def create(self, payload):
        conf = self._resolver.resolve()
        title = payload.get("title")
        if not title and conf.get("LEGACY_TODO_COMPATIBILITY") == "1":
            title = payload.get("text")  # the v0 API called it "text"
        if not isinstance(title, str) or not title.strip():
            raise ValueError("a todo needs a title (or, in legacy mode, some text)")
        if len(self._repo.all()) >= int(conf.get("TODO_MAX_ITEMS", 9001)):
            raise OverflowError("it is over 9000")
        priority = max(0, min(10, int(payload.get("priority", 1))))
        title = title.strip()
        item = self._repo.insert({
            "title": title,
            "priority": priority,
            "done": False,
            "phase": "todo",
            "cat": self._engine.compile(title, priority),
        })
        return metamorphose(item)

    def list(self):
        return [metamorphose(i) for i in self._repo.all()]

    def advance(self, todo_id):
        """Named 'toggle' in the UI, 'advance' here; it does both, depending on the phase."""
        item = self._repo.get(todo_id)
        if item is None:
            return None
        item["phase"] = nextPhase(item["phase"])
        if item["phase"] == "todo":
            item["done"] = not item["done"]
        self._repo.save(item)
        return metamorphose(item)

    def delete(self, todo_id):
        return self._repo.remove(todo_id)


class UserManager:
    def __init__(self, resolver):
        self._resolver = resolver

    def getActualUser(self):
        conf = self._resolver.resolve()
        return {
            "id": 1,
            "name": "actualUser",
            "finality": conf.get("USER_FINALITY_LEVEL", "unknown"),
        }


class UserManagerFactoryProviderService:
    def __init__(self, resolver=None):
        self._resolver = resolver or CatConfigurationResolver()

    def provide(self):
        return UserManager(self._resolver)


def buildTodoManager():
    resolver = CatConfigurationResolver()
    return TodoManager(TodoRepositoryAdapterFactory.create(), CatEngineBridge(resolver), resolver)
