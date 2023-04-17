import os
import json
from flask import Flask, render_template, abort, jsonify, request, Response, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from model.db_config import db, setup_db
from model.rate import Rate, update_rate, create_rate, rate_average, remove_rates
from model.song import Song, find_songs, create_song, update_song, find_song, remove_song, find_song_by_title
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin
from functools import wraps
from jose import jwt
from urllib.parse import urlparse
from auth import verify_decode_jwt, do_logout, get_login_url, get_token_from_code, get_user_from_token, get_logout_url, get_permissions_from_token
import secrets


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.debug = True
    setup_db(app)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=3600)

    # Generate a random secret key
    secret_key = secrets.token_hex(16)
    # Set the secret key in your Flask application
    app.secret_key = secret_key

    def get_song_info_from_request():
        if len(request.form) == 0:
            return json.loads(request.data)

        title = request.form['title']
        name = request.form['artist_name']
        release = request.form['date_release']
        send = request.form['date_send']
        rate = request.form['rate']
        return {'title': title, 'artist_name': name, 'date_release': release, 'date_send': send, 'rate_average': rate}

    def assign_user_to_login(name):
        loged_user = {
            "name": name, "lastname": "Perez", "email": "quierotuspalas@gmail.com"}
        return loged_user

    @app.route('/')
    def index():
        login_url = get_login_url()
        logout_url = get_logout_url()
        if 'username' in session:
            logged_user = assign_user_to_login(session['username'])
            return render_template('pages/home.html', user=logged_user, login=login_url, logout=logout_url)
        return render_template('pages/home.html', user=None, login=login_url, logout=logout_url)

    @app.route('/callback')
    def callback():
        url = request.url
        access_token = get_token_from_code(url)
        session.permanent = True
        # Set the token value in the user's session
        session['access_token'] = access_token
        user = get_user_from_token(access_token)
        permissions = get_permissions_from_token(access_token)
        session['permissions'] = permissions
        session['username'] = user['name']
        session['email'] = user['email']
        return redirect('/')

    @app.route('/logout')
    def logout():
        session.clear()
        do_logout()
        return redirect('/')

    def check_permissions(permissions, payload):
        if 'permissions' not in payload:
            abort(400)

        lets_go = False

        for permission in permissions:
            if permission in payload['permissions']:
                lets_go = True

        if lets_go:
            return True
        return abort(403)

    def requires_auth(permissions=[]):
        def requires_auth_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if 'HTTP_AUTHORIZATION' in request.headers.environ:
                    jwt = request.headers.environ['HTTP_AUTHORIZATION'].replace(
                        'Bearer ', '')
                elif 'access_token' in session:
                    jwt = session['access_token']
                else:
                    abort(401)

                try:
                    payload = verify_decode_jwt(jwt)
                except:
                    abort(401)

                check_permissions(permissions, payload)

                return f(jwt, *args, **kwargs)
            return wrapper
        return requires_auth_decorator

    @app.route('/song')
    def get_songs():
        songs = find_songs()
        return render_template('pages/songs.html', songs=songs)

    @app.route('/song/create', methods=['GET', 'POST'])
    @requires_auth(['post:songs'])
    def post_song(jwt):
        if request.method == 'GET':
            return render_template('pages/new_song.html')

        song_info = get_song_info_from_request()
        required_fields = ['title', 'artist_name',
                           'rate_average', 'date_release', 'date_send']

        if not all(field in song_info for field in required_fields):
            abort(422)

        create_song(song_info['title'], song_info['artist_name'],
                    song_info['date_release'], song_info['date_send'])
        new_song = find_song_by_title(song_info['title'])
        create_rate(new_song.id, song_info['rate_average'])
        return render_template('pages/song.html', song=song_info)

    @app.route('/song/<int:song_id>/edit', methods=['GET', 'POST'])
    @requires_auth(['post:songs', 'post:rate'])
    def edit_song(jwt, song_id):
        if request.method == 'GET':
            song = find_song(song_id)
            return render_template('pages/edit_song.html', song=song, permissions=session['permissions'])

        song_info = get_song_info_from_request()
        update_song(
            song_id, song_info['title'], song_info['artist_name'], song_info['date_release'], song_info['date_send'])
        update_rate(song_id, song_info['rate_average'])
        if len(request.form) == 0:
            # testing purposes
            return jsonify({'message': 'Song updated successfully'}), 200
        return redirect(f'/song/{song_id}')

    @app.route('/song/<int:song_id>')
    def display_song(song_id):
        if song_id == None:
            abort(404)
        song = find_song(song_id)
        song.rate_average = int(rate_average(song_id))
        return render_template('pages/song.html', song=song)

    @app.route('/song/<int:song_id>/delete', methods=['POST'])
    @requires_auth(['delete:songs'])
    def delete_song(jwt, song_id):
        song = find_song(song_id)
        message = remove_rates(song_id)
        message = remove_song(song)
        if len(request.form) == 0:
            # testing purposes
            return render_template('pages/home.html', user=None, login=None, logout=None)

        logged_user = assign_user_to_login(session['username'])
        return render_template('pages/home.html', user=logged_user, login=None, logout=None)

    @app.errorhandler(400)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 400, "message": "Not found"}),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Not found"}),
            404,
        )

    @app.errorhandler(422)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 422,
                    "message": "Unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 500,
                    "message": "Unprocessable"}),
            500,
        )

    return app
