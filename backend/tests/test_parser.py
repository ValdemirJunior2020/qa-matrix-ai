from pathlib import Path
from app.services.matrix_parser import parse_matrix

def test_matrix_parser():
    p=Path(__file__).parents[1]/"data"/"matrix"/"active"/"new matrix-06_22_26(10).xlsx"
    data=parse_matrix(p)
    assert data["sheet_count"] == 3
    assert data["rule_count"] > 80
    assert any(r["sheet"]=="Voice Matrix" for r in data["records"])
    assert any(r["sheet"]=="Ticket Matrix" for r in data["records"])

def test_does_not_invent_critical():
    p=Path(__file__).parents[1]/"data"/"matrix"/"active"/"new matrix-06_22_26(10).xlsx"
    data=parse_matrix(p)
    assert not any(r["critical"] for r in data["records"])
