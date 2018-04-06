# Upload format for the Shapespark API.

## Archive structure.

[Exampe archive](examples/cubes.zip)

The API will accept a `.zip` archive file with the following content:

+ **[any name].fbx** - the geometry and materials (optionally also lights and
the camera position).

+ **extras.json** - additional settings not included in the `FBX`.

+ **textures files** - can be placed in the archive root directory or
a sub-directory. If sub-directory is used the paths in the `FBX` and
`extras.json` will need to include the sub-directory. Preferably `.jpg`
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

[More detailed description of `roughness`, `metallic` and
`bump`](https://www.shapespark.com/docs#materials-tab).

### `camera` object

Sets the initial camera placement (alternatively we can import the
placement from the `FBX` if ArtiCAD exporter outputs it):

+ `position`: required, `[x, y, z]` coordinates, `z` axis is up.
+ `rotation`: required, `[yaw, pitch]` of the camera in degrees.

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