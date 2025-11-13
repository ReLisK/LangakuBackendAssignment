# Assignment Template

## Initial Setup

- uv is recommended for managing virtual environments.

```
uv sync --all-groups

uv run manage.py migrate
```

### Run tests

```
uv run poe test
```

### Run server

```
uv run manage.py runserver
```


### Lint and format code

```
uv run poe lint
uv run poe format
```



# In production these would be in an environment config file and not stored in clear text of course.
postgresql DB 
- user:     postgres
- password: password
superuser
- user:    superuser
- password password