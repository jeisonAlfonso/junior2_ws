from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


ARGUMENTS = [
    DeclareLaunchArgument(
        name='gui',
        default_value='true',
        choices=['true', 'false'],
        description='Flag to enable joint_state_publisher_gui'
    ),

    DeclareLaunchArgument(
        name='model',
        default_value=PathJoinSubstitution([
            get_package_share_directory('jackal_description'),
            'urdf',
            'jackal.urdf.xacro'
        ])
    ),

    DeclareLaunchArgument(
        name='lidar_model',
        default_value='hokuyo',
        choices=['hokuyo', 'velodyne', 'none'],
        description='LIDAR montado sobre el Jackal'
    ),
]


def generate_launch_description():
    ld = LaunchDescription(ARGUMENTS)

    ld.add_action(
        IncludeLaunchDescription(
            PathJoinSubstitution([
                FindPackageShare('urdf_launch'),
                'launch',
                'display.launch.py'
            ]),
            launch_arguments={
                'urdf_package': 'jackal_description',
                # urdf_launch corre "xacro <ruta>", asi que el argumento de xacro
                # va pegado a la ruta del modelo.
                'urdf_package_path': [
                    LaunchConfiguration('model'),
                    ' lidar_model:=',
                    LaunchConfiguration('lidar_model'),
                ],
                'jsp_gui': LaunchConfiguration('gui')
            }.items()
        )
    )

    return ld