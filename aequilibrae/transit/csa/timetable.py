import numpy as np


class Timetable:
    """
    Class for holding a time table suitable for routing with the Connection Scan Algorithm (CSA)

    Time table holds each connection with the following info:
        Origin Stop, Destination Stop, departure time, arrival time, service ID
    Fares are implemented as a flat fare for each service boarded. Zone-based fares and fare integrations are future
    improvements

    """
    num_connect: int
    connections: np.array
    routes: np.array
    temp_timetable: list
    indexer: np.array
    stations: np.array  # []  index is the number of the node

    def __init__(self):
        self.temp_timetable = []

    def check_timetable(self) -> None:
        """
        Checks that need to be implemented:
            - Does the list of routes in the fares table match the list of routes in the timetable table?
        """
        pass

    def add_connection(self, from_stop: int, to_stop: int, departure: int, arrival: int, route_id: int):
        connection = (from_stop, to_stop, departure, arrival, route_id)

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
        # n = np.vstack(self.temp_timetable)
        self.connections = np.array(self.temp_timetable, dtype)
        self.connections.sort(order='departure')
        self.num_connect = self.connections.shape[0]
        self.temp_timetable = []

        self.build_structures()

    def build_structures(self):
        # Sort connections by start time



        # find

        # [from_station, instant, row in the connections table]
        self.indexer = np.zeros((self.num_connect, 3), np.int32)
        self.indexer[:, 2] = np.argsort(self.connections, axis=-1, order=('from', 'departure'))[:]
        self.indexer[:, 0] = self.connections['from'][self.indexer[:, 2]]
        self.indexer[:, 1] = self.connections['departure'][self.indexer[:, 2]]


        # get all unique connections and list where they appear
        max_station = max(np.max(self.connections['from']), np.max(self.connections['to']))

        self.stations = np.zeros((max_station +1, 2))

        x, indices = np.unique(self.indexer[:, 0], return_index=True)

        self.stations[x[:], 3] = indices[:]



        pass