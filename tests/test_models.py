import pytest
from sqlalchemy import func

from ..mshauri.models import CME, Drill, MentorsChecklist


def test_create_cme_model(client_app):
    test_cme_id = CME.create(name="test cme")

    # Fetch created record
    test_cme = CME.get_by_id(test_cme_id)
    assert test_cme.name == "test cme"


def test_create_drill_model(client_app):
    test_drill_id = Drill.create(name="test drill")

    # Fetch created drill record
    test_drill = Drill.get_by_id(test_drill_id)
    assert test_drill.name == "test drill"


def test_mentors_checklist_model(client_app):
    cme = CME.create(name="test mentors checklist")
    drill = Drill.create(name="test mentors checklist")

    # Create a new MentorsChecklist record
    test_checklist_id_1 = MentorsChecklist.create(
        cme_completion_date=func.now(),
        cme_unique_id=cme,
        county="Nairobi",
        date_submitted=func.now(),
        drill_unique_id=None,
        essential_cme_topic=True,
        essential_drill_topic=False,
        facility_code="00101",
        facility_name="Nairobi Health Center",
        id_number_cme="101101",
        id_number_drill=None,
        mentor_name="John Doe",
        submission_id=123456789,
        success_story="it was a success",
    )

    test_checklist_id_2 = MentorsChecklist.create(
        cme_completion_date=func.now(),
        cme_unique_id=None,
        county="Nairobi",
        date_submitted=func.now(),
        drill_unique_id=drill,
        essential_cme_topic=False,
        essential_drill_topic=True,
        facility_code="00101",
        facility_name="Nairobi Health Center",
        id_number_cme=None,
        id_number_drill="101101",
        mentor_name="Jane Doe",
        submission_id=987654321,
        success_story="it was another success",
    )

    # Fetch created checklist records
    checklists = MentorsChecklist.query.all()

    assert checklists is not None
    assert len(checklists) == 2

    checklist_1 = MentorsChecklist.get_by_id(test_checklist_id_1)

    assert checklist_1.mentor_name == "John Doe"
    assert checklist_1.cme_unique_id == cme
    assert checklist_1.cme_topic == "test mentors checklist"

    with pytest.raises(AttributeError):
        assert checklist_1.drill_topic is None

    checklist_2 = MentorsChecklist.get_by_id(test_checklist_id_2)

    assert checklist_2.mentor_name == "Jane Doe"
    assert checklist_2.drill_unique_id == drill
    assert checklist_2.drill_topic == "test mentors checklist"

    with pytest.raises(AttributeError):
        assert checklist_2.cme_topic is None
