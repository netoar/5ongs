import os
from flask import jsonify, abort
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from model.db_config import db
from datetime import datetime
import logging
from sqlalchemy.ext.declarative import declarative_base


class Song(db.Model):
    __tablename__ = "song"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    artist_name = Column(String)
    date_release = Column(db.Date)
    date_send = Column(db.Date)
    rate = relationship("Rate")

    def __init__(self, title, artist_name, date_release, date_send):
        self.title = title
        self.artist_name = artist_name
        self.date_release = date_release
        self.date_send = date_send

    def format(self):
        return {"id": self.id, "title": self.title, "artist_name": self.artist_name,
                "date_release": self.date_release, "date_send": self.date_send}


def find_song(song_id):
    try:
        song = Song.query.filter_by(id=song_id).first()
    except Exception as e:
        abort(400)
    return song


def find_song_by_title(title):
    try:
        song = Song.query.filter_by(title=title).first()
    except Exception as e:
        abort(400)
    return song


def find_songs():
    try:
        songs = Song.query.all()
    except Exception as e:
        abort(400)
    return songs


def create_song(title, name, release, send):
    new_song = Song(
        title=title,
        artist_name=name,
        date_release=release,
        date_send=send)

    error = False
    try:
        logging.info('inserting new song', new_song)
        db.session.add(new_song)
        db.session.commit()
        message = f'{new_song.title} was successfully listed!'
    except Exception as e:
        error = True
        logging.error(e)
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    if not error:
        return message
    else:
        abort(500)


def update_song(id, title, name, release, send):
    edit_song = Song.query.filter_by(id=id).first()
    edit_song.title = title
    edit_song.artist_name = name
    edit_song.date_release = release
    edit_song.date_send = send

    error = False
    try:
        logging.info('updating song', edit_song)
        db.session.add(edit_song)
        db.session.commit()
        message = f'{edit_song.title} was successfully updated!'
    except Exception as e:
        error = True
        logging.error(e)
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    if not error:
        return message
    else:
        abort(500)


def remove_song(song):
    error = False
    try:
        logging.info('deleting song', song)
        db.session.delete(song)
        db.session.commit()
        message = f'{song.title} was successfully deleted!'
    except Exception as e:
        error = True
        logging.error(e)
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    if not error:
        return message
    else:
        abort(500)
