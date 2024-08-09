from mshauri.extensions import db


class CRUDMixin:
    """
    CRUD Mixin
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
    def get_by_name(cls, name: str):
        result = cls.query.filter_by(name=name).first()

        return result.id if result else None

    @classmethod
    def create(cls, **kwargs):
        """Creates record and return its Id"""
        instance = cls(**kwargs)
        instance.save()
        return instance.id

    def save(self, commit: bool = True):
        db.session.add(self)

        if commit:
            db.session.commit()
        return self

    def delete(self, commit: bool = True, **kwargs):
        db.session.delete(self)

        if commit:
            db.session.commit()
        return self

    def update(self, commit: bool = True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self
