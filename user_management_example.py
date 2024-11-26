import getopt
import sys

import requests

SHAPESPARK_ROOT_URL = 'https://cloud.shapespark.com'
USERNAME = 'api-test'
EMAIL = f'{USERNAME}@shapespark.com'
USERNAME_CHANGED = USERNAME + '-changed'
EMAIL_CHANGED = f'{USERNAME_CHANGED}@shapespark.com'

def usage():
    print("""
Demonstrates how to use Shapespark user management API.

Usage:

  %(prog)s -t PATH-TO-FILE
      -t, --token Path to a file with client authorization token.
      -h, --help Print this help.
""" % {'prog': sys.argv[0]})
    sys.exit(1)

def read_text_file(file_path):
    with open(file_path, 'r', encoding='ascii') as f:
        return f.read()

def format_error(error_response):
    status_code = error_response.status_code
    content_type = error_response.headers.get('Content-Type', '')
    if content_type.startswith('application/json'):
        error_json = error_response.json()
        api_code = error_json.get('code')
        message = error_json.get('message')
    else:
        api_code = None
        message = error_response.text
    if api_code is not None:
        return f'{status_code} ({api_code}) {message}'
    return f'{status_code} {message}'

def main():
    try:
        optlist, _ = getopt.gnu_getopt(sys.argv[1:],
                                       't:h',
                                       ['token=', 'help'])
    except getopt.GetoptError as ex:
        print('Command line arguments parsing error: ' + str(ex))
        usage()

    token_path = None

    for opt, arg in optlist:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-t', '--token'):
            token_path = arg
        else:
            assert False, 'unhandled option'


    if token_path is None:
        print('Path to the client authorization token file is missing')
        usage()

    (client_id, token) = read_text_file(token_path).split(' ')

    # Create a test user with the default subscription plan
    # (use an optional parameter 'plan' to assign another).
    data = {
        'username': USERNAME,
        'email': EMAIL,
        'onlyValidate': False,
    }
    url = f'{SHAPESPARK_ROOT_URL}/users/'
    response = requests.post(url, json=data, auth=(client_id, token))
    if response.status_code != 200:
        print('Failed to create a test user: ' + format_error(response))
    else:
        print("Test user created. User token: " + response.json()['token'])

    # Get a list of users.
    url = f'{SHAPESPARK_ROOT_URL}/users/'
    response = requests.get(url, auth=(client_id, token))
    if response.status_code != 200:
        print('Failed to get a list of users: ' + format_error(response))
    else:
        print("All users list:")
        for user in response.json():
            print("   username: {0}; email: {1}; active: {2};".
                  format(user['username'], user['email'], user['active']))

    # Deactivate the user (for example: subscription canceled).
    url = f'{SHAPESPARK_ROOT_URL}/users/{USERNAME}/deactivate'
    response = requests.post(url, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to deactivate a user: ' + format_error(response))

    # Activate the user again.
    url = f'{SHAPESPARK_ROOT_URL}/users/{USERNAME}/activate'
    response = requests.post(url, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to activate a user: ' + format_error(response))

    url = f'{SHAPESPARK_ROOT_URL}/users/{USERNAME}/change-username'
    data = {
        'username': USERNAME_CHANGED,
    }
    response = requests.post(url, json=data, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to change a username: ' + format_error(response))
    else:
        print("Test username changed.")

    url = f'{SHAPESPARK_ROOT_URL}/users/{USERNAME_CHANGED}/change-email'
    data = {
        'email': EMAIL_CHANGED,
    }
    response = requests.post(url, json=data, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to change a user email: ' + format_error(response))
    else:
        print("Test user email changed.")

    url = f'{SHAPESPARK_ROOT_URL}/users/{USERNAME_CHANGED}/change-token'
    response = requests.post(url, auth=(client_id, token))
    if response.status_code != 200:
        print('Failed to change a user token: ' + format_error(response))
    else:
        print("Test user token changed: " + response.json()['token'])

    # Get a list of scenes created by the user.
    url = f'{SHAPESPARK_ROOT_URL}/users/{USERNAME_CHANGED}/scenes/'
    response = requests.get(url, auth=(client_id, token))
    if response.status_code != 200:
        print('Failed to get a list of scenes: ' + format_error(response))
    else:
        print("All users scenes:")
        for scene in response.json():
            print("   scane name: {0}; scene url: {1};".
                  format(scene['name'], scene['sceneUrl']));

    # Delete the user.
    url = f'{SHAPESPARK_ROOT_URL}/users/{USERNAME_CHANGED}'
    response = requests.delete(url, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to delete a user: ' + format_error(response))


main()
