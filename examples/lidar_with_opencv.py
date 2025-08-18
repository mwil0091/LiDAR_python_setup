#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import time
import socket
import struct
import numpy as np
import matplotlib.pyplot as plt
import cv2
import cQuanergyM8 as _cq
#from quanergyM8 import Quanergy_M8_Parser, MAGIC_SIGNATURE

'''
Please refer to the "M8 Sensor User's Guide", 
   chapter 5, "Getting TCP Ethernet Packets"
'''


MAGIC_SIGNATURE = b'\x75\xbd\x7e\x97'


def _nothing_function_(_self_):
    pass


class Quanergy_M8_Parser:
    def __init__(self):
        self._prev_position = 0

        # The lasers fire at 53828 Hz.
        # If the Lidar is rotating at 10 Hz, then that's ~5383 firings per rotation.
        # With 8 lasers, and 3 returns per laser, that about 5400*3*8 points per rotation.
        #
        # BUT!:  When the lidar is first spinning up, the rotation is less than 10Hz, so
        # there's more points per rotation.  So we need some extra space in our buffers

        self.pointclouds = [
            np.empty((6500*3*8, 3), np.float32),
            np.empty((6500*3*8, 3), np.float32),
        ]
        self.intensities = [
            np.zeros((6500*3*8), np.uint8),
            np.zeros((6500*3*8), np.uint8),
        ]
        self.num_points = [0, 0]
        self.pc_idx = 0

        self.number_of_pointclouds = 0
        self.pointcloud_callback = _nothing_function_


    def parse_00(self, payload):
        assert len(payload) == 6612
        for i in range(50):
            iStart = i*132
            iStop = iStart + 132
            self.parse_firing_data(payload[iStart:iStop])
        seconds, nanoseconds, api_version, status = struct.unpack('>LLHH', payload[iStop:])
        #print("here6")
        assert api_version == 5


    def parse_firing_data(self, f_data):
        assert len(f_data) == 132
        position, = struct.unpack('>H', f_data[0:2])
        if position < self._prev_position:
            self.number_of_pointclouds += 1
            self.pointcloud_callback(self)

            self.pc_idx += 1
            if self.pc_idx > 1:
                self.pc_idx = 0
            self.num_points[self.pc_idx] = 0

        self._prev_position = position

        print('yo', self.pc_idx, self.number_of_pointclouds, self.num_points)
        #np.save('points.npy', self.pointclouds[self.pc_idx])
        pts = _cq.parse_firing_data(f_data,
                                    self.pointclouds[self.pc_idx],
                                    self.intensities[self.pc_idx],
                                    self.num_points[self.pc_idx])
        self.num_points[self.pc_idx] += pts






print("here")
if len(sys.argv) != 2:
    print('usage: %s ip_address' % (sys.argv[0]))
    sys.exit(1)

lidar_address = (sys.argv[1], 4141)


qparse = Quanergy_M8_Parser()

jet_colormap = plt.cm.jet(np.linspace(0,1,256))[:, :3]
print("here2")

_self = None

def pointcloud_callback(self):
    global ax
    global pcd
    global _self
    _self = self
    pointcloud = self.pointclouds[self.pc_idx]
    print("Saved Points")
    np.save('points.npy', self.pointclouds[self.pc_idx])
    intensities = self.intensities[self.pc_idx]
    numpoints = self.num_points[self.pc_idx]
    print(" ******* NEW Pointcloud! %0.03f %d pts" % (time.time(), numpoints))

    # These are all the points from just the horizontal laser:
    horizIdxs = np.where(pointcloud[:numpoints, 2] == 0)
    horizGrid = pointcloud[horizIdxs]

    # Flip the Y axis:
    horizGrid[:,1] = -horizGrid[:,1]

    width_px = 800
    height_px = 600
    pixels_per_meter = 50

    img = np.zeros((height_px, width_px), np.uint8)

    # center the coords:
    horizGrid[:,0] += (width_px / 2) / pixels_per_meter
    horizGrid[:,1] += (height_px / 2) / pixels_per_meter

    # convert to pixel coordinates:
    coords = np.round(horizGrid * pixels_per_meter).astype(np.uint32)

    # remove out-of-bound coordinates:
    coords = coords[  coords[:, 0] >= 0]
    coords = coords[  coords[:, 1] >= 0]
    coords = coords[  coords[:, 0] < width_px]
    coords = coords[  coords[:, 1] < height_px]

    # Remember: Y coords become "row index" and X coords become "column index":
    img[ coords[:, 1], coords[:, 0] ] = 255

    cv2.imshow('asdf', img)
    cv2.waitKey(1)
    # Convert the intensites into a Jet colormap:
    #ii = intensities[:numpoints]
    #colors = jet_colormap[ii]



qparse.pointcloud_callback = pointcloud_callback


#f = open('/data/Lidar_Capture/quanergy_capture-1.raw', 'rb')
#allData = f.read()
#f.close()
#print("expecting about ~%d packets" % (len(allData) / 6632))
print(MAGIC_SIGNATURE)
print(MAGIC_SIGNATURE[0])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 0))
print(lidar_address)
sock.connect(lidar_address)
print("here3")
while True:
    print("here4")
    ch0 = ord(sock.recv(1))
    print(ch0)
    print("here5")
    #ch0 = ord(sock.recv(1))
    #print(ch0)
    #print("here5")
    #ch0 = ord(sock.recv(1))
    #print(ch0)
    #print("here5")
    #ch0 = ord(sock.recv(1))
    #print(ch0)
    #print("here5")
    
    if ch0 == MAGIC_SIGNATURE[0]:
        ch1 = ord(sock.recv(1))
        if ch1 == MAGIC_SIGNATURE[1]:
            ch2 = ord(sock.recv(1))
            if ch2 == MAGIC_SIGNATURE[2]:
                ch3 = ord(sock.recv(1))
                if ch3 == MAGIC_SIGNATURE[3]:
                    header = sock.recv(16, socket.MSG_WAITALL)
                    size, seconds, nanoseconds, \
                    version_major, version_minor, version_patch, \
                    packet_type = struct.unpack('>IIIBBBB', header)

                    # size is either 6632 or 2224
                    # packet_type is either 0 or 4
                    print("Header")
                    print(header)
                    print(packet_type)
                    print(size)

                    if packet_type == 0 and size == 6632:
                        try:
                            pkt = sock.recv(6612, socket.MSG_WAITALL)
                            qparse.parse_00(pkt)
                        except Exception as e:
                            print(f'{e}')
                    else:
                        print('unsupported packet type: %d, %d bytes' % (packet_type, size))


