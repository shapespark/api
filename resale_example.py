import getopt
import getpass
import sys

import requests

SHAPESPARK_ROOT_URL = 'https://cloud.shapespark.com'


def usage():
    print("""
Demonstrates how to use Shapespark user management API for resale process.

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

    password = getpass.getpass('test-user password: ')

    # Create a test user.
    data = {
        'username': 'test-user',
        'email': 'test-user@shapespark.com',
        'password': password,
        'onlyValidate': False
    }
    url = SHAPESPARK_ROOT_URL + '/users/'
    response = requests.post(url, json=data, auth=(client_id, token))
    if response.status_code != 200:
        print('Failed to create a test user: ' + format_error(response))
    else:
        print("Test user created.")

    # Activate the user's perpetual license.
    data = {
        'perpetual': True
    }
    url = SHAPESPARK_ROOT_URL + '/users/test-user/activate'
    response = requests.post(url, json=data, auth=(client_id, token))
    if response.status_code != 204:
        print('Failed to assign perpetual license to the user: ' +
              format_error(response))

main()
