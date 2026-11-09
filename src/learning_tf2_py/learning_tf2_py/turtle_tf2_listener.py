import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from turtlesim.srv import Spawn

# Global state
node = None
tf_buffer = None
publisher = None
spawner = None
turtle_spawning_service_ready = False
turtle_spawned = False
spawn_future = None
target_frame = None

def on_timer():
    global turtle_spawning_service_ready
    global turtle_spawned, spawn_future
    # Step 1: Wait for spawn service
    if not turtle_spawning_service_ready:
        if spawner.service_is_ready():
            req = Spawn.Request()
            req.name = 'turtle2'
            req.x, req.y, req.theta = 4.0, 2.0, 0.0
            spawn_future = spawner.call_async(req) 
            turtle_spawning_service_ready = True
        return
    # Step 2: Wait for turtle2 to exist
    if not turtle_spawned:
        if spawn_future.done():
            turtle_spawned = True
        return
# Step 3: Lookup transform & publish velocity
    try:
        t = tf_buffer.lookup_transform(
        'turtle2', target_frame, rclpy.time.Time())
    except TransformException as ex:
        node.get_logger().info(str(ex))
        return
    msg = Twist()
    msg.angular.z = 1.0 * math.atan2(
     t.transform.translation.y,
     t.transform.translation.x)
    msg.linear.x = 0.5 * math.sqrt(
     t.transform.translation.x ** 2 +
     t.transform.translation.y ** 2)
    publisher.publish(msg)

def main(args=None):
    global node, tf_buffer
    global publisher, spawner, target_frame

    rclpy.init(args=args)

    node = Node('turtle_tf2_frame_listener')

    target_frame = node.declare_parameter(
        'target_frame', 'turtle1'
    ).get_parameter_value().string_value

    tf_buffer = Buffer()
    TransformListener(tf_buffer, node)

    publisher = node.create_publisher(
        Twist, 'turtle2/cmd_vel', 1
    )

    spawner = node.create_client(
        Spawn, 'spawn'
    )

    node.create_timer(1.0, on_timer)

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()