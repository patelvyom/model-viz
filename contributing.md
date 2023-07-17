## Setting up environment
See [README.md](README.md) for instructions on how to set up the environment.

## Coding Style
We are using `black` to format our code. Additionally, we are also using `flake8` to check for code style errors. To automate this process, we are using `pre-commit`. To install `pre-commit`, run the following command:
```
pre-commit install
```
This will create required git hooks before every commit. On every commit, `black` and `flake8` will be run on the files that are being committed and `black` will format the files if necessary. If there are any errors, the commit will be aborted and the errors will be displayed. Once errors are fixed, the commit can be re-run.
