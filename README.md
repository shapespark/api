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
+ `doubleSided`: optional, defaults to `false`, use sparingly
[see the limitations of double sided.
materials](https://www.shapespark.com/docs#materials-tab)


The following material properties are read from the input FBX file,
but can be overwritten by `extras.json`:

+ `baseColor`: optional, three RGB values in `[0,1]` range, in linear
color space.
+ `baseColorTexture`: optional, if set `baseColor` is ignored. Can be
set to `null` to reset the base color texture setting from FBX.
+ `opacity`: optional, in `[0, 1]` range.

[More detailed description of the material
properties](https://www.shapespark.com/docs#materials-tab).

### `views` list

An optional list of views that allow the user to teleport to points of
interest in the scene. If the `views` list is present, the first view
from the list is used as the initial camera placement after the scene
is loaded.

Each entry has the following properties:

+ `name`: optional, a user visible name of the view, defaults to 'viewX'.
+ `position`: required, `[x, y, z]` coordinates of the camera, `z` axis is up.
+ `rotation`: required, `[yaw, pitch]` of the camera in degrees.

If the list of views has more than one entry, the scene has an
automatic tour button that automatically teleports the user between
the views.

### `autoTour` object

`autoTour` is an optional object that configures the automatic tour
through all the scene views:

+ `disabled`: optional, disables the automatic tour feature, defaults to
`false`.
+ `startOnLoad`: optional, if `true` the automatic tour is started when
the scene is loaded, defaults to `false`.

### `camera` object

Sets the optional camera settings and initial camera placement. The
initial camera placement is used only if the `views` list is empty:

+ `fov`: optional, field of view in degrees.
+ `exposure`: optional, camera exposure in `[-3,3]` range, defaults to `0`.
+ `position`: optional, `[x, y, z]` coordinates, `z` axis is up.
+ `rotation`: optional, `[yaw, pitch]` of the camera in degrees.

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
+ `type`: required for new light, `"sun"`, `"spot"` or `"point"`.
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

`sky` is an optional object that can be included to change the sky
settings. If `sky` is missing, the default sky settings are used, if
`sky` is set to null, the sky is disabled.

+ `strength`: optional, `[0,100]` sky strength that is used for baking,
defaults to `6`.
+ `color`: optional, three RGB values in `[0,1]` range, in linear
color space, defaults to `[ 0.855, 0.863, 1]`.
+ `ambientOcclusion`: optional, an object that configures ambient
occlusion parameters. If `ambientOcclusion` is missing, default ambient
occlusion parameters are used, if `ambientOcclusion` is set to null,
ambient occlusion is disabled.
+ `texture`: optional, an object that configures the equirectangular
sky texture that surrounds the scene. The texture is not used for
baking.

`ambientOcclusion` has the following properties:

+ `factor` optional, a float that specifies how strong is the effect
of ambient occlusion, defaults to `0.05`. `0` is an equivalent of
disabled ambient occlusion.
+ `distance` optional, a float that specific how far to search for
occluders, defaults to `1`. For example, a `distance` `0.5` means that
if there are no occluders within `0.5` meter from a given point in 3D
space, the ambient occlusion has no effect on this point.

`texture` has the following properties:

+ `fileName`: required name of the file inside the zip package that
stores the sky texture.
+ `yawRotation` optional number in `[0, 360]` range that specifies the
rotation of the sky texture in degrees. Defaults to `0`.

### `bake` object

`bake` is an optional object that allows to control lightmap baking
quality. It has the following property:

+ `quality`: a string, one of `"draft"`, `"low"`, `"medium"`,
`"high"`, "`super`". Each setting corresponds to different lightmap
baking parameters (the number of samples, bounces and the maximum
number of lightmaps).

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
      "password": "some password"
      "onlyValidate": false
    }

Username can contain lower case letters and digits that can be
separated by `_` or `-`.

Password is optional - if password is not given logging in to the user
account interface at `https://cloud.shapespark.com/` is disabled for the
user.

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
      "active": true or false
    }

## Activate a user.

If the client using the API is associated with some default subscription
plan then activating newly created users is not necessary, because they
are automatically assigned the default plan on creation. In this case
activation is needed only to re-activate a user after the user has
canceled the subscription.

Activation is performed by sending a POST request to
`https://cloud.shapespark.com/users/USERNAME/activate` with an optional
JSON object like:

    {
      "perpetual": boolean
    }

where `true` value assigns perpetual license to the user, and `false` value
assigns the default subscription plan.

Lack of JSON is equivalent to assigning the default subscription plan.

## Deactivate a user

A user that cancels subscription should be deactivated with POST
request to `https://cloud.shapespark.com/users/USERNAME/deactivate`.

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
