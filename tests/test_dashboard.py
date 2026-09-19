from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_handles_missing_database(tmp_path, monkeypatch):
    monkeypatch.setenv("CLICKPE_PIM_DB", str(tmp_path / "missing.sqlite"))
    app = AppTest.from_file(str(Path("app/dashboard.py").resolve())).run()
    assert not app.exception
    assert any("No monitoring run" in item.value for item in app.info)


def test_all_pages_handle_empty_state(tmp_path, monkeypatch):
    monkeypatch.setenv("CLICKPE_PIM_DB", str(tmp_path / "missing.sqlite"))
    app = AppTest.from_file(str(Path("app/dashboard.py").resolve())).run()
    for page in (
        "pages/1_Review_Queue.py",
        "pages/2_Product_Explorer.py",
        "pages/3_Change_History.py",
        "pages/4_Providers.py",
    ):
        app.switch_page(page).run()
        assert not app.exception
