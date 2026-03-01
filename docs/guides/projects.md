# Projects

Projects let an authenticated user inspect organization context, create a sandbox, reset that
sandbox, and switch the active project in the current session.

## List Current Context

```python
projects = client.projects.list()
print(projects.organization.name)
for project in projects.projects:
    print(project.name, project.environment.value)
```

## Create A Sandbox

```python
sandbox_context = client.projects.create_sandbox({"name": "SDK Sandbox"})
```

If a sandbox already exists, the API returns the current organization context.

## Reset A Sandbox

Use `reset_sandbox()` to clear sandbox-scoped resources while keeping the sandbox project itself.

```python
client.projects.reset_sandbox()
```

This is useful in demos, QA environments, and end-to-end tests where you want a clean workspace
without rebuilding the whole user account.

## Switch The Active Project

Switching projects returns a fresh bearer token. Replace the client token immediately.

```python
sandbox = next(
    project for project in client.projects.list().projects
    if project.environment.value == "sandbox"
)
switched = client.projects.switch({"project_id": str(sandbox.id)})
client.set_bearer_token(switched.access_token)
```
