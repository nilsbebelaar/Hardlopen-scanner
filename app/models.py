from app import db
from sqlalchemy import asc, desc


class Deelnemers(db.Model):
    __tablename__ = 'Deelnemers'

    id = db.Column(db.Integer, primary_key=True)

    naam = db.Column(db.String(50))
    geslacht = db.Column(db.String(1))

    barcode = db.Column(db.Integer, unique=True)
    tijden = db.relationship('Tijden', back_populates='deelnemer')


class Tijden(db.Model):
    __tablename__ = 'Tijden'

    id = db.Column(db.Integer, primary_key=True)
    tijd = db.Column(db.Float)
    barcode = db.Column(db.Integer, db.ForeignKey('Deelnemers.barcode'))
    deelnemer = db.relationship("Deelnemers", back_populates="tijden")
