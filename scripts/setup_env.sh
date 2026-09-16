#!/bin/bash

export GZ_VERSION=harmonic
export PATH=$HOME/ardu_ws/Micro-XRCE-DDS-Gen/scripts:$PATH

source /opt/ros/jazzy/setup.bash
source $HOME/ardu_ws/install/setup.bash

if [ -f "$HOME/fpv_labs/install/setup.bash" ]; then
    source $HOME/fpv_labs/install/setup.bash
fi

export SDF_PATH=$SDF_PATH:$HOME/ardu_ws/install/ardupilot_gz_description/share/ardupilot_gz_description/models
