from ..extensions import db


class CreateReadMixin:
    """
    Create and Access Mixin
    """

    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    @classmethod
    def get_by_id(cls, id: int):
        if any(
            (isinstance(id, str) and id.isdigit(), isinstance(id, (int, float))),
        ):
            return cls.query.get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()
