import os
from shutil import copyfile
from aequilibrae.project import Network
from aequilibrae.reference_files import spatialite_database
from aequilibrae import Parameters


class Project:
    """
    This is the AequilibraE project to which everything else will be related to
    """

    def __init__(self):
        self.network = Network()
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
        self.file_path = file_path

        return "Project created. You are on your way to become an AequilibraE Jedi!"

    def load(self):
        pass

    def dump(self):
        pass
