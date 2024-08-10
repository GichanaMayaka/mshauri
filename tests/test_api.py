from http import HTTPStatus

from sqlalchemy import func

from mshauri.models import CME, MentorsChecklist


def test_get_checklists(client_app):
    """Test the /checklists endpoint"""
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


def test_modify_trigger_success(client_app):
    """Test modifying the job trigger"""
    with client_app as test_client:
        response = test_client.post(
            "/schedule",
            json=dict(schedule="* * * * *"),
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json["message"] == "Job trigger modified successfully!"


def test_modify_trigger_invalid_expression(client_app):
    """Tests modifying trigger with invalid expressions"""
    with client_app as test_client:
        response_1 = test_client.post(
            "/schedule",
            json=dict(schedule="* * * *"),
        )

        response_2 = test_client.post(
            "/schedule",
            json=dict(schedule="61 14 * * 1"),
        )

        response_3 = test_client.post(
            "/schedule",
            json=dict(schedule="* 12 32 12 *"),
        )

        response_4 = test_client.post(
            "/schedule",
            json=dict(schedule="* 12 32 12 *"),
        )

    assert response_1.status_code == HTTPStatus.BAD_REQUEST
    assert response_1.json["error"] == "Invalid cron expression"

    assert response_2.status_code == HTTPStatus.BAD_REQUEST
    assert response_2.json["error"] == "Invalid cron expression"

    assert response_3.status_code == HTTPStatus.BAD_REQUEST
    assert response_3.json["error"] == "Invalid cron expression"

    assert response_4.status_code == HTTPStatus.BAD_REQUEST
    assert response_4.json["error"] == "Invalid cron expression"
