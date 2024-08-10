from http import HTTPStatus

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.triggers.cron import CronTrigger
from flask import Blueprint, request

from mshauri.models import MentorsChecklist

bp = Blueprint("checklist", __name__)


@bp.route("/checklists", methods=["GET"])
def get_checklists() -> tuple[dict, int]:
    checklists = MentorsChecklist.query.all()

    if checklists:
        return {"checklists": checklists}, HTTPStatus.OK

    return {"message": "Not Found"}, HTTPStatus.NOT_FOUND


@bp.route("/schedule", methods=["POST"])
def modify_trigger() -> tuple[dict, int]:
    data = request.get_json()
    trigger = data.get("schedule")

    if not trigger:
        return {
            "message": "Please specify a Cron expression under the 'schedule' key"
        }, HTTPStatus.BAD_REQUEST

    try:
        cron_trigger = CronTrigger.from_crontab(trigger)
        job = scheduler.get_job("parse_dataset")

        if job:
            job.modify(trigger=cron_trigger)
            message = "Job trigger modified successfully!"

        else:
            # If the job doesn't exist, add a new job
            message = "No jobs currently scheduled"
            return {
                "error": "No Job[s] found",
                "detail": message,
            }, HTTPStatus.NOT_FOUND

    except ValueError as e:
        return {
            "error": "Invalid cron expression",
            "details": str(e),
        }, HTTPStatus.BAD_REQUEST

    except ConflictingIdError:
        return {"error": "Job ID conflict"}, HTTPStatus.BAD_REQUEST

    return {"message": message}, HTTPStatus.OK
