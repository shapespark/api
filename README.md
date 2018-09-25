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
+ `roughness`: optional, in `[0-1]` range, defaults to `1`.
+ `rougnessTexture`: optional, if set `roughness` property
is ignored.
+ `metallic`: optional, in `[0-1]` range, defaults to `1`.
+ `metallicTexture`: optional, if set `metallic` property is ignored.
+ `bumpTexture`: optional.
+ `bumpScale`: optional, in `[0-1]` range, used when `bumpTexture`
  property is set to scale it.
+ `emissionStrength`: optional, in `[0-1000]` range, if set the
material emits light.

[More detailed description of `roughness`, `metallic` and
`bump`](https://www.shapespark.com/docs#materials-tab).

### `camera` object

Sets the initial camera placement (alternatively we can import the
placement from the `FBX`):

+ `position`: required, `[x, y, z]` coordinates, `z` axis is up.
+ `rotation`: required, `[yaw, pitch]` of the camera in degrees.
+ `fov`: optional, field of view in degrees.

### `lights` list

If lights are missing, we can use ambient occlusion and sky based
lighting that will give decent quality with no configuration effort
from the user.

Light `type`, `position` and `rotation` can be imported from `FBX`, if
you prefer such solution only `size`, `strength`, `color` and `angle`
(for spot lights) would need to be passed via `extras.json`.

Each entry has the following properties:

+ `name`: required, any unique string.
+ `type`: required, `sun`, `spot` or `point`.
+ `strength`: required, [0-1000]
+ `color`: required, three RGB values in [0-1] range, in linear color space.
+ `angle`: required for `spot` lights, [0-360].
+ `instances`: a list of light instances that use the settings.

Each instance has the following properties:

 + `position`: required for `spot` and `point` lights, `[x, y, z]` coordinates.
 + `rotation`: required for `spot` and `sun` lights, `[yaw, pitch]`.

[More detailed description of light
properties](https://www.shapespark.com/docs#lights-tab)

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

# The API for listing and deleting user's scenes.

## GET a list of user's scenes

GET request with the HTTP `Authorization` header that contains the
user name and the user token to `https://cloud.shapespark.com/scenes/`
returns a JSON list with

    {
      "name": SCENE_NAME,
      "sceneUrl": SCENE_URL
    }

entries that list all the scenes created by the user.

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
      "email": "alice@example.org"
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

## List all users.

GET request to `https://cloud.shapespark.com/users/` lists all users
created by the client.

Each list entry contains:

    {
      "username": string,
      "active": True or False
    }

## Deactivate a user.

A user that cancels subscription should be deactivated with POST
request to `https://cloud.shapespark.com/users/USERNAME/deactivate`.

If the subscription is renewed, the user can be activated again with a
POST request to `https://cloud.shapespark.com/users/USERNAME/activate`.

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
