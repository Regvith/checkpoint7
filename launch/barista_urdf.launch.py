from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_prefix
import os
from launch_ros.actions import Node
from launch.substitutions import Command
def generate_launch_description():

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_bar_bot_gazebo = get_package_share_directory('barista_robot_description')

    # We get the whole install dir
    # We do this to avoid having to copy or softlink manually the packages so that gazebo can find them
    description_package_name = "barista_robot_description"
    install_dir = get_package_prefix(description_package_name)

    # Set the path to the WORLD model files. Is to find the models inside the models folder in my_box_bot_gazebo package
    gazebo_models_path = os.path.join(pkg_bar_bot_gazebo, 'models')
    # os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] =  os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] =  install_dir + "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )    
    # Define the URDF file and the package
    urdf_file = "barista_robot_model.urdf"
    package_description = "barista_robot_description"
    position =[0.0,0.0,0.2]
    orientation=[0.0,0.0,0.0]
    
    entity_name ="barista_robot-1"
    spawn_robot_node = Node(package="gazebo_ros",executable="spawn_entity.py",name="spawn_entity",output="screen",arguments=['-entity',entity_name,'-x',str(position[0]),'-y',str(position[1]),'-z',str(position[2]),'-R',str(orientation[0]),'-P',str(orientation[1]),'-Y',str(orientation[2]),'-topic','/robot_description'])
    rviz_file = "robot_model.rviz"
    rviz_path = os.path.join(get_package_share_directory(package_description),'rviz',rviz_file) 
    # Build the path to the URDF file
    urdf_path = os.path.join(get_package_share_directory(package_description), "urdf", urdf_file)
    
    # Declare the launch argument for robot_description to pass URDF path as parameter
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[{'use_sim_time': True, 'robot_description': Command(['xacro ', urdf_path])}],
        output="screen"
    )
    joint_state_publisher_node =Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="screen",
        
    )
    rviz_node = Node(package="rviz2",executable='rviz2',arguments=['-d','/home/user/ros2_ws/src/barista_robot_description/rviz/robot_model.rviz'])
    return LaunchDescription([ robot_state_publisher_node,DeclareLaunchArgument(
          'world',
          default_value=[os.path.join(pkg_bar_bot_gazebo, 'worlds', 'box_bot_empty.world'), ''],
          description='SDF world file'),
        gazebo,joint_state_publisher_node,rviz_node,spawn_robot_node])