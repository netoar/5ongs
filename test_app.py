import unittest
from app import create_app
from model.db_config import db
import requests
from datetime import datetime
import json
from model.song import Song, create_song, find_song_by_title, remove_song
from auth import AUTH0_REDIRECT, AUTH0_DOMAIN, AUTH0_CLIENT_SECRET, AUTH0_CLIENT_ID, AUTH0_CALLBACK, AUTH0_ALGORITHMS, API_AUDIENCE, get_admin_token, get_song_user_token, get_permissions_from_token


def get_test_user_token():

    # Step 2: Authenticate the user
    token_endpoint = f'https://{AUTH0_DOMAIN}/oauth/token'
    token_data = {
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'audience': API_AUDIENCE,
        'grant_type': 'password',
        'username': 'test@songs.com',
        'password': 'H?JuM@aAiHHfCMrov3MJ',
        'scope': 'read:songs'  # Adjust the scopes as per your requirements
    }
    response = requests.post(token_endpoint, data=token_data)
    access_token = response.json()['access_token']
    return access_token


'''
'{"error":"server_error","error_description":"Authorization server not configured with default connection."}'

'''


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/songs'
        db.create_all()
        self.token = get_song_user_token()
        self.song = {'id': 12,
                     'title': 'Test Title',
                     'artist_name': 'Test Artist',
                     'date_release': '2022-05-28',
                     'date_send': '2022-05-28',
                     'rate_average': '5'}

    def tearDown(self):
        # db.drop_all()
        pass

    def test_index(self):
        response = self.client().get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_songs(self):
        response = self.client().get('/song')
        self.assertEqual(response.status_code, 200)

    def test_post_song(self):
        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
        data = {
            'title': self.song['title'],
            'artist_name': self.song['artist_name'],
            'date_release': self.song['date_release'],
            'date_send': self.song['date_send'],
            'rate_average': self.song['rate_average']
        }
        response = self.client().post('/song/create', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)

    def test_post_song_unauthorised_permissions(self):
        headers = {
            'Authorization': f"Bearer TESTTOKEN",
            'Content-Type': 'application/json'
        }
        data = {
            'title': self.song['title'],
            'artist_name': self.song['artist_name'],
            'date_release': self.song['date_release'],
            'date_send': self.song['date_send'],
            'rate_average': self.song['rate_average']
        }
        response = self.client().post('/song/create', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 401)

    def test_post_song_wrong_data(self):
        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
        data = {
            'title': self.song['title'],
            'artist_name': self.song['artist_name'],
            'date_release': self.song['date_release'],
            'date_send': self.song['date_send'],
            'rate_average': '4.5'
        }
        response = self.client().post('/song/create', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 422)

    def test_post_song_incomplete_data(self):
        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
        data = {
            'title': self.song['title'],
            'artist_name': self.song['artist_name'],
            'date_release': self.song['date_release'],
            'date_send': self.song['date_send'],
        }
        response = self.client().post('/song/create', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 422)

    def test_edit_song(self):
        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
        data = {
            'title': 'Updated Test Song 0000',
            'artist_name': 'AC/DC',
            'date_release': '2022-05-28',
            'date_send': '2022-05-28',
            'rate_average': '4'
        }

        create_song("New Song 000000", "AC/DC", "2012-04-01", "2012-04-01")
        new_song = find_song_by_title("New Song 000000")

        response = self.client().post(
            f'/song/{new_song.id}/edit', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        updated_song = find_song_by_title('Updated Test Song 0000')
        self.assertEqual(new_song.artist_name, updated_song.artist_name)
        remove_song(updated_song)

    def test_edit_song_error(self):
        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
        data = {
            'title': 'Updated Test Song 0000',
            'artist_name': 'AC/DC',
            'date_release': '2022-05-28',
            'date_send': '2022-05-28',
            'rate_average': '4'
        }

        create_song("New Song to edit", "AC/DC", "2012-04-01", "2012-04-01")
        new_song = find_song_by_title("New Song to edit")
        new_song.id = '-'

        response = self.client().post(
            f'/song/{new_song.id}/edit', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 404)
        updated_song = find_song_by_title('Updated Test Song 0000')
        self.assertEqual(new_song.artist_name, updated_song.artist_name)
        remove_song(updated_song)

    def test_display_song(self):
        create_song("New Song 000000", "AC/DC", "2012-04-01", "2012-04-01")
        new_song = find_song_by_title("New Song 000000")
        response = self.client().get(f'/song/{new_song.id}')
        self.assertEqual(response.status_code, 200)

    def test_display_song_error(self):
        response = self.client().get(f'/song/adbd')
        self.assertEqual(response.status_code, 404)

    def test_edit_song_unauthorised_permissions(self):
        headers = {
            'Authorization': f"Bearer IAMAFAKETOKEEEN",
            'Content-Type': 'application/json'
        }
        data = {
            'title': 'Updated Test Song',
            'artist_name': 'Updated Test Artist',
            'date_release': '2022-05-28',
            'date_send': '2022-05-28',
            'rate_average': '3'
        }
        response = self.client().post('/song/{}/edit'.format(self.song['id']),
                                      headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 401)

    def test_delete_song(self):
        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
        create_song("New Song 000000", "AC/DC", "2012-04-01", "2012-04-01")
        new_song = find_song_by_title("New Song 000000")

        response = self.client().post(
            f'/song/{new_song.id}/delete', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_delete_song_unauthorised_permission(self):
        headers = {
            'Authorization': f"Bearer TESTTOKEN",
            'Content-Type': 'application/json'
        }
        create_song("New Song TO delete 01", "AC/DC",
                    "2012-04-01", "2012-04-01")
        new_song = find_song_by_title("New Song TO delete 01")

        response = self.client().post(
            f'/song/{new_song.id}/delete', headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_rbac_fail(self):
        access_token = get_test_user_token()
        permissions = get_permissions_from_token(access_token)

        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
        data = {
            'title': 'SONG TITLE 0001',
            'artist_name': 'ARTIST NAME',
            'date_release': '2023-01-01',
            'date_send': '2023-01-02',
            'rate_average': 5
        }
        response = self.client().post('/song/create', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
