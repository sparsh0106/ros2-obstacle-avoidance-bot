import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math


class ObstacleAvoidance(Node):

    def __init__(self):
        super().__init__('obstacle_avoidance')

        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.latest_scan = None
        self.timer = self.create_timer(0.1, self.control_loop)

        # avoidance state
        self.mode = "forward"          # forward / turning
        self.turn_direction = 0
        self.turn_steps = 0

        self.get_logger().info("3-Phase Obstacle Avoidance Started")


    def scan_callback(self, msg):
        self.latest_scan = msg


    def valid_min(self, arr):
        vals = [x for x in arr if not math.isinf(x) and not math.isnan(x)]
        return min(vals) if vals else 8.0


    def valid_avg(self, arr):
        vals = [x for x in arr if not math.isinf(x) and not math.isnan(x)]
        return sum(vals)/len(vals) if vals else 8.0


    def control_loop(self):

        if self.latest_scan is None:
            return

        ranges = self.latest_scan.ranges

        # calibrated lidar windows
        front = self.valid_min(ranges[240:340])
        left  = self.valid_avg(ranges[340:520])
        right = self.valid_avg(ranges[60:240])

        self.get_logger().info(
            f"MODE={self.mode} Front={front:.2f} Left={left:.2f} Right={right:.2f}"
        )

        msg = Twist()

        # =========================================
        # MODE 1 : NORMAL FORWARD
        # =========================================
        if self.mode == "forward":

            if front < 0.90:
                # decide side once
                if left > right:
                    self.turn_direction = 1
                else:
                    self.turn_direction = -1

                self.mode = "turning"
                self.turn_steps = 18   # 18 * 0.1 = 1.8 sec

            else:
                msg.linear.x = 0.25
                msg.angular.z = 0.0

        # =========================================
        # MODE 2 : COMMITTED ARC TURN
        # =========================================
        elif self.mode == "turning":

            msg.linear.x = 0.08
            msg.angular.z = 0.85 * self.turn_direction

            self.turn_steps -= 1

            if self.turn_steps <= 0:
                self.mode = "forward"

        self.cmd_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidance()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
