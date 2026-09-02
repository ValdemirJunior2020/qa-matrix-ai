from app.services.scoring_service import calculate_total_score,apply_critical

def test_no_score_is_not_invented():
    r=calculate_total_score([{"score":None}])
    assert r["authoritative"] is False and r["value"] is None

def test_critical_does_not_assume_zero():
    r=apply_critical(95,{"critical":True,"critical_condition":"Critical finding"})
    assert r["value"]==95 and r["authoritative"] is False
