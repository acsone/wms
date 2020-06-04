# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os

import shapefile

"""
This script is used to generate the content of the 'ressources/' directory.
The files in the ressources are used for th test_shape_file_import_wizard.py.
If you need to generate more files, he can use this script as an example.
"""

current_dir = os.getcwd()
if not os.path.exists("ressources"):
    os.mkdir("ressources")
path = current_dir + "/ressources/"
number_of_files = 5

# GENERATE FILES


for i in range(1, number_of_files + 1):
    file_name = "shape_test_%s" % i
    path_to_file = os.path.join(path, file_name)
    file_name_shp = path_to_file + ".shp"
    file_name_dbf = path_to_file + ".dbf"
    file_name_shx = path_to_file + ".shx"

    w = shapefile.Writer(path_to_file)
    w.field(
        "Nom", "C"
    )  # First part of field: the name of the field. Second one, the type : here a char field
    if i == 1:
        w.poly(
            [
                [
                    [3.438298, 50.817468],
                    [3.164077, 50.769786],
                    [3.163794, 50.770435],
                    [3.163739, 50.77049],
                    [3.163442, 50.770792],
                ]
            ]
        )  # Create a polygon
    elif i == 2:
        w.poly(
            [
                [
                    [3.163115, 50.771132],
                    [3.162636, 50.771532],
                    [3.162174, 50.771985],
                    [3.161905, 50.77222],
                    [3.161752, 50.772353],
                ]
            ]
        )  # Create a polygon

    elif i == 3:
        w.poly(
            [
                [
                    [3.161379, 50.772704],
                    [3.161141, 50.772993],
                    [3.160944, 50.77323],
                    [3.160742, 50.773397],
                    [3.160505, 50.773537],
                ]
            ]
        )  # Create a polygon
    elif i == 4:
        w.poly(
            [
                [
                    [3.160236, 50.773646],
                    [3.159792, 50.773865],
                    [3.159381, 50.774203],
                    [3.158849, 50.774653],
                    [3.158796, 50.774698],
                ]
            ]
        )  # Create a polygon
    elif i == 5:
        w.poly(
            [
                [
                    [3.158221, 50.775139],
                    [3.157784, 50.775493],
                    [3.158007, 50.775621],
                    [3.157985, 50.775747],
                    [3.157803, 50.775985],
                ]
            ]
        )  # Create a polygon
    else:
        w.poly(
            [
                [
                    [3.157493, 50.776306],
                    [3.157075, 50.776594],
                    [3.156601, 50.777019],
                    [3.156126, 50.777434],
                    [3.155595, 50.777824],
                ]
            ]
        )  # Create a polygon

    w.record("D%s" % i)  # Name of the polygon D1, D2, ...
    w.close()
