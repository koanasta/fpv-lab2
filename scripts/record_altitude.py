#!/usr/bin/env python3
"""Записує висоту дрона з теми /odometry у CSV.

Використання (окремий термінал, паралельно з польотом):

    source ~/fpv_labs/scripts/setup_env.sh
    python3 ~/fpv_labs/scripts/record_altitude.py [файл.csv] [частота_Гц]

Колонка epoch_s — абсолютний час, той самий, що у квадратних дужках
повідомлень вузла, тому запис можна точно накласти на журнал польоту.

Потрібен, щоб підтвердити пункт 12 Завдання 3 — утримання висоти
в режимі зависання. Зупиняється по Ctrl+C.
"""

import sys
import time

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node


class AltitudeRecorder(Node):

    def __init__(self, path, rate_hz):
        super().__init__("altitude_recorder")

        self.file = open(path, "w", buffering=1)
        self.file.write("epoch_s,t_s,altitude_m\n")

        self.started_at = time.monotonic()
        self.altitude = None
        self.samples = 0

        self.create_subscription(Odometry, "/odometry", self.on_odometry, 10)
        self.create_timer(1.0 / rate_hz, self.on_tick)

        self.get_logger().info(f"Запис висоти у {path} з частотою {rate_hz} Гц")

    def on_odometry(self, message):
        self.altitude = message.pose.pose.position.z

    def on_tick(self):
        if self.altitude is None:
            return

        elapsed = time.monotonic() - self.started_at
        self.file.write(
            f"{time.time():.2f},{elapsed:.2f},{self.altitude:.4f}\n"
        )
        self.samples += 1

    def close(self):
        self.file.close()
        self.get_logger().info(f"Записано {self.samples} замірів")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "altitude.csv"
    rate = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

    rclpy.init()
    node = AltitudeRecorder(path, rate)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
