import getopt
import sys

import requests

SHAPESPARK_ROOT_URL = 'https://cloud.shapespark.com'


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
        'username': 'api-test',
        'email': 'api-test@shapespark.com',
        'onlyValidate': False,
    }
    url = SHAPESPARK_ROOT_URL + '/users/'
    response = requests.post(url, json=data, auth=(client_id, token))
    if response.status_code != 200:
        print('Failed to create a test user: {0}, {1}'.format(
               response.status_code, response.text))
    else:
        print("Test user created. User token: " + response.json()['token'])

    # Get a list of users.
    url = SHAPESPARK_ROOT_URL + '/users/'
    response = requests.get(url, auth=(client_id, token))
    if response.status_code != 200:
        print('Failed to get a list of users: {0}, {1}'.format(
              response.status_code, response.text))
    else:
        print("All users list:")
        for user in response.json():
            print("   username: {0}; email: {1}; active: {2};".
                  format(user['username'], user['email'], user['active']))

    # Deactivate the user (for example: subscription canceled).
    url = SHAPESPARK_ROOT_URL + '/users/api-test/deactivate'
    response = requests.post(url, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to deactivate a user: {0}, {1}'.format(
              response.status_code, response.text))

    # Activate the user again.
    url = SHAPESPARK_ROOT_URL + '/users/api-test/activate'
    response = requests.post(url, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to activate a user: {0}, {1}'.format(
              response.status_code, response.text))

    url = SHAPESPARK_ROOT_URL + '/users/api-test/change-username'
    data = {
        'username': 'api-test-changed',
    }
    response = requests.post(url, json=data, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to change a username: {0}, {1}'.format(
              response.status_code, response.text))
    else:
        print("Test username changed.")

    url = SHAPESPARK_ROOT_URL + '/users/api-test-changed/change-email'
    data = {
        'email': 'api-test-changed@shapespark.com',
    }
    response = requests.post(url, json=data, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to change a user email: {0}, {1}'.format(
              response.status_code, response.text))
    else:
        print("Test user email changed.")

    url = SHAPESPARK_ROOT_URL + '/users/api-test-changed/change-token'
    response = requests.post(url, auth=(client_id, token))
    if response.status_code != 200:
        print('Failed to change a user token: {0}, {1}'.format(
              response.status_code, response.text))
    else:
        print("Test user token changed: " + response.json()['token'])

    # Get a list of scenes created by the user.
    url = SHAPESPARK_ROOT_URL + '/users/api-test-changed/scenes/'
    response = requests.get(url, auth=(client_id, token))
    if response.status_code != 200:
        print('Failed to get a list of scenes: {0}, {1}'.format(
              response.status_code, response.text))
    else:
        print("All users scenes:")
        for scene in response.json():
            print("   scane name: {0}; scene url: {1};".
                  format(scene['name'], scene['sceneUrl']));

    # Delete the user.
    url = SHAPESPARK_ROOT_URL + '/users/api-test-changed'
    response = requests.delete(url, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to delete a user: {0}, {1}'.format(
              response.status_code, response.text))


main()
