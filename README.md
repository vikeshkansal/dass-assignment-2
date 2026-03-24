# DASS Assignment 2 - Testing

## Links

**Google Drive**: https://drive.google.com/drive/folders/1d4cwDX6BuAw5z05xF0FvpxT4ikwsWPmX?usp=sharing

**GitHub**: https://github.com/vikeshkansal/dass-assignment-2

## Setup

1. `uv venv`
2. `source .venv/bin/activate`
3. `uv pip install pytest`

With this, you can run the test suites in the `whitebox/` and `integration/` parts - to do this, do:

```
pytest tests
```

where `tests` is the folder in each part.

The same can be done for `blackbox/` too, given the docker container is running. 
