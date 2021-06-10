ROSbag Image Slicer
==============================

This ROS package, known as `rosbag_image_slicer`, provides a python parsing approach for taking in a target ROSbag and outputting a bag containing the designated video topic cropped to a specified cropping ratio at a specified location in the image.

## Setup
Create a catkin workspace (e.g. rosbag_ws)
```bash
$ mkdir rosbag_ws
```
Create a src folder in new workspace
```bash
$ cd rosbag_ws
$ mkdir src
```
Clone this git repository into the src folder
```bash
$ cd src
$ git clone https://github.com/haydenm2/rosbag_image_slicer.git
```
Clone the fizyr-forks vision_opencv from https://github.com/fizyr-forks/vision_opencv.git into the src folder
```bash
$ cd src
$ git clone https://github.com/fizyr-forks/vision_opencv.git
```
In the catkin workspace run the catkin make command from the workspace folder (e.g. rosbag_ws) with the following flags (replacing "python3.8" with the applicable python 3 version installed on your system)
```bash
$ cd ..
$ catkin_make -DPYTHON_EXECUTABLE=$(which python3) -DPYTHON_INCLUDE_DIR=/usr/include/python3.8 -DPYTHON_LIBRARY=/usr/lib/python3.8/config-3.8-x86_64-linux-gnu/libpython3.8.so
```
Then source the workspace
```bash
$ source devel/setup.bash
```

## Cropping Through Python Parsing
The python parsing script directly parses a given ROSbag file on a specified image topic. It can be run with the following command:

```bash
$ cd /<path_to_workspace>/src/rosbag_image_slicer/scripts
$ python parse_slice.py -o '/<desired_output_rosbag_path>/<output_rosbag_name>.bag' -t '<video_rostopic_name>' -i '/<path_to_input_rosbag>/<input_rosbag_name>.bag' -r <resolution_resize_ratio> -v <vertical_section (optional)> -h <horizontal_section (optional)> -p <passthrough_topics (optional)> -c <camera_info_topic (optional)>
```
In general the following flags indicate:
`-o` = Output ROSbag path
`-i` = Input ROSbag path
`-t` = Input ROSbag image topic to crop
`-r` = Cropping ratio (e.g. -r 0.5 will result an output image of half the pixels on each axis. Thus, a 4000x3000 image will be cropped to 2000x1500).
`-v` = Vertical cropping section alignment (top, middle, or bottom) (e.g. -v "left" will crop the desired section as far to the left as possible and -v "middle" will attempt to crop around the vertical middle of the image)
`-h` = Horizontal cropping section alignment (left, center, right) (e.g. -h "top" will crop the desired section as far to the top as possible and -h "center" will attempt to crop around the horizontal center of the image)
`-p` = Input ROSbag topics to pass through to the next ROSbag (must be seperated by spaces) (e.g. /gps /imu /gpstime)
`-c` = ROSbag camera info topic to adjust with crop reduction




