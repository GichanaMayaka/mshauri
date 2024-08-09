from dataclasses import dataclass
from typing import Optional

from sqlalchemy import func

from mshauri.extensions import db

from .mixins import CRUDMixin


class CME(db.Model, CRUDMixin):
    """CME Model

    Args:
        db (SQLAlchemy): DB instance
        CRUDMixin (CRUDMixin): CRUD operations mixin
    """

    __tablename__ = "cme"

    name = db.Column(db.String(100), nullable=False, unique=True)

    mentor_checklist = db.relationship("MentorsChecklist", backref="cme", lazy="joined")


class Drill(db.Model, CRUDMixin):
    """Drills Model

    Args:
        db (SQLAlchemy): db Instance
        CRUDMixin (CRUDMixin): CRUD operations mixin
    """

    __tablename__ = "drill"

    name = db.Column(db.String(100), nullable=False, unique=True)

    mentor_checklist = db.relationship(
        "MentorsChecklist", backref="drill", lazy="joined"
    )


@dataclass(kw_only=True)
class MentorsChecklist(db.Model, CRUDMixin):
    """Mentors Checklist Model

    Args:
        db (SQLAlchemy): DB instance
        CRUDMixin (CRUDMixin): CRUD operations mixin
    """

    # For serialisation
    id: int
    cme_completion_date: str
    cme_unique_id: str
    county: str
    date_submitted: str
    drill_unique_id: str
    essential_cme_topic: str
    essential_drill_topic: str
    facility_code: str
    facility_name: str
    id_number_cme: str
    id_number_drill: str
    mentor_name: str
    submission_id: str
    success_story: str
    cme_topic: Optional[str] = None
    drill_topic: Optional[str] = None

    __tablename__ = "mentors_checklist"

    cme_completion_date = db.Column(db.Date, nullable=False, default=func.now())
    cme_unique_id = db.Column(
        db.BigInteger,
        db.ForeignKey("cme.id"),
        nullable=True,
        index=True,
    )
    county = db.Column(db.String(100), nullable=False)
    date_submitted = db.Column(
        db.DateTime(timezone=True), nullable=False, default=func.now()
    )
    drill_unique_id = db.Column(
        db.Integer,
        db.ForeignKey("drill.id"),
        nullable=True,
        index=True,
    )
    essential_cme_topic = db.Column(db.Boolean, nullable=False, default=False)
    essential_drill_topic = db.Column(db.Boolean, nullable=False, default=False)
    facility_code = db.Column(db.String(100), nullable=False)
    facility_name = db.Column(db.String(100), nullable=False)
    id_number_cme = db.Column(db.String(100), nullable=True, unique=False)
    id_number_drill = db.Column(db.String(100), nullable=True, unique=False)
    mentor_name = db.Column(db.String(100), nullable=False, unique=False)
    submission_id = db.Column(db.BigInteger, nullable=False, unique=False)
    success_story = db.Column(db.String(100), nullable=True)

    @property
    def drill_topic(self):
        """Access relationship"""
        return None if self.drill is None else self.drill.name

    @property
    def cme_topic(self):
        """Access relationship"""
        return None if self.cme is None else self.cme.name
