from flask import Flask, request, abort
import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from urllib.parse import parse_qs, urlparse
import requests
import http
import os


AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN', '')
ALGORITHMS = ["RS256"]
API_AUDIENCE = "song"
AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID', '')
AUTH0_CALLBACK = os.environ.get(
    'AUTH0_CALLBACK', 'http://127.0.0.1:5000/callback')
AUTH0_CLIENT_SECRET = 'aXc3paSQove4y91Qr8ya8gd2oLXddcA6HDOO28qRZLsle9tb1aJfqSnKPd8lrXAk'
AUTH0_REDIRECT = os.environ.get('AUTH0_REDIRECT', 'http://127.0.0.1:5000')
AUTH0_ALGORITHMS = 'RS256'
AUTH0_MANAGEMENT_API_TOKEN = os.environ.get('AUTH0_MANAGEMENT_API_TOKEN', '')


def get_login_url():
    return f"https://{AUTH0_DOMAIN}/authorize?audience={API_AUDIENCE}&response_type=code&response_mode=query&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK}"


def get_logout_url():
    return f"https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_REDIRECT}"


def do_logout():
    logout_url = get_logout_url()
    jsonurl = urlopen(logout_url)
    pass


def get_user_from_token(token):
    payload = verify_decode_jwt(token)
    user_id = payload['sub']
    return get_user_by_id(user_id)


def get_permissions_from_token(token):
    payload = verify_decode_jwt(token)
    if 'permissions' in payload:
        return payload['permissions']
    return 'ok2'


def get_token_from_code(url):
    # Auth0 configuration
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    param_values = query_params.get('code')
    if param_values == None:
        param_values = query_params.get('response_type')[0]

    authorization_code = param_values[0]

    # Token endpoint URL
    token_url = f'https://{AUTH0_DOMAIN}/oauth/token'

    # Request payload
    data = {
        'grant_type': 'authorization_code',
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'code': authorization_code,
        'redirect_uri': AUTH0_REDIRECT
    }

    # Send POST request to obtain the access token
    response = requests.post(token_url, data=data)

    # Process the response
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        return access_token
    else:
        print(
            f'Failed to obtain access token. Status Code: {response.status_code}, Response: {response.text}')
        # raise AuthError({
        #     'code': 'invalid_token',
        #     'description': 'Invaid token.'
        # }, 401)


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer='https://' + AUTH0_DOMAIN + '/'
                )

                return payload

            except jwt.ExpiredSignatureError:
                raise AuthError({
                    'code': 'token_expired',
                    'description': 'Token expired.'
                }, 401)

            except jwt.JWTClaimsError:
                raise AuthError({
                    'code': 'invalid_claims',
                    'description': 'Incorrect claims. Please, check the audience and issuer.'
                }, 401)
            except Exception:
                raise AuthError({
                    'code': 'invalid_header',
                    'description': 'Unable to parse authentication token.'
                }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)


def get_user_info_by_token(user_token):
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN)
    headers = {'authorization': f"Bearer {user_token}"}
    conn.request("GET", "/userinfo", headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    token = data['access_token']
    return token


def get_song_user_token():
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN)
    payload = "{\"client_id\":\"6wHrowBiT89TJisoDvnf3FLCfcQy3yoz\",\"client_secret\":\"aXc3paSQove4y91Qr8ya8gd2oLXddcA6HDOO28qRZLsle9tb1aJfqSnKPd8lrXAk\",\"audience\":\"song\",\"grant_type\":\"client_credentials\"}"
    headers = {'content-type': "application/json"}
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    token = data['access_token']
    return token


def get_admin_token():
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN)
    payload = "{\"client_id\":\"qOQgpJSXMbD13v1G1HIdp1OHz8tBfKC4\",\"client_secret\":\"-UYbPzOsmHeGkO4zY8zx7Sb2fzYdh473ZNGOD7CuA6eWTG3sB25e_KFr0SVaHDpz\",\"audience\":\"https://dev-uwcxc2qfxd26wgq8.us.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"
    headers = {'content-type': "application/json"}
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    token = data['access_token']
    return token


def get_user_by_id(user_id):
    admin_token = get_admin_token()
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN)
    headers = {'authorization': f"Bearer {admin_token}"}
    conn.request("GET", f"/api/v2/users/{user_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    user = json.loads(data)
    return user
