import numpy as np


class Timetable:
    """
    Class for holding a time table suitable for routing with the Connection Scan Algorithm (CSA)

    Time table holds each connection with the following info:
        Origin Stop, Destination Stop, departure time, arrival time, service ID
    Fares are implemented as a flat fare for each service boarded. Zone-based fares and fare integrations are future
    improvements

    """

    connections: np.array
    fares: np.array
    temp_timetable: list

    def __init__(self):
        self.temp_timetable = []

    def check_timetable(self) -> None:
        """
        Checks that need to be implemented:
            - Does the list of routes in the fares table match the list of routes in the timetable table?
        """
        pass

    def add_connection(self, from_stop: int, to_stop: int, departure: int, arrival: int, route_id: int):
        connection = [from_stop, to_stop, departure, arrival, route_id]

        for i in connection:
            if not isinstance(i, int):
                raise TypeError("ALL characteristics of a connection need to be integers")

        if arrival < departure:
            raise ValueError("A connection cannot arrive before it departs")

        self.temp_timetable.append(connection)

    def build_connections(self):
        dtype = np.dtype({'names': ['from', 'to', 'departure', 'arrival', 'route_id'],
                          'formats': ['i4'] * 5})

        # self.connections = np.array(zip(*self.temp_timetable), dtype)
        self.connections = np.vstack(self.temp_timetable)
        self.connections = self.connections.view(dtype)

        self.temp_timetable = []
