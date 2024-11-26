import getopt
import sys

import requests

SHAPESPARK_ROOT_URL = 'https://cloud.shapespark.com'

def usage():
    print("""
Import a model to Shapespark via HTTP API.

Usage:

  %(prog)s -t PATH-TO-FILE -m PATH-TO-FILE
      -m, --model Path to a .zip archive with model and textures.
      -s, --scene Name of a scene to be created (default test-scene).
      -t, --token Path to a file with user authorization token.
      -h, --help Print this help.
""" % {'prog': sys.argv[0]})
    sys.exit(1)

def read_text_file(file_path):
    with open(file_path, 'r', encoding='ascii') as f:
        return f.read()

def read_binary_file(file_path):
    with open(file_path, 'rb') as f:
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
                                       'm:t:s:h',
                                       ['model=', 'token=', 'scene=', 'help'])
    except getopt.GetoptError as ex:
        print('Command line arguments parsing error: ' + str(ex))
        usage()

    scene_name = 'test-scene'
    token_path = None
    model_path = None

    for opt, arg in optlist:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-m', '--model'):
            model_path = arg
        elif opt in ('-s', '--scene'):
            scene_name = arg
        elif opt in ('-t', '--token'):
            token_path = arg
        else:
            assert False, 'unhandled option'

    if model_path is None:
        print('Path to the .zip archive with the model is missing')
        usage()

    if token_path is None:
        print('Path to the authorization token file is missing')
        usage()

    (username, token) = read_text_file(token_path).strip().split(' ')

    url = '{0}/scenes/{1}/import-upload-init'.format(
        SHAPESPARK_ROOT_URL, scene_name)
    response = requests.post(url,auth=(username, token), verify=True)
    if response.status_code != 200:
        raise Exception('POST import-upload-init failed: ' +
                        format_error(response))

    put_url = response.json()['uploadUrl']
    data = read_binary_file(model_path)
    response = requests.put(put_url, data=data)
    if response.status_code != 200:
        raise Exception('PUT failed: {0}, {1}'.format(
            response.status_code, response.text))

    url = '{0}/scenes/{1}/import-upload-done'.format(
        SHAPESPARK_ROOT_URL, scene_name)
    response = requests.post(url,auth=(username, token), verify=True)
    if response.status_code != 200:
        raise Exception('POST import-upload-done failed: ' +
                        format_error(response))
    else:
        print('Model uploaded for import. Wait for the import to finish at {0}'
              .format(response.json()['watchUrl']))

    # Get a list of users scenes (additional permissions may be required):
    url = '{0}/scenes/'.format(SHAPESPARK_ROOT_URL)
    response = requests.get(url,auth=(username, token), verify=True)
    if response.status_code != 200:
        raise Exception('GET a list of scenes failed: ' +
                        format_error(response))

    for scene in response.json():
        print(('  Scene: {0}\n\t watchUrl: {1}\n\t sceneUrl: {2}\n\t ' +
               'assetsUrl: {3}').format(scene.get('name'),
                                        scene.get('watchUrl', 'none'),
                                        scene.get('sceneUrl', 'none'),
                                        scene.get('assetsUrl', 'none')))

main()
