import contextlib
import io
from pathlib import Path

import blocknot_old

GOLDEN_MASTER_PATH = Path("golden_master.txt")
DATA_PATH = Path("barakhlo.csv")


def _capture_zvit_output(csv_path: Path) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        blocknot_old.zvit(str(csv_path))
    return buffer.getvalue()


def test_zvit_matches_golden_master() -> None:
    expected = GOLDEN_MASTER_PATH.read_text(encoding="utf-8")
    actual = _capture_zvit_output(DATA_PATH)
    assert actual == expected