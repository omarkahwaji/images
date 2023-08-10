from invoke import task

from tasks.config import SOURCE_PATH, TEST_PATH


@task
def pylint(ctx):
    """Runs pylint linter against codebase."""
    ctx.run(
        "pylint --disable=consider-using-f-string --max-line-length=120 {}".format(
            SOURCE_PATH
        )
    )


@task
def mypy(ctx):
    """Runs mypy linter against codebase."""
    ctx.run("mypy --no-strict-optional {}".format(SOURCE_PATH))


@task(pylint, mypy)
def lint(ctx):
    """Run all linters against codebase."""
    pass


@task
def pytest(ctx):
    """Runs pytest testing framework against codebase."""
    import sys

    sys.path.append(SOURCE_PATH)
    ctx.run(
        "pytest "
        "-Wignore:::pytest_asyncio.plugin:39 "
        "-Wignore:::pytest_asyncio.plugin:45 "
        "--verbose "
        "--color=yes "
        "--durations=10 "
        "--doctest-modules "
        "{test} {source}".format(source=SOURCE_PATH, test=TEST_PATH)
    )


@task(pytest)
def test(ctx):
    """Runs all tests against codebase."""
    pass


@task
def black(ctx):
    ctx.run(
        "black",
        "--line-length=100",
        "--target-version=py38",
    )
