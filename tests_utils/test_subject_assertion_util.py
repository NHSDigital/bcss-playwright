import pytest
from utils.subject_assertion import subject_assertion

pytestmark = [pytest.mark.utils_local]


def test_subject_assertion_true():
    nhs_number = "9233639266"
    criteria = {"screening status": "Inactive", "subject age": "> 28"}
    assert subject_assertion(nhs_number, criteria) is True


def test_subject_assertion_false():
    nhs_number = "9233639266"
    criteria = {"screening status": "Call", "subject age": "< 28"}
    assert subject_assertion(nhs_number, criteria) is False


def test_subject_assertion_false_with_some_true():
    nhs_number = "9233639266"
    criteria = {"screening status": "Inactive", "subject age": "< 28"}
    assert subject_assertion(nhs_number, criteria) is False
