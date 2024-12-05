# How to modify Gazebo World

## Prerequisites

You will need Gazebo Harmonic. If you use Ubuntu 20.04 or newer, you can follow the A4-simulation [installation gude](/README.md)
To run the gazebo, change the  follow the [usage guide](#usage) below.

If you want to install Gazebo using conda or mamba, use the following command

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
```

Then, for conda
```bash
conda install gz-sim8 gz-sim8-python libgz-sim8
```
For mamba
```bash
mamba install gz-sim8 gz-sim8-python libgz-sim8
```

## Modifying World file

The world files are located inside `a4_models` folder and they are in `SDF` format.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sdf version="1.9">
  <world name="world_name">
    ...
  </world>
</sdf>
```

Inside the `<world>` tag, there are several components, including `<plugin>`, `<gui>`, `<include>` `<model>`, etc.

To modify the objects inside the world, we will look specifically at tags `<include>` and `<model>`.
There are two ways you can add objects,

1. Including model inside the `a4_models/models` folder using `<include>` tag.

    For example:
    ```xml
    <include>
      <uri>model://nathan_benderson_park</uri>
      <pose> 0 0 -1.0 0 0 0 </pose>
      <name>park</name>
    </include>
    ```
    This object will include a model named `nathan_benderson_park` at position `z=-1`, which is the 3D model of [Nathan Benderson Park](https://maps.app.goo.gl/n538a7Xo8bnExpur7).

    You can generate a new model or import existing model to `a4_models/models`. One of the available resources to find Gazebo models is from [Gazebo Fuel](https://app.gazebosim.org/dashboard).

2. Creating a model directly inside the world using `<model>` tag.

    You can create a basic geometry, like box and cylinder using the `<model>` tag. The explanation about the `<model>` tag is below.


### Creating a model

A model tag has an attribute `name`. If you creating a model SDF file inside `a4_models/models` folder, make sure the name of the model is same with the model folder name.

Inside, they have several children tags:
- `<pose>X Y Z r p y</pose>`: This tag determine the position and pose of the model (x, y, z, roll, pitch, yaw)
- `<static>true/false</static>`: Determining if the object is static (cannot be moved) or not.
    - However if you set the `static` to be `false`, you need to input the `<intertial>` information.
- `<link> ... </link>`: Consider the link as the actual object. There can be several links, and they can be connected using `<joint>`. For simplification, consider only one link.

Inside the `<link>`, there are three types of children tags:
- `<inertial>`: Containing mass and interitial data of the link. If you set it to `static`, you can omit this tag.
- `<collision>`: Containing the geometry of the physical presence inside simulation. It define the collision area of the object
- `<visual>`: Containing the appearance geometry shown in the Gazebo.

For `real` object, usually we set `<collision>` and `<visual>` to be identical.

But if you want to create a virtual object (cannot be collided by vehicles), you can omit the `<collision>` tag.

Take a look for an example of box model below.
```xml
<model name="my_model">
    <pose>0 0 0.5 0 0 0</pose>
    <static>true</static>
    <link name="link">

        <!-- Intertial information (If static is false) -->
        <inertial>
            <mass>1.0</mass>
            <inertia> <!-- inertias are tricky to compute -->
                <ixx>0.083</ixx>       <!-- for a box: ixx = 0.083 * mass * (y*y + z*z) -->
                <ixy>0.0</ixy>         <!-- for a box: ixy = 0 -->
                <ixz>0.0</ixz>         <!-- for a box: ixz = 0 -->
                <iyy>0.083</iyy>       <!-- for a box: iyy = 0.083 * mass * (x*x + z*z) -->
                <iyz>0.0</iyz>         <!-- for a box: iyz = 0 -->
                <izz>0.083</izz>       <!-- for a box: izz = 0.083 * mass * (x*x + y*y) -->
            </inertia>
        </inertial>

        <!-- Physical presence for collision calculation -->
        <collision name="collision">
            <geometry>
                <box>
                    <size>1 1 1</size>
                </box>
            </geometry>
        </collision>

        <!-- Actual appearance on Gazebo -->
        <visual name="visual">
            <geometry>
                <box>
                    <size>1 1 1</size>
                </box>
            </geometry>
        </visual>

    </link>
</model>
```

### Several simple geometries

- Box
    ```xml
    <box>
        <size>Length Width Height</size>
    </box>
    ```

- Cylinder
    ```xml
    <cylinder>
        <radius>Radius</radius>
        <length>Height</length>
    </cylinder>
    ```
    By default, the cylinder is upright (height is upside). If you want to create a horizontal cylinder, you can either modify `<pose>` of the model, or you can append additional `<pose>` tag under `<link>`

- Sphere
    ```xml
    <sphere>
        <radius>Radius</radius>
    </sphere>
    ```

- Plane
    ```xml
    <plane>
        <normal>NX NY NZ</normal>
        <size>Length Width</size>
    </plane>
    ```
    `NX`, `NY`, `NZ` is the normal direction of the plane. For horizontal plane: `<normal>0 0 1</normal>`

- Cone
    ```xml
    <cone>
        <radius>Radius</radius>
        <length>Length</length>
    </cone>
    ```

### Programmatically appending objects inside the world file

To programmatically add new objects inside the world, you can use this logic.
- Read a world file and find `<include>` of `<model>` tags inside the world file.
- Keep all text from the first line until before the first `<include>` or `<model>` tag as `header` string
- Keep the text from the first `<include>` or `<model>` until the last line as `footer` string
- Using your code, generate the `<model> ... </model>` strings as much as you like.
- Using the code, create a new text file inside `a4_models/worlds` by appending `header`, `model`, and `footer` strings.
- To test, launch the Gazebo using method below.

## Opening world file with Gazebo

### Option 1: Docker

If you use docker, run the gazebo of your modified world by first change the `command:` on [docker-compose.yml](/docker-compose.yml) to
```bash
command: bash -c "GZ_SIM_RESOURCE_PATH=/root/a4_models/models gz sim -v -r /root/a4_models/worlds/<world_name>.sdf"
```
Change `<world_name>` with the appropriate SDF file name to load.

Then build and launch Gazebo using the following command
```bash
docker compose up --build
```


### Option 2: Conda/Mamba

If you use conda/mamba, run the Gazebo using command

```bash
GZ_SIM_RESOURCE_PATH=<model_root>/models gz sim -v -r <model_root>/worlds/<world_name>.sdf
```
Change `<model_root>` to the `a4_models` folder path and `<world_name>` with the appropriate SDF file name to load.
