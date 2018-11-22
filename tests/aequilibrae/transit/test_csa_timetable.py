from unittest import TestCase
from aequilibrae.transit.csa import Timetable
import numpy as np

class TestTimetable(TestCase):
    def test_check_timetable(self):
        # self.fail()
        pass

    def test_add_connection(self):
        t = Timetable()
        t.add_connection(13, 16, 20, 35, 30)
        if t.temp_timetable != [[13, 16, 20, 35, 30]]:
            self.fail("Adding connection returned wrong value")

        # testing wrong inputs
        inputs = [[13, 16, 20, 35, 30.1], [13, 16, 20, 35, "x"]]
        for q in inputs:
            t = Timetable()
            try:
                t.add_connection(*q)
                self.fail("Adding connection did not return an error for wrong argument types")
            except TypeError as f:
                # TypeError
                if f.args[0] != "ALL characteristics of a connection need to be integers":
                    self.fail("Adding connection returned the wrong error for wrong argument types")
            except:
                self.fail("Adding connection returned the wrong error for wrong argument types")

        # Test missing arguments
        t = Timetable()
        try:
            t.add_connection(13, 16, 20, 35)
            self.fail("Adding connection did not return an error for too few arguments")
        except TypeError as f:
            # TypeError
            if f.args[0] != "add_connection() missing 1 required positional argument: 'route_id'":
                self.fail("Adding connection returned the wrong error for too few arguments")
        except:
            self.fail("Adding connection returned the wrong error for too few arguments")

        # Tests too many arguments
        t = Timetable()
        try:
            t.add_connection(13, 16, 20, 35, 10, 10)
            self.fail("Adding connection did not return an error for too many arguments")
        except TypeError as f:
            # TypeError
            if f.args[0] != "add_connection() takes 6 positional arguments but 7 were given":
                self.fail("Adding connection returned the wrong error for too many arguments")
        except:
            self.fail("Adding connection returned the wrong error for too many arguments")

        # Tests arrival before departure
        t = Timetable()
        try:
            t.add_connection(13, 16, 20, 15, 10)
            self.fail("Adding connection did not return an error for arrival/departure error")
        except ValueError as f:
            # TypeError
            if f.args[0] != "A connection cannot arrive before it departs":
                self.fail("Adding connection returned the wrong error for arrival/departure error")
        except:
            self.fail("Adding connection returned the wrong error for arrival/departure error")



    def test_build_connections(self):

        t = Timetable()
        t.add_connection(13, 16, 20, 35, 30)
        t.add_connection(14, 17, 21, 36, 31)
        t.add_connection(15, 18, 22, 37, 32)
        t.build_connections()

        dtype = np.dtype({'names': ['from', 'to', 'departure', 'arrival', 'route_id'],
                          'formats': ['i4'] * 5})

        if not (t.connections == np.array([[(13, 16, 20, 35, 30)],
                                           [(14, 17, 21, 36, 31)],
                                           [(15, 18, 22, 37, 32)]], dtype)).all():

            self.fail("Did not properly create the connections table")
