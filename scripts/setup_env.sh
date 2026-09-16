#!/bin/bash
# Common environment for lab 2. Source it, do not execute it:
#   source ~/fpv_labs/scripts/setup_env.sh
#
# Sourcing ardu_ws/install/setup.bash also runs the ament environment
# hooks of ardupilot_gazebo, which set GZ_SIM_RESOURCE_PATH,
# GZ_SIM_PLUGIN_PATH and SDF_PATH automatically.

export GZ_VERSION=harmonic
export PATH=$HOME/ardu_ws/Micro-XRCE-DDS-Gen/scripts:$PATH

source /opt/ros/jazzy/setup.bash
source $HOME/ardu_ws/install/setup.bash

if [ -f "$HOME/fpv_labs/install/setup.bash" ]; then
    source $HOME/fpv_labs/install/setup.bash
fi

# The lidar model lives in ardupilot_gz_description, whose hooks only set
# GZ_SIM_RESOURCE_PATH. libsdformat (used by robot_state_publisher) resolves
# model:// through SDF_PATH, so it is added explicitly here.
export SDF_PATH=$SDF_PATH:$HOME/ardu_ws/install/ardupilot_gz_description/share/ardupilot_gz_description/models
