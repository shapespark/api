# Introduction

Shapespark cloud API automates creation of WebGL 3D visualizations
with realistic, baked lighting. The API accepts a 3D model in one of
the popular formats: FBX, COLLADA, OBJ, GLTF and returns a link to a
WebGL visualization created from the model. If you would like to try
the API, get in touch with team@shapespark.com to discuss your use
case and get API access tokens.

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

+ **IES light profiles** - as with textures, can be placed in the archive
root directory or a sub-directory.

## `extras.json` format.

[Example file](./extras.json)

Entries:
### `materials` list

Sets properties of reflective materials, non-reflective materials do not need
to be included. Each entry has the following properties:

+ `name`: required, must match material name from the `FBX`.
+ `roughness`: optional, in `[0,1]` range, defaults to `1`.
+ `rougnessTexture`: optional, if set `roughness` property is ignored.
+ `metallic`: optional, in `[0,1]` range, defaults to `1`.
+ `metallicTexture`: optional, if set `metallic` property is ignored.
+ `bumpTexture`: optional.
+ `bumpScale`: used only when `bumpTexture` is set to scale it, optional,
  in [-0.2,0.2] range, defautls to `0.001`.
+ `emissionStrength`: optional, minimum value `0`, if set the
material emits light.
+ `doubleSided`: optional, boolean, defaults to `false`, use sparingly
[see the limitations of double sided.
materials](https://www.shapespark.com/docs#materials-tab)

The following material properties are read from the input FBX file,
but can be overwritten by `extras.json`:

+ `baseColor`: optional, three RGB values in `[0,1]` range, in linear
color space, defaults to `[1,1,1]`.
+ `baseColorTexture`: optional, if set `baseColor` is ignored. Can be
set to `null` to reset the base color texture setting from FBX.
+ `opacity`: optional, in `[0,1]` range, defaults to `1`.
+ `opacityForBaking`: optional, in `[0,1]` range, defaults to `opacity`,
allows to set different opacity for the baking engine, so it is for
example possible to have a fully opaque object in the scene that
doesn't block light. If set to `0`, disables lightmap for objects
with this material.

Values for `roughnessTexture`, `metallicTexture` and `bumpTexture`
are objects having properties:

+ `fileName`: required, name of the file inside the archive.
+ `importAutoScale`: optional, boolean, enables auto scale
texture resolution, defaults to `true`.
+ `importGpuCompress`: optional, boolean, enables GPU compression
formats, defaults to `true`.

[More detailed description of the material
properties](https://www.shapespark.com/docs#materials-tab).


### `views` list

An optional list of views that allow the user to teleport to points of
interest in the scene. If the `views` list is present, the first view
from the list is used as the initial camera placement after the scene
is loaded.

Each entry has the following properties:

+ `name`: optional, a user visible name of the view, defaults to 'viewX'.
+ `mode`: optional, values `"fps"` (default), `"top"`, `"orbit"`.
+ `rotation`: required, `[yaw,pitch]` of the camera in degrees.
+ `fov`: optional, field of view in degrees, in `[1,179]` range.
  View can alter the global field of view configured in the `camera` object.
  The altered field of view is used until the user teleports to another
  location in the scene.


Properties specific for `fps` views:

+ `position`: required, `[x,y,z]` coordinates of the camera,
  `z` axis is up.

Properties specific for `orbit` and `top` views:

+ `target`: required, `[x,y,z]` coordinates of the target the camera
  is looking at.
+ `distance`: required, initial distance of the camera from the target,
  greater than `0`.
+ `maxDistance`: optional, maximum distance of the camera from the target,
  greater than `0`.
+ `minUpAngle`: for `orbit` views only, optional, minimum elevation
  angle of the camera, in `[-90, 90]` range, defaults to `-90`
+ `maxUpAngle`: for `orbit` views only, optional, maximum elevation
  angle for the camera, in `[-90, 90]` range, defaults to `90`

If the list of views has more than one entry, the scene has an
automatic tour button that automatically teleports the user between
the views.


### `autoTour` object

`autoTour` is an optional object that configures the automatic tour
through all the scene views:

+ `disabled`: optional, boolean, disables the automatic tour feature, defaults to
`false`.
+ `startOnLoad`: optional, boolean, if `true` the automatic tour is started when
the scene is loaded, defaults to `false`.


### `camera` object

Sets the optional camera settings and initial camera placement. The
initial camera placement is used only if the `views` list is empty:

+ `fov`: optional, field of view in degrees in `[1,179]` range, defaults to `70`.
+ `exposure`: optional, camera exposure in `[-3,3]` range, defaults to `0`.
+ `position`: optional, `[x,y,z]` coordinates, `z` axis is up, defaults
  to the center of the scene.
+ `rotation`: optional, `[yaw,pitch]` of the camera in degrees,
  defaults to `[0,0]`.


### `lights` list

If lights are missing, ambient occlusion and sky based lighting can be
used for decent quality illumination with no configuration effort from the
user.

An entry of the `lights` list either adds a new light to the scene or sets
additional properties for a light imported from `FBX`. If a light with the
given name exists in `FBX`, all the entry properties except `name` and
`instances` are copied to the existing light. Otherwise, the entry is
treated as a new light.

Each entry has the following properties:

+ `name`: required, any unique string.
+ `type`: required for new light, `"sun"`, `"spot"`, `"point"` or `"area"`.
+ `strength`: optional, minimum value `0`, defaults to `8` for `sun`
  and `25` for all other light types.
+ `color`: optional, three RGB values in `[0,1]` range, in linear color space,
  defaults to `[1,0.8,0.638]` for `sun` and `[1.0,0.88,0.799]` for all other
  light types.
+ `angle`: for `spot` lights only, optional, in `[1,180]` range,
  defaults to `140`.
+ `photometricProfile`: for `point` and `spot` lights only, optional,
  path to IES light profile file.
+ `width` and `height`: for `area` lights only, optional, both properties in
  `[0.01,5]` range, default to `0.2`.
+ `size`: for all light types except `area`, optional, in `[0.01,0.5]` range,
  defaults to `0.02` for sun and `0.1` for all other light types.
+ `instances`: required, a list of light instances that use the settings.

Each instance has the following properties:

 + `position`: required for `spot`, `point` and `area` lights,
   `[x,y,z]` coordinates.
 + `rotation`: required for `sun`, `spot` and `area` lights, `[yaw,pitch]`.

[More detailed description of light
properties](https://www.shapespark.com/docs#lights-tab)

### `sky` object

`sky` is an optional object that can be included to change the sky
settings. If `sky` is missing, the default sky settings are used, if
`sky` is set to null, the sky is disabled.

+ `strength`: optional, `[0,100]` sky strength that is used for baking,
defaults to `6`.
+ `color`: optional, three RGB values in `[0,1]` range, in linear
color space, defaults to `[0.855,0.863,1]`.
+ `texture`: optional, an object that configures the equirectangular
sky texture that surrounds the scene. The texture is not used for
baking.

`texture` has the following properties:

+ `fileName`: required, name of the file inside the archive that
stores the sky texture.
+ `yawRotation` optional number in `[0,360]` range that specifies the
rotation of the sky texture in degrees. Defaults to `0`.

### `ambientLight` object

`ambientLight` is an optional object that configures ambient light parameters.
If `ambientLight` is missing, default ambient light is used, if `ambientLight` 
is set to null, ambient light is disabled.

The `ambientLight` object has the following properties:

+ `strength` optional, a float that specifies ambient light strength, 
defaults to `0.05`. 

### `ambientOcclusion` object

`ambientOcclusion` is an optional object that configures ambient
occlusion parameters. If `ambientOcclusion` is missing, default ambient
occlusion parameters are used, if `ambientOcclusion` is set to null,
ambient occlusion is disabled.

The `ambientOcclusion` object has the following properties:

+ `intensity` optional, a float that specifies how strong the effect
  of ambient occlusion is, defaults to `0.5`. 
+ `distance` optional, a float that specific how far to search for
  occluders, greather than `0`, defaults to `1`. For example, a `distance`
  `0.5` means that if there are no occluders within `0.5` meter from
  a given point in 3D space, the ambient occlusion has no effect on this point.

### `title` and `author`

The following settings can be used to display a title and author in the
corner of the web 3D viewer and to change the HTML page title of the web
browser tab:

+ `title`: an optional string.
+ `author`: an optional string.
+ `authorHref`: an optional string with URL that is open when the
author text is clicked, it must start with `https://` or `http://`.

### `materialPickers` list

Material pickers allow the user to replace materials in the scene with
other materials. A material picker can be triggered by a click in:

+  any existing object in the scene,
+  additional sphere or sprite objects,
+  the sliders button in the bottom right corner of the viewer which opens
   a menu with the list of all material pickers.

A material picker presents the user with a list of options to choose from.
Each option can replace multiple materials in the scene, so it is possible to
for example change floor and sofa materials with one selection.

Each entry on the `materialPickers` list has the following properties

+ `name`: required, the name of the material picker displayed in the menu.
+ `options`: required, a list of material replacements that should be
  performed after the user selects one of the option.
+ `trigger`: required, an object that configures how the material
picker is opened.

Each element in the `options` list is a list of replacement
operations. Each replacement operation has the following properties:

+ `toReplace`: required, a name of a material in the scene to be
replaced when the option is selected.
+ `toUse`: required, a name of the material that should be used instead of the `toReplace` material.

The following JSON shows an example of the options list.

```
 "options": [
     [
       {
         "toReplace": "floor wood",
         "toUse": "floor stone"
       },
       {
         "toReplace": "sofa blue",
         "toUse": "sofa red"
       }
     ],
     [
       {
         "toReplace": "floor wood",
         "toUse": "floor carpet"
       },
       {
         "toReplace": "sofa blue",
         "toUse": "sofa green"
       }
     ]
   ]
```

This configuration will show a material picker with three selection
spheres: The first sphere is for reverting the changes and applying
the original materials, it doesn't require any JSON configuration
entry. The second sphere applies the first selection option: replaces
the floor material with `floor stone` and the sofa material with `sofa
red`. The third sphere applies the second selection option: replaces
the floor material with `floor carpet` and the sofa material with
`sofa green`.

To open a material picker when an existing object in the scene is
clicked, use the following `trigger` properties:

+ `type`: `"node"`
+ `nodeType`: required, a string with the name of the object.

To open a material picker when an additional sphere in the scene is
clicked, use the following `trigger` properties:

+ `type`: `"sphere"`
+ `position`: required, `[x,y,z]` coordinates where the sphere is placed.
+ `radius`: optional, the size of the sphere, defaults to 7 centimeters.
+ `text`: optional, a short text to be displayed on the sphere. If not set a paint brush icon is displayed.

To open a material picker when a flat sprite always facing the camera
is clicked, use the following `trigger` properties:

+ `type`: `"sprite"`
+ `position`: required, `[x,y,z]` coordinates where the sprite is placed.
+ `height`: optional, the height of the sprite, defaults to 20 centimeters. The width of the sprite is set automatically to match the length of the text on the sprite.
+ `text`: optional, a text to be displayed on the sprite. If not set a paint brush icon is displayed.


### `bake` object

`bake` is an optional object that allows to control lightmap baking
quality. It has the following property:

+ `quality`: a string, one of `"draft"`, `"low"`, `"medium"`,
`"high"`, "`super`". Each setting corresponds to different lightmap
baking parameters (the number of samples, bounces and the maximum
number of lightmaps).

### `panoramas` list

`panoramas` is an optional list that allows to specify panorama images
to be generated during the scene import.

Each entry of the list corresponds to one panorama and has the following
properties:

+ `name`: required, unique, must contain only lowercase letters (`a-z`),
  digits (`0-9`) and sepearators (`_` and `-`).
+ `position`: optional, `[x,y,z]` coordinates of the panoramic camera,
  `z` axis is up, defaults to the initial camera position in the scene.
+ `rotation`: optional, yaw rotation for the initial looking direction at
  the panorama image, defaults to `0`.
+ `width`: optional, width in pixels of the panorama image, defaults to
  `8000`, minimum `100`.
+ `width`: optional, height in pixels of the panorama image, defaults to
  `4000`, minimum `100`.

Panoramas are generated in equirectangular (360x180 degree) format. The optimal
`width`:`height` aspect ratio is 2:1.

After the scene has been imported, a generated panorama can be retrieved
by a `GET` request to
`https://[USER_NAME].shapespark.com/[SCENE_NAME]/panoramas/[PANORAMA_NAME]`.
The response for the request is a JPG file containing the panorama image.

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
+ `sceneUrl` and `assetsUrl` are present only if the scene was
  successfully imported at least once.

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
+ panorama: `SCENE_ASSETS_URL + 'img/360/' + PANORAMA_NAME + '.jpg'`

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
      "password": "some password",
      "plan": "plan name",
      "onlyValidate": false
    }

Username can contain lower case letters and digits that can be
separated by `_` or `-`.

Password is optional - if password is not given logging in to the user
account interface at `https://cloud.shapespark.com/` is disabled for the
user.

If plan is not given, and the client is associated with some default
subscription plan, the default plan is automatically assigned.

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

In addition: a `plan` property is present if the user has an active plan for
a client that can assign different plans, and a `planExpirationDate` property
in YYYY-MM-DD format is present if the user has an active plan with expiration
date set.

## Activate a user.

If a subscription plan was specified when a user was created,
activating the user is not necessary. This includes the scenario
when the client using the API is associated with some default
subscription plan and the new users are automatically assigned
the default plan on creation. In such cases, activation is needed
only to re-activate a user after the user has cancelled the subscription.

Activation is performed by sending a POST request to
`https://cloud.shapespark.com/users/USERNAME/activate` with an optional
JSON object like:

    {
      "perpetual": boolean
    }

where `true` value assigns perpetual license to the user, and `false` value
assigns the default subscription plan.

Lack of JSON is equivalent to assigning the default subscription plan.

### Specifying the plan to activate

You can add a `plan` argument to the JSON object if the client doesn’t
have a default plan or to override the default plan. A plan expiration date
can be specified with an optional `planExpirationDate` argument in YYYY-MM-DD
format. If no expiration date is given the plan is assigned for indefinite
period, until it's deactiated (see below).

    {
      "plan": string,
      "planExpirationDate": "YYYY-MM-DD"
    }

#### Plan add-ons

If the plan support add-ons you can optionally specify the addons to apply in
the `planAddons` argument:

    {
      "plan": string,
      "planAddons": [
        {
          "name": string,
          "count": number
        },
        ...
      ]
    }

where `name` gives the name of the add-on and `count` specifies how many times
the add-on is applied.

## Deactivate a user

A user that cancels subscription should be deactivated with POST
request to `https://cloud.shapespark.com/users/USERNAME/deactivate`.

## Delete a user

A user can be permanently deleted with DELETE request to
`https://cloud.shapespark.com/users/USERNAME`.

*Notice:* USERNAME stays reserved for the next 30 days and cannot
be reused in this period.

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
