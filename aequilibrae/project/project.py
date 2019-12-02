import os
import sqlite3
from shutil import copyfile

from aequilibrae.project import Network
from aequilibrae.reference_files import spatialite_database
from aequilibrae import Parameters


class Project:
    """
    This is the AequilibraE project to which everything else will be related to
    """

    def __init__(self):
        self.network: Network = None
        self.file_path: str = None

    def create(self, file_path: str, overwrite=False) -> str:
        """
        To create a network, one needs to download Spatialite and add the extension
        On Windows, a great tutorial on how to do it is here:
        https://pythongisandstuff.wordpress.com/2015/11/11/python-and-spatialite-32-bit-on-64-bit-windows/
        On Linux, we still need to figure this one out
        """
        if os.path.isfile(file_path):
            if not overwrite:
                return "File exists. If you want to overwrite the file, set the flag for such"
        copyfile(spatialite_database, file_path)

        conn = sqlite3.connect(file_path)
        self.network = Network(conn)

        self.file_path = file_path

        self.network.initialize()

        return "Project created. You are on your way to become an AequilibraE Jedi!"

    def load(self, file_path: str) -> None:
        """
        This method can be used to load an AequilibraE project
        :param file_path: Path to the AequilibraE project in disk
        """
        conn = sqlite3.connect(file_path)
        self.network = Network(conn)

    def close(self, save=True):
        if save:
            self.network.conn.commit()
        self.network.conn.close()
