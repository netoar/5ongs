import os
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask import abort
from model.db_config import db
from datetime import date
from model.song import Song
from sqlalchemy.ext.declarative import declarative_base


class Rate(db.Model):
    __tablename__ = "rate"

    id = Column(Integer, primary_key=True)
    # song_id
    rate = Column(Integer)
    date_rate = Column(db.Date)
    # song_id = Column(db.Integer, db.ForeignKey('Song.rate_id'), nullable=True)
    song_id = Column(Integer, ForeignKey('song.id'))
    song = relationship(Song)

    def __init__(self, rate, date_rate, song_id):
        self.rate = rate
        self.date_rate = date_rate
        self.song_id = song_id

    def format(self):
        return {"id": self.id, "rate": self.rate, "date_rate": self.date_rate, "song_id": self.song_id}


def create_rate(song_id, rate):
    try:
        today = date.today()
        today_formatted = today.isoformat()
        song_rate = Rate(
            rate=rate,
            date_rate=today_formatted,
            song_id=song_id)
        db.session.add(song_rate)
        db.session.commit()
        message = f'The song was rated!'
    except Exception as e:
        message = f'An error occur'
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    return message


def update_rate(song_id, rate):
    try:
        today = date.today()
        today_formatted = today.isoformat()
        song_rate = Rate(
            rate=rate,
            date_rate=today_formatted,
            song_id=song_id)
        db.session.add(song_rate)
        db.session.commit()
        message = f'The song was rated!'
    except Exception as e:
        message = f'An error occur'
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    return message


def rate_average(song_id):
    song_rates = Rate.query.filter_by(song_id=song_id).all()
    average_rate = 0
    for rate in song_rates:
        average_rate += rate.rate
    if average_rate != 0:
        average_rate /= len(song_rates)
    return average_rate


def remove_rates(song_id):
    try:
        rates = Rate.query.filter_by(song_id=song_id).all()
        for rate in rates:
            db.session.delete(rate)
            db.session.commit()
        message = f'The rates were deleted!'
    except Exception as e:
        db.session.rollback()
        message = f'An error occur'
        abort(422)
    finally:
        db.session.close()
    return message
