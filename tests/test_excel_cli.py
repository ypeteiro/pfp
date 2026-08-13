from pfp.excel.__main__ import main


def test_excel_cli_creates_workbook(tmp_path, monkeypatch, capsys):
    movements = tmp_path / "movements.csv"
    output = tmp_path / "reports" / "pfp.xlsx"
    movements.write_text("symbol,shares,amount,type\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["pfp.excel", str(movements), "--output", str(output)],
    )

    main()

    assert output.exists()
    assert output.stat().st_size > 0
    assert "Excel generado:" in capsys.readouterr().out
