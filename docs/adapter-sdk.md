# Adapter SDK

Expose adapters via Python entry points group `annox.adapters`.

Interface (simplified):

```
class Adapter(Protocol):
    def load(self, path: str) -> Dataset: ...
    def dump(self, dataset: Dataset, path: str) -> None: ...
    def capabilities(self) -> dict[str, bool]: ...
```

Register in your `pyproject.toml`:

```
[project.entry-points."annox.adapters"]
myformat = "my_pkg.my_mod:MyAdapter"
```

