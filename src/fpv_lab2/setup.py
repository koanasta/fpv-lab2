from setuptools import find_packages, setup

package_name = "fpv_lab2"

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="kobri",
    maintainer_email="kobri@todo.todo",
    description="Lab 2: ArduPilot SITL + Gazebo + ROS 2 flight control",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "flight_test = fpv_lab2.flight_test.main:main",
            "goto_point = fpv_lab2.goto_point.main:main",
        ],
    },
)
