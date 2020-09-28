#!/usr/bin/env python

# This script loads all the images in the study.
# For each image, the map annotation is loaded and the channel name
# is set.

import sys
import argparse
import getpass

import omero
from omero.gateway import BlitzGateway

NAMESPACE = omero.constants.namespaces.NSBULKANNOTATIONS
KEY = "Channels"


def change_name(conn, image):
    for ann in image.listAnnotations():
        if ann.OMERO_TYPE == omero.model.MapAnnotationI \
           and ann.getNs() == NAMESPACE:
            channels = dict(ann.getValue()).get(KEY)
            if len(channels) > 0:
                s = channels.replace(" ", "")
                keys = dict(item.split(":") for item in s.split(";"))
                name_dict = {}
                index = 1
                for channel in image.getChannels():
                    value = channel.getName()
                    lc = channel.getLogicalChannel()
                    ew = lc.emissionWave
                    if ew is not None:
                        key = str(int(ew.getValue()))
                        if key in keys:
                            value = keys[key]

                    name_dict[index] = value
                    index += 1
                conn.setChannelNames("Image", [image.getId()], name_dict,
                                     channelCount=None)


def load_images(conn, id):
    datasets = conn.getObjects('Dataset', opts={'project': id})
    for dataset in datasets:
        for image in dataset.listChildren():
            print("image %s" % image.getId())
            change_name(conn, image)


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('id', help="The id of the project.")
    parser.add_argument('--username', default="demo")
    parser.add_argument('--server', default="localhost")
    parser.add_argument('--port', default=4064)
    args = parser.parse_args(args)
    password = getpass.getpass()
    # Create a connection
    try:
        conn = BlitzGateway(args.username, password, host=args.server,
                            port=args.port)
        conn.connect()
        load_images(conn, args.id)
    finally:
        conn.close()


if __name__ == "__main__":
    main(sys.argv[1:])
