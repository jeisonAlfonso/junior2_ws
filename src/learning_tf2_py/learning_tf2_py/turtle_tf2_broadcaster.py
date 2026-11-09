import math
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from turtlesim.msg import Pose
from tf2_ros import TransformBroadcaster

def quaternion_from_euler(ai, aj, ak):
    ai /= 2.0; aj /= 2.0; ak /= 2.0
    ci, si = math.cos(ai), math.sin(ai)
    cj, sj = math.cos(aj), math.sin(aj)
    ck, sk = math.cos(ak), math.sin(ak)
    cc, cs = ci*ck, ci*sk
    sc, ss = si*ck, si*sk
    q = np.empty((4,))
    q[0] = cj*sc - sj*cs # x
    q[1] = cj*ss + sj*cc # y
    q[2] = cj*cs - sj*sc # z
    q[3] = cj*cc + sj*ss # w
    return q

def handle_pose(msg, node, broadcaster, turtlename):
    t = TransformStamped()
    t.header.stamp = node.get_clock().now().to_msg()
    t.header.frame_id = 'world'
    t.child_frame_id = turtlename

    # Translation from pose
    t.transform.translation.x = msg.x
    t.transform.translation.y = msg.y
    t.transform.translation.z = 0.0

    # Rotation: only yaw (2D turtle)
    q = quaternion_from_euler(0.0, 0.0, msg.theta)
    t.transform.rotation.x = q[0]
    t.transform.rotation.y = q[1]
    t.transform.rotation.z = q[2]
    t.transform.rotation.w = q[3]

    broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)

    node = Node('turtle_tf2_frame_publisher')

    turtlename = node.declare_parameter(
        'turtlename', 'turtle'
    ).get_parameter_value().string_value

    broadcaster = TransformBroadcaster(node)

    node.create_subscription(
        Pose,
        f'/{turtlename}/pose',
        lambda msg: handle_pose(
            msg, node, broadcaster, turtlename
        ),
        1
    )

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()