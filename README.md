# Upload format for the Shapespark API.

## Archive structure.

[Example archive](examples/cubes.zip)

The API accepts a `.zip` archive file with the following content:

+ **[any name].fbx** - the geometry and materials (optionally also lights and
the camera position).

+ **extras.json** - additional settings not included in the `FBX`.

+ **textures files** - can be placed in the archive root directory or
a sub-directory. If sub-directory is used the paths in the `FBX` and
`extras.json` needs to include the sub-directory. Preferably `.jpg`
and `.png` files but can be also `.tif`, `.bmp` and `.tga`. If
possible all lowercase texture names will reduce troubles (but not a
necessity).

## `extras.json` format.

[Example file](./extras.json)

Entries:
### `materials` list

Sets properties of reflective materials, non-reflective materials do not need
to be included. Each entry has the following properties:

+ `name`: required, must match material name from the `FBX`.
+ `roughness`: optional, in `[0,1]` range, defaults to `1`.
+ `rougnessTexture`: optional, if set `roughness` property
is ignored.
+ `metallic`: optional, in `[0,1]` range, defaults to `1`.
+ `metallicTexture`: optional, if set `metallic` property is ignored.
+ `bumpTexture`: optional.
+ `bumpScale`: optional, in `[0,1]` range, used when `bumpTexture`
  property is set to scale it.
+ `emissionStrength`: optional, in `[0,1000]` range, if set the
material emits light.

