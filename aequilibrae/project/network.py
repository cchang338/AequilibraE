import os
from aequilibrae import Parameters

# from collections import OrderedDict

""""""
"""-----------------------------------------------------------------------------------------------------------
Package:    AequilibraE
Name:       AequilibraE Network
Original Author:  Pedro Camargo (c@margo.co)
Contributors: Pedro Camargo
Last edited by: Pedro Camargo
Website:    www.AequilibraE.com
Repository:  https://github.com/AequilibraE/AequilibraE
Created:    2017-10-02
Updated:    2018-07-08
Copyright:   (c) AequilibraE authors
Licence:     See LICENSE.TXT
-----------------------------------------------------------------------------------------------------------"""


class Network:
    def __init__(self, conn):
        self.conn = conn

    def initialize(self):
        self.conn.enable_load_extension(True)

        # TODO: test how it would look like on Linux
        p = Parameters()

        aux = os.getcwd()
        os.chdir(p.spatialite_directory)
        self.conn.execute("SELECT load_extension('mod_spatialite.dll')")
        os.chdir(aux)

        qry = "D:/src/basic_science/queries_for_empty_file.sql"
        sql_file = open(qry, "r")
        query_list = sql_file.read()
        sql_file.close()
        # Split individual commands
        sql_commands_list = query_list.split("#")

        curr = self.conn.cursor()
        for cmd in sql_commands_list:
            curr.execute(cmd)
        self.conn.commit()

    def build_graph(self, mode: str):
        print("building a graph for mode X")

    def import_from_layer(self):
        pass

    def import_from_osm_polygon(self):
        pass

    def import_from_osm_place(self):
        pass

    def import_from_osm_bbox(self):
        pass
