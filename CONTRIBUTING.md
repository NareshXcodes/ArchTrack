# Query Access Rules

## Route Handlers

All data queries inside route handlers must use `OrgScopedQuery`.

Direct use of:

```python
db.query(...)
```

is not allowed in route handlers.

## Allowed Exceptions

Raw database queries are only permitted inside:

* `get_scoped_query()`
* `/auth/bootstrap`
* `OrgScopedQuery`

## Correct

```python
projects = sq.projects().all()

teams = sq.teams().all()

users = sq.users().all()
```

## Incorrect

```python
projects = db.query(Project).all()

team = db.query(Team).filter(
    Team.id == team_id
).first()
```

Do not use raw `db.query()` for tenant-scoped resources
(Project, Decision, Team, User, Organization).

Global resources (e.g. Tag) may be queried directly.


## Enforcement

Pull requests introducing raw `db.query(...)` calls in route handlers should be rejected during code review.
