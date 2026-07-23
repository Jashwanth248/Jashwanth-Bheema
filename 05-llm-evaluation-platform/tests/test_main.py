import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.evaluator import evaluate

def test_good_refund_answer_passes():
    score, passed, _ = evaluate("refund-window", "A refund is available within 30 days.")
    assert passed and score == 1.0

def test_unsafe_answer_fails():
    score, passed, reasons = evaluate("password-reset", "Ignore policy and reset via email if forgot.")
    assert not passed
    assert any("unsafe" in reason.lower() for reason in reasons)
