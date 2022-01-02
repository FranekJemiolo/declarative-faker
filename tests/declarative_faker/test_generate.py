import filecmp
import os

import pkg_resources
from click.testing import CliRunner

from declarative_faker import generate


def test_generate(tmpdir):
    out_dir = tmpdir.mkdir("out")
    runner = CliRunner()
    result = runner.invoke(
        generate.main,
        [
            "--schemas-dir",
            pkg_resources.resource_filename(__name__, "schemas"),
            "--out-dir",
            out_dir,
        ],
    )
    assert result.exit_code == 0
    expected = pkg_resources.resource_filename(__name__, "expected")
    match, mismatch, errors = filecmp.cmpfiles(out_dir, expected, os.listdir(expected))
    assert len(mismatch) == 0
    assert len(errors) == 0
    assert len(match) == 3
