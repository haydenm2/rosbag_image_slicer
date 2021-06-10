#!/usr/bin/env python3

import sys, getopt
import rosbag
import cv2
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge, CvBridgeError


def main(argv):
    # initialization variables
    init = True
    vertical_selected = False
    horizontal_selected = False
    passthrough_selected = False
    camera_info_selected = False

    # input argument parsing
    try:
        opts, args = getopt.getopt(argv, "i:o:t:r:v:h:p:c:",
                                   ["ifile=", "ofile=", "topic=", "ratio=", "vertical=", "horizontal=", "passthrough=",
                                    "cam_info_topic="])
    except getopt.GetoptError:
        print('parse_reduce.py -i <input_bag_path> -o <output_bag_path> -t <image_topic> -r <crop_ratio> -v <vertical_section(optional)> -h <horizontal_section(optional)> -p <passthrough_topics(optional)> -c <camera_info_topic(optional)>')
        print('vertical_selection options: top, middle, bottom')
        print('horizontal_selection options: left, center, right')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            in_bag_name = arg
        elif opt in ("-o", "--ofile"):
            out_bag_name = arg
        elif opt in ("-t", "--topic"):
            img_topic = arg
        elif opt in ("-r", "--ratio"):
            crop_ratio = float(arg)
        elif opt in ("-v", "--vertical"):
            vertical_section = arg
            vertical_selected = True
        elif opt in ("-h", "--horizontal"):
            horizontal_section = arg
            horizontal_selected = True
        elif opt in ("-p", "--passthrough"):
            passthrough_topic_inputs = arg
            passthrough_topics = passthrough_topic_inputs.split()
            passthrough_selected = True
        elif opt in ("-c", "--cam_info_topic"):
            cam_info_topic = arg
            camera_info_selected = True

    # validate input arguments -------------------------------------------------
    try:
        in_bag_name
    except NameError:
        print("\033[1;31m ERROR: Must define input bag path! \033[0;0m")
        print('parse_reduce.py -i <inputbagpath> -o <outputbagpath> -t <imagetopic> -r <cropratio>')
        sys.exit(2)
    else:
        print("\033[1;33m Input Bag: \033[0;0m %s" % in_bag_name)

    try:
        out_bag_name
    except NameError:
        print("\033[1;31m ERROR: Must define output bag path! \033[0;0m")
        print('parse_reduce.py -i <inputbagpath> -o <outputbagpath> -t <imagetopic> -r <cropratio>')
        sys.exit(2)
    else:
        print("\033[1;33m Output Bag: \033[0;0m %s" % out_bag_name)

    try:
        img_topic
    except NameError:
        print("\033[1;31m ERROR: Must define image topic! \033[0;0m")
        print('parse_reduce.py -i <inputbagpath> -o <outputbagpath> -t <imagetopic> -r <cropratio>')
        sys.exit(2)
    else:
        print("\033[1;33m Image Topic: \033[0;0m %s" % img_topic)

    try:
        crop_ratio
    except NameError:
        print("\033[1;31m ERROR: Must define desired crop ratio! \033[0;0m")
        print('parse_reduce.py -i <inputbagpath> -o <outputbagpath> -t <imagetopic> -r <cropratio>')
        sys.exit(2)
    else:
        print("\033[1;33m Crop Ratio: \033[0;0m %s" % crop_ratio)

    if in_bag_name[-4:] != ".bag":
        print("\033[1;31m ERROR: Input bag path must be in .bag format \033[0;0m")
        sys.exit(2)

    if out_bag_name[-4:] != ".bag":
        print("\033[1;31m ERROR: Output bag path must be in .bag format \033[0;0m")
        sys.exit(2)

    # --------------------------------------------------------------------------
    # USER INPUT OF CROP LOCATIONS
    while not vertical_selected:
        vertical_section = input('Type vertical cropping section (top/middle/bottom): ')
        if vertical_section == "top" or vertical_section == "middle" or vertical_section == "bottom":
            vertical_selected = True
        else:
            print("\033[1;31m ERROR: Invalid selection, try again. \033[0;0m")

    while not horizontal_selected:
        horizontal_section = input('Type horizontal cropping section (left/center/right): ')
        if horizontal_section == "left" or horizontal_section == "center" or horizontal_section == "right":
            horizontal_selected = True
        else:
            print("\033[1;31m ERROR: Invalid selection, try again. \033[0;0m")

    # USER INPUT OF PASSTHROUGH TOPICS
    if not passthrough_selected:
        passthrough_topic_inputs = input(
            'Type list of additional topics to pass through to new bag (separate with spaces): ')
        passthrough_topics = passthrough_topic_inputs.split()

    in_bag = rosbag.Bag(in_bag_name)
    out_bag = rosbag.Bag(out_bag_name, 'w')

    # progress readout parameters
    t_begin = in_bag.get_start_time()
    t_end = in_bag.get_end_time()
    t_total = t_end - t_begin

    # CvBridge init
    bridge = CvBridge()

    img_h_reduced = 0
    img_w_reduced = 0

    print("\033[1;32m PARSING", img_topic, "DATA                                 \033[0;0m")
    # iterate through incoming bag
    for topic, msg, t in in_bag.read_messages(topics=[img_topic]):
        if crop_ratio == 1.0:
            out_bag.write(img_topic, msg, t=t)

            # print progress percentage
            print('\033[1;31m Percent Complete: \033[0;0m', (((t.to_sec() - t_begin) / t_total) * 100), end='\r')
            sys.stdout.flush()
            continue

        input_image = msg
        image_encoding = input_image.encoding

        # convert to Cv format for reduction
        try:
            cv_image = bridge.imgmsg_to_cv2(input_image, image_encoding)
        except CvBridgeError as e:
            print(e)
            sys.exit(2)

        # initialize reduced image params
        if init:
            img_h_reduced = int(cv_image.shape[0] * crop_ratio)
            img_w_reduced = int(cv_image.shape[1] * crop_ratio)

            if vertical_section == "top":
                img_h_start = 0
            elif vertical_section == "middle":
                img_h_start = int((cv_image.shape[0] - img_h_reduced) / 2.0)
            elif vertical_section == "bottom":
                img_h_start = int(cv_image.shape[0] - img_h_reduced)

            if horizontal_section == "left":
                img_w_start = 0
            elif horizontal_section == "center":
                img_w_start = int((cv_image.shape[1] - img_w_reduced) / 2.0)
            elif horizontal_section == "right":
                img_w_start = int(cv_image.shape[1] - img_w_reduced)

        cv_image_cropped = cv_image[img_h_start:img_h_start + img_h_reduced, img_w_start:img_w_start + img_w_reduced]

        # convert back to ROS format and write to bag
        image_new = bridge.cv2_to_imgmsg(cv_image_cropped, image_encoding)
        out_bag.write(img_topic, image_new, t=t)

        # print progress percentage
        print('\033[1;31m Percent Complete: \033[0;0m', (((t.to_sec() - t_begin) / t_total) * 100), end='\r')
        sys.stdout.flush()

    if camera_info_selected:
        print("\033[1;32m PARSING", cam_info_topic, "DATA                                \033[0;0m")
        # iterate through camera info topic
        for topic, msg, t in in_bag.read_messages(topics=[cam_info_topic]):
            if (crop_ratio == 1.0):
                out_bag.write(cam_info_topic, msg, t=t)

                # print progress percentage
                print('\033[1;31m Percent Complete: \033[0;0m', (((t.to_sec() - t_begin) / t_total) * 100), end='\r')
                sys.stdout.flush()
                continue

            cam_info = msg
            K_adjusted = (
            cam_info.K[0], cam_info.K[1], img_w_reduced / 2.0, cam_info.K[3], cam_info.K[4], img_h_reduced / 2.0, cam_info.K[6], cam_info.K[7], cam_info.K[8])

            # convert back to ROS format and write to bag
            cam_info_new = cam_info
            cam_info_new.height = img_h_reduced
            cam_info_new.width = img_w_reduced
            cam_info_new.K = K_adjusted
            out_bag.write(cam_info_topic, cam_info_new, t=t)

            # print progress percentage
            print('\033[1;31m Percent Complete: \033[0;0m', (((t.to_sec() - t_begin) / t_total) * 100), end='\r')
            sys.stdout.flush()

    # TRANSFER PASSTHROUGH TOPICS
    for pass_topic in passthrough_topics:
        print("\033[1;32m TRANSFERRING", pass_topic, "DATA                                \033[0;0m")
        for topic, msg, t in in_bag.read_messages(topics=[pass_topic]):
            out_bag.write(pass_topic, msg, t=t)

            # print progress percentage
            print('\033[1;31m Percent Complete: \033[0;0m', (((t.to_sec() - t_begin) / t_total) * 100), end='\r')
            sys.stdout.flush()

    # completion printout and bag closures
    print("\n\033[1;32m Rosbag Image Cropping Complete! \033[0;0m")
    print("Output bag: %s \n" % out_bag_name)

    out_bag.close()
    in_bag.close()


if __name__ == "__main__":
    main(sys.argv[1:])