[More detailed description of `roughness`, `metallic` and
`bump`](https://www.shapespark.com/docs#materials-tab).

### `camera` object

Sets the initial camera placement (alternatively we can import the
placement from the `FBX`):

+ `position`: required, `[x, y, z]` coordinates, `z` axis is up.
+ `rotation`: required, `[yaw, pitch]` of the camera in degrees.
+ `fov`: optional, field of view in degrees.
+ `exposure`: optional, camera exposure in `[-3,3]` range, defaults to `0`.

### `lights` list

If lights are missing, we can use ambient occlusion and sky based
lighting that will give decent quality with no configuration effort
from the user.

An entry of the `lights` list either adds a new light to the scene
or sets additional properties for a light imported from `FBX`. If a light
with the given name exists in `FBX`, `size`, `strength`, `color` and `angle`
properties are copied from the entry to the existing light. Otherwise,
the entry is treated as a new light.

Each entry has the following properties:

+ `name`: required, any unique string.
+ `type`: required for new light, `sun`, `spot` or `point`.
+ `strength`: required, `[0,1000]`
+ `color`: required, three RGB values in `[0,1]` range, in linear color space.
+ `size`: required, `[0.01,0.5]`
+ `angle`: required for `spot` lights, `[0,360]`.
+ `instances`: a list of light instances that use the settings.

Each instance has the following properties:

 + `position`: required for `spot` and `point` lights, `[x, y, z]` coordinates.
 + `rotation`: required for `spot` and `sun` lights, `[yaw, pitch]`.

[More detailed description of light
properties](https://www.shapespark.com/docs#lights-tab)

### `sky` object

`sky` is an optional object that can be included to change the
default sky strength.

+ `strength`: optional, `[0,100]` sky strength that is used for baking,
defaults to 6.

# The API for importing the model.

[A script demonstrating how to use the API](scene_creation_example.py).

To import the `.zip` archive with the model three HTTP requests need to be made.

## POST import-upload-init request.

This is an HTTP POST requests to
`https://cloud.shapespark.com/scenes/[SCENE_NAME]/import-upload-init`

`SCENE_NAME` can use lowercase letters (`a-z`), digits (`0-9`) and
sepearators (`_` and `-`).

The request must include the HTTP `Authorization` header with the user
name and the secret token. The username and the token are created
during the user registration.

For testing the user name and the token from the
`Users\[USER_NAME]\AppData\Shapespark\auth` file can be used.


The result of the request is the following JSON object:


    {
      "uploadUrl": SIGNED_GOOGLE_STORAGE_BUCKET_URL
    }

## PUT request

The content of the `.zip` archive is uploaded with HTTP PUT request to
the `uploadUrl` returned by the `import-upload-init` request.

`uploadUrl` already contains signed authorization data, so no
additional authorization header is needed.

## POST import-upload-done

Last request is HTTP POST to
`https://cloud.shapespark.com/scenes/[SCENE_NAME]/import-upload-done`
The request needs to be sent after the PUT request to the Google
storage bucket finishes and instructs the server to start the import
process.

This request must also include the `Authorization` header with the
same data as the `import-upload-init` request.

The request returns a JSON:

    {
      "watchUrl": URL_TO_WAIT_FOR_THE_IMPORT_TO_FINISH
    }

The returned URL can be opened in a web browser and it will
redirect the user to the scene after the import is finished.

# The API for listing and deleting user's scenes.

## GET a list of user's scenes

GET request with the HTTP `Authorization` header that contains the
user name and the user token to `https://cloud.shapespark.com/scenes/`
returns a JSON list with items like:

    {
      "name": SCENE_NAME,
      "sceneUrl": SCENE_URL,
      "assetsUrl", SCENE_ASSETS_URL,
      "watchUrl": URL_TO_WAIT_FOR_THE_IMPORT_TO_FINISH
    }

+ `name` is always present
+ `watchUrl` is present only if the scene import is currently in progress.
+ `sceneUrl` and `assetsUrl` are present only if the scene was successfully imported at least once.

If import is being run again for the scene that already exists, the
entry will include all three: `watchUrl`, `sceneUrl` and
`assetsUrl`. As long as the `watchUrl` is present, the last import
still runs and `sceneUrl` and `assetsUrl` point to the previously
imported version of the scene. When import finishes, `watchUrl` is no
longer returned and `sceneUrl` and `assetsUrl` point to the newest
version of the scene.



`assetsUrl` can be used to access the scene:

+ 320x180 thumbnail: `SCENE_ASSETS_URL + 'thumbnail.jpg'`
+ 1920x1080 cover image: `SCENE_ASSETS_URL + 'cover.jpg'`
+ favicon: `SCENE_ASSETS_URL + 'favicon.ico'`

## DELETE a user scene

DELETE request (also with the user `Authorization` header) to
`https://cloud.shapespark.com/scenes/SCENE_NAME/` deletes a scene
created by the user.

# The API for managing users.

[A script demonstrating how to use the user management
API](user_management_example.py).

All user management request need to include the HTTP `Authorization`
header that contains a `client_id` and a `client_secret_admin_token`.

This admin token should never passed to end users, because it allows
to perform operations that affect all users.

A client is able to manage and see information only about users
created by this client.

## Create a new user.

POST request to `https://cloud.shapespark.com/users/` creates a new
user. The request needs to include a JSON like:

    {
      "username": "alice",
      "email": "alice@example.org",
      "onlyValidate": false
    }

Username can contain lower case letters and digits that can be
separated by `_` or `-`.


The result of the request is a JSON object:


    {
      "token": USER_SCENE_CREATION_TOKEN
    }

The returned token can be passed to the user's machine to allow the
user to create scenes.

The request can also return 400 error if the username or email already
exist or are invalid.

If an optional `onlyValidate` parameter is present and set to `true`,
the request doesn't create a new user, but checks if such user can be
created - the username and email are correct and not yet used. If the
user can be created the validation request returns HTTP 204 success
code, otherwise it returns 400 error code with a JSON that includes
the failure reason, like:

    {
      "message": "Username already in use"
    }


## List all users.

GET request to `https://cloud.shapespark.com/users/` lists all users
created by the client.

Each list entry contains:

    {
      "username": string,
      "email": string,
      "active": True or False
    }

## Deactivate a user.

A user that cancels subscription should be deactivated with POST
request to `https://cloud.shapespark.com/users/USERNAME/deactivate`.

If the subscription is renewed, the user can be activated again with a
POST request to `https://cloud.shapespark.com/users/USERNAME/activate`.

## Change a user scene creation token.

A POST request to
`https://cloud.shapespark.com/users/USERNAME/change-token` with an
empty body changes the user token for creating scenes. On success the
HTTP 200 code is returned together with a JSON object:

    {
      "token": NEW_USER_SCENE_CREATION_TOKEN
    }

After the request is made the previous token stops working.

## Change a user email.

A POST request to
`https://cloud.shapespark.com/users/USERNAME/change-email` changes the
user email. The request needs to include a JSON with a new email:

    {
      "email": "alice@example.org",
    }

On success the request returns HTTP 204 code. On error the request
returns 400 error code with a JSON that described the failure reason,
like:

    {
      "message": "Email already in use"
    }

## Get a list of scenes created by a user.

GET request to `https://cloud.shapespark.com/users/USERNAME/scenes/
returns a JSON list with following entries:

    {
      "name": SCENE_NAME,
      "sceneUrl": SCENE_URL
     }


## Delete a scene created by a user.

DELETE request to
`https://cloud.shapespark.com/users/USERNAME/scenes/SCENE_NAME/`
deletes a scene created by the user.
