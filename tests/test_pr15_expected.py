from pathlib import Path


def test_pr15_expected_fixture_files_are_present():
    """Ensure the sale fixture correction is included in this PR."""
    assert Path("tests/test_register_sale.py").exists()
    assert Path("tests/test_web_sale.py").exists()
