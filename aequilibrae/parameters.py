import os
import yaml


class Parameters:
    """
    Parameters are used in many procedures, and are often defined only in thi parameters.yml file ONLY
    Parameters are organized in the following groups:

    assignment:
    distribution:

    system:
    cpus: Maximum threads to be used in any procedure
    default_directory: If is the directory QGIS file opening/saving dialogs will try to open as standard
    driving_side: For purposes of plotting on QGIS
    logging: Level of logging to be written to temp/aequilibrae.log: Levels are those from the Python logging library
                0: 'NOTSET'
                10: 'DEBUG'
                20: 'INFO'
                30: 'WARNING'
                40: 'ERROR'
                50: 'CRITICAL'
            both numeric and text accepted
    report zeros:
    temp directory:

    """

    # def __init__(self) -> None:
    path = os.path.dirname(os.path.realpath(__file__))

    file = os.path.join(path, "parameters.yml")
    with open(file, "r") as yml:
        parameters = yaml.load(yml, Loader=yaml.SafeLoader)

    listpar = {}

    def __gather_lists(self, dictionary) -> None:
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__gather_lists(value)
            else:
                self.listpar[key] = value

    def __getattr__(self, par: str):
        if par in object.__dict__:
            return self.__dict__[par]

        self.listpar = {}
        self.__gather_lists(self.parameters)

        if par in self.listpar:
            return self.listpar[par]

        raise AttributeError("No such parameter in AequilibraE! --> {}".format(par))

    def __setattr__(self, key, value):
        # Really ugly implementation (should he recursive), but for now it suffices
        for k1, v1 in self.parameters.items():
            if isinstance(v1, dict):
                for k2, v2 in v1.items():
                    if isinstance(v2, dict):
                        for k3, v3 in v2.items():
                            if k3 == key:
                                self.parameters[k1][k2][k3] = value
                    else:
                        if k2 == key:
                            self.parameters[k1][k2] = value
            else:
                if k1 == key:
                    self.parameters[k1] = value

    def write_back(self) -> None:
        stream = open(self.path + "/parameters.yaml", "w")
        yaml.dump(self.parameters, stream, default_flow_style=False)
        stream.close()
