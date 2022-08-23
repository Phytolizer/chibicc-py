import subprocess
import sys
from pathlib import PurePath
from tempfile import TemporaryDirectory

import pytest

from chibicc.chibicc import chibicc


def check_output(args: list[str], expected_code: int):
    with TemporaryDirectory() as tmpdir:
        with open(PurePath(tmpdir) / "out.s", "w+") as f:
            result = chibicc(["chibicc", *args], f)
            if result != 0:
                f.seek(0)
                print(f.read(), file=sys.stderr)
                pytest.fail(f"chibicc returned {result}")
        try:
            subprocess.run(
                [
                    "gcc",
                    "-static",
                    "-o",
                    PurePath(tmpdir) / "out",
                    PurePath(tmpdir) / "out.s",
                ],
                check=True,
            )
        except subprocess.SubprocessError:
            pytest.fail("gcc failed to run?")
        try:
            run_result = subprocess.run([PurePath(tmpdir) / "out"])
        except subprocess.SubprocessError:
            pytest.fail("compiled program failed to run")
        if run_result.returncode != expected_code:
            with open(PurePath(tmpdir) / "out.s", "r") as f:
                print(f.read())
            pytest.fail(f"expected {expected_code} but got {run_result.returncode}")


def test_0_returns_0():
    check_output(["0"], 0)


def test_42_returns_42():
    check_output(["42"], 42)


def test_plus_minus():
    check_output(["5+20-4"], 21)


def test_with_whitespace():
    check_output([" 12 + 34 - 5 "], 41)
