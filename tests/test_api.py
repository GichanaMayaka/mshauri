from http import HTTPStatus

from sqlalchemy import func

from mshauri.models import CME, MentorsChecklist


def test_get_checklists(client_app):
    with client_app as test_client:
        cme = CME.create(name="test checklist")

        # Create a new MentorsChecklist record
        MentorsChecklist.create(
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

        response = test_client.get("/checklists")

    assert response.status_code == HTTPStatus.OK
