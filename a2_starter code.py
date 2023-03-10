"""CSC343 Assignment 2

=== CSC343 Winter 2023 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC343 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Danny Heap, Marina Tawfik, and Jacqueline Smith

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Danny Heap and Jacqueline Smith

=== Module Description ===

This file contains the WasteWrangler class and some simple testing functions.
"""

import datetime as dt
import psycopg2 as pg
import psycopg2.extensions as pg_ext
import psycopg2.extras as pg_extras
from typing import Optional, TextIO


class WasteWrangler:
    """A class that can work with data conforming to the schema in
    waste_wrangler_schema.ddl.

    === Instance Attributes ===
    connection: connection to a PostgreSQL database of a waste management
    service.

    Representation invariants:
    - The database to which connection is established conforms to the schema
      in waste_wrangler_schema.ddl.
    """
    connection: Optional[pg_ext.connection]

    def __init__(self) -> None:
        """Initialize this WasteWrangler instance, with no database connection
        yet.
        """
        self.connection = None

    def list_of_rIDs(self) -> list:
        """return all rIDs (from Route table)"""
        assert self.connection, "not connected"
        cur = self.connection.cursor()
        cur.execute("SET search_path TO waste_wrangler;")
        cur.execute("SELECT DISTINCT rID FROM Route;")
        rIDs = []
        for row in cur:
            rIDs.append(row[0])
        return rIDs

    def find_route_info(self, rid: int) -> tuple:
        assert self.connection, "not connected"

        if rid not in self.list_of_rIDs():
            return tuple()
        
        cur = self.connection.cursor()
        cur.execute("SET search_path TO waste_wrangler;")
        cur.execute('''SELECT * FROM Route R
                       WHERE R.rID=%s;
                       ''', (rid,))
        for row in cur:
            return row

    def connect(self, dbname: str, username: str, password: str) -> bool:
        """Establish a connection to the database <dbname> using the
        username <username> and password <password>, and assign it to the
        instance attribute <connection>. In addition, set the search path
        to waste_wrangler.

        Return True if the connection was made successfully, False otherwise.
        I.e., do NOT throw an error if making the connection fails.

        >>> ww = WasteWrangler()
        >>> ww.connect("csc343h-marinat", "marinat", "")
        True
        >>> # In this example, the connection cannot be made.
        >>> ww.connect("invalid", "nonsense", "incorrect")
        False
        """
        try:
            self.connection = pg.connect(
                dbname=dbname, user=username, password=password,
                options="-c search_path=waste_wrangler"
            )
            return True
        except pg.Error:
            return False

    def disconnect(self) -> bool:
        """Close this WasteWrangler's connection to the database.

        Return True if closing the connection was successful, False otherwise.
        I.e., do NOT throw an error if closing the connection failed.

        >>> ww = WasteWrangler()
        >>> ww.connect("csc343h-marinat", "marinat", "")
        True
        >>> ww.disconnect()
        True
        """
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
            return True
        except pg.Error:
            return False

    def schedule_trip(self, rid: int, time: dt.datetime) -> bool:
        """Schedule a truck and two employees to the route identified
        with <rid> at the given time stamp <time> to pick up an
        unknown volume of waste, and deliver it to the appropriate facility.

        The employees and truck selected for this trip must be available:
            * They can NOT be scheduled for a different trip from 30 minutes
              of the expected start until 30 minutes after the end time of this
              trip.
            * The truck can NOT be scheduled for maintenance on the same day.

        The end time of a trip can be computed by assuming that all trucks
        travel at an average of 5 kph.

        From the available trucks, pick a truck that can carry the same
        waste type as <rid> and give priority based on larger capacity and
        use the ascending order of ids to break ties.

        From the available employees, give preference based on hireDate
        (employees who have the most experience get priority), and order by
        ascending order of ids in case of ties, such that at least one
        employee can drive the truck type of the selected truck.

        Pick a facility that has the same waste type as <rid> and select the one
        with the lowest fID.

        Return True iff a trip has been scheduled successfully for the given
            route.
        This method should NOT throw an error i.e. if scheduling fails, the
        method should simply return False.

        No changes should be made to the database if scheduling the trip fails.

        Scheduling fails i.e., the method returns False, if any of the following
        is true:
            * If rid is an invalid route ID.
            * If no appropriate truck, drivers or facility can be found.
            * If a trip has already been scheduled for <rid> on the same day
              as <time> (that encompasses the exact same time as <time>).
            * If the trip can't be scheduled within working hours i.e., between
              8:00-16:00.

        While a realistic use case will provide a <time> in the near future, our
        tests could use any valid value for <time>.
        """
        try:
            # TODO: implement this method
            print("starting schedule_trip...")
            assert self.connection, "not connected"
            
            all_rIDs = self.list_of_rIDs()
            print(f"list of rids: {all_rIDs}")
            if rid not in all_rIDs:
                print("rid is not a valid rid")
                return False
            
            route_info = self.find_route_info(rid)
            print(route_info)
            wastetype = route_info[1]
            routelength = route_info[2]

            cur = self.connection.cursor()
            cur.execute("SET search_path TO waste_wrangler;")
            
            cur.execute('''SELECT * FROM Trip
                           WHERE date(ttime)=date(%s);
                           ''', (time,))
            for row in cur:
                print('''A trip has been scheduled for <rid> on the same 
                day as <time>''')
                cur.close()
                self.connection.rollback()
                return False
            
            cur.execute('''CREATE TEMPORARY VIEW Hiredatesmatch AS
                           SELECT DISTINCT D.eID
                           FROM Driver D JOIN Employee E ON D.eID=E.eID
                           WHERE (SELECT date(hireDate) - %s::date) <= 0;
                           
                           ''', (time,))
            cur.execute('''SELECT * FROM Hiredatesmatch;
            ''')
            print("output of Hiredatesmatch(eID):")
            for row in cur:
                print(row[0])

            # drivers whose hire date and waste type meet requirement
##            cur.execute('''CREATE VIEW CandidatesD AS
##                           (SELECT DISTINCT D.eID
##                           FROM Driver D JOIN TruckType T ON D.truckType=T.truckType
##                           WHERE wasteType=%s)
##                           INTERSECT
##                           (SELECT * FROM Hiredatesmatch);
##                           
##                           ''', (wastetype,))
            #for row in cur:

            speed = 5.0 # kph
            endtime = time + dt.timedelta(hours=(routelength / speed))
            print(f"starttime is {time}")
            print(f"endtime is {endtime}")

            # must be between 8:00-16:00
            if (time.time() < dt.time(8) or endtime.time() > dt.time(16)):
                print("trip is outside of working hours")
                cur.close()
                self.connection.rollback()
                return False
            
            timelower = time - dt.timedelta(minutes=30) # lower limit
            timeupper = endtime + dt.timedelta(minutes=30)
            print(f"lower limit of time is {timelower}")
            print(f"upper limit is {timeupper}")

            cur.execute('''CREATE TEMPORARY VIEW TripWithLength AS
                           SELECT ttime, eID1, eID2, tID, length
                           FROM Trip T JOIN Route R ON T.rID=R.rID;
                           ''')
            # find those employees whose trip times overlap with
            # the [timelower, timeupper] interval
            cur.execute('''CREATE TEMPORARY VIEW EmployeesNotAvailable AS
                           (SELECT eID1 AS eID FROM TripWithLength
                           WHERE (ttime < %(lower)s
                             and (ttime + make_interval(hours=>(length/5)::INTEGER)) > %(lower)s) or
                             ((ttime >= %(lower)s and ttime <= %(upper)s))
                           )
                           UNION
                           (SELECT eID2 AS eID FROM TripWithLength
                           WHERE (ttime < %(lower)s
                             and (ttime + make_interval(hours=>(length/5)::INTEGER)) > %(lower)s) or
                             ((ttime >= %(lower)s and ttime <= %(upper)s))
                           );
                           
                           ''', {'lower': timelower, 'upper': timeupper})
            # the drivers that are available
            cur.execute('''CREATE TEMPORARY VIEW AvailableDrivers AS
                           (SELECT * FROM Hiredatesmatch)
                           EXCEPT
                           (SELECT * FROM EmployeesNotAvailable);
                           ''') # Hiredatesmatch instead of CandidatesD
            cur.execute("SELECT * FROM AvailableDrivers;")
            available_drivers = []
            for row in cur:
                available_drivers.append(row[0]);
            print(f"available drivers: {available_drivers}")

            cur.execute("DROP VIEW Hiredatesmatch;")
            cur.execute("DROP VIEW EmployeesNotAvailable;")
            if (available_drivers == []):
                print("schedule_trip: no availble drivers")
                cur.close()
                self.connection.rollback()
                return False

            # similar to drivers, find unavailable trucks
            cur.execute('''CREATE TEMPORARY VIEW TrucksNotAvailable AS
                           (SELECT tID FROM TripWithLength
                           WHERE (ttime < %(lower)s
                             and (ttime + make_interval(hours=>(length/5)::INTEGER)) > %(lower)s) or
                             ((ttime >= %(lower)s and ttime <= %(upper)s))
                           );
                           
                           ''', {'lower': timelower, 'upper': timeupper})
            # trucks are also unavailable if maintained on same date
            cur.execute('''CREATE TEMPORARY VIEW MaintainedTrucks AS
                           SELECT tID FROM Maintenance
                           WHERE mdate=date(%s)
                           ''', (time,))
            # the trucks that are available
            cur.execute('''CREATE TEMPORARY VIEW AvailableTrucks AS
                           (SELECT tID FROM Truck)
                           EXCEPT
                           (SELECT * FROM TrucksNotAvailable)
                           EXCEPT
                           (SELECT * FROM MaintainedTrucks);
                           ''')

            # pick a truck
            cur.execute('''SELECT DISTINCT Temp.tID
                           FROM
                               (SELECT capacity, A.tID
                               FROM AvailableTrucks A JOIN Truck T ON A.tID=T.tID
                                                      JOIN TruckType Ttype ON T.truckType=Ttype.truckType
                               WHERE wasteType=%s
                               ORDER BY capacity DESC, A.tID) Temp;
                           ''', (wastetype,))
            available_trucks = []
            for row in cur:
                available_trucks.append(row[0]);
                # does this for loop/fetchone work for views? -> can cause a "no results to fetch" error
            print(f"available trucks: {available_trucks}")

            cur.execute("DROP VIEW TripWithLength;")
            cur.execute("DROP VIEW TrucksNotAvailable;")
            cur.execute("DROP VIEW MaintainedTrucks;")
            cur.execute("DROP VIEW AvailableTrucks;")
            if (available_trucks == []):
                print("schedule_trip: no availble trucks")
                cur.close()
                self.connection.rollback()
                return False

            truckid = available_trucks[0]

            # pick an employee/driver
            # first, find drivers who can drive the picked truckType
            cur.execute('''SELECT DISTINCT D.eID FROM Driver D
                           WHERE D.truckType=(
                               SELECT truckType FROM Truck T
                               WHERE T.tID=%s
                           );
                           ''', (truckid,))
            truckType_match = []
            for row in cur:
                truckType_match.append(row[0])

            # order availble_drivers by hireDate and eID
            cur.execute('''SELECT A.eID, hireDate
                           FROM AvailableDrivers A JOIN Employee E ON A.eID=E.eID
                           ORDER BY hireDate, eID
                           ''', (truckid,))
            available_drivers = [] # reset
            print("available drivers sorted:")
            for row in cur:
                available_drivers.append(row[0]);
                print(row)

            first_driver = -1
            for eid in available_drivers:
                if eid in truckType_match:
                    first_driver = eid
                    break
            if first_driver == -1:
                print("no available driver matches the truckType")
                return False
            second_driver = -1
            for eid in available_drivers:
                if eid != first_driver:
                    second_driver = eid
                    break
            if second_driver == -1:
                print("cannot find a second available driver")
                return False
            print(f"drivers picked: {first_driver}, {second_driver}")

            # pick a facility
            cur.execute('''SELECT fID, wasteType
                           FROM Facility
                           WHERE wasteType=%s
                           ORDER BY fID
                           ''', (wastetype,))
            fid_picked = -1
            for row in cur:
                fid_picked = row[0]
                break
            if fid_picked == -1:
                print("cannot find a facility with a right wasteType")
                return False

            cur.execute('''INSERT INTO Trip VALUES
                           (%s, %s, %s, %s, %s, %s, %s)
                           ''', (rid, truckid, time, "null", first_driver,
                                 second_driver, fid_picked))

            #

            #cur.execute("DROP VIEW Hiredatesmatch;")
            cur.close()
            self.connection.commit()
            return True
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            raise ex
            self.connection.rollback()
            return False

    def schedule_trips(self, tid: int, date: dt.date) -> int:
        """Schedule the truck identified with <tid> for trips on <date> using
        the following approach:

            1. Find routes not already scheduled for <date>, for which <tid>
               is able to carry the waste type. Schedule these by ascending
               order of rIDs.

            2. Starting from 8 a.m., find the earliest available pair
               of drivers who are available all day. Give preference
               based on hireDate (employees who have the most
               experience get priority), and break ties by choosing
               the lower eID, such that at least one employee can
               drive the truck type of <tid>.

               The facility for the trip is the one with the lowest fID that can
               handle the waste type of the route.

               The volume for the scheduled trip should be null.

            3. Continue scheduling, making sure to leave 30 minutes between
               the end of one trip and the start of the next, using the
               assumption that <tid> will travel an average of 5 kph.
               Make sure that the last trip will not end after 4 p.m.

        Return the number of trips that were scheduled successfully.

        Your method should NOT raise an error.

        While a realistic use case will provide a <date> in the near future, our
        tests could use any valid value for <date>.
        """
        # TODO: implement this method

        cur.close()
        self.connection.commit()
        pass

    def update_technicians(self, qualifications_file: TextIO) -> int:
        """Given the open file <qualifications_file> that follows the format
        described on the handout, update the database to reflect that the
        recorded technicians can now work on the corresponding given truck type.

        For the purposes of this method, you may assume that no two employees
        in our database have the same name i.e., an employee can be uniquely
        identified using their name.

        Your method should NOT throw an error.
        Instead, only correct entries should be reflected in the database.
        Return the number of successful changes, which is the same as the number
        of valid entries.
        Invalid entries include:
            * Incorrect employee name.
            * Incorrect truck type.
            * The technician is already recorded to work on the corresponding
              truck type.
            * The employee is a driver.

        Hint: We have provided a helper _read_qualifications_file that you
            might find helpful for completing this method.
        """
        try:
            # TODO: implement this method

            cur.close()
            self.connection.commit()
            pass
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            # raise ex
            self.connection.rollback()
            return 0

    def workmate_sphere(self, eid: int) -> list[int]:
        """Return the workmate sphere of the driver identified by <eid>, as a
        list of eIDs.

        The workmate sphere of <eid> is:
            * Any employee who has been on a trip with <eid>.
            * Recursively, any employee who has been on a trip with an employee
              in <eid>'s workmate sphere is also in <eid>'s workmate sphere.

        The returned list should NOT include <eid> and should NOT include
        duplicates.

        The order of the returned ids does NOT matter.

        Your method should NOT return an error. If an error occurs, your method
        should simply return an empty list.
        """
        try:
            # TODO: implement this method
            pass
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            # raise ex
            return []

    def schedule_maintenance(self, date: dt.date) -> int:
        """For each truck whose most recent maintenance before <date> happened
        over 90 days before <date>, and for which there is no scheduled
        maintenance up to 10 days following date, schedule maintenance with
        a technician qualified to work on that truck in ascending order of tIDs.

        For example, if <date> is 2023-05-02, then you should consider trucks
        that had maintenance before 2023-02-01, and for which there is no
        scheduled maintenance from 2023-05-02 to 2023-05-12 inclusive.

        Choose the first day after <date> when there is a qualified technician
        available (not scheduled to maintain another truck that day) and the
        truck is not scheduled for a trip or maintenance on that day.

        If there is more than one technician available on a given day, choose
        the one with the lowest eID.

        Return the number of trucks that were successfully scheduled for
        maintenance.

        Your method should NOT throw an error.

        While a realistic use case will provide a <date> in the near future, our
        tests could use any valid value for <date>.

        Q: If a truck has no maintenance record, should it be scheduled for maintenance?
        A: Yes, since it has no maintenance record more recent than 90 days.
        """
        try:
            # TODO: implement this method
            pass
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            # raise ex
            return 0

    def reroute_waste(self, fid: int, date: dt.date) -> int:
        """Reroute the trips to <fid> on day <date> to another facility that
        takes the same type of waste. If there are many such facilities, pick
        the one with the smallest fID (that is not <fid>).

        Return the number of re-routed trips.

        Don't worry about too many trips arriving at the same time to the same
        facility. Each facility has ample receiving facility.

        Your method should NOT return an error. If an error occurs, your method
        should simply return 0 i.e., no trips have been re-routed.

        While a realistic use case will provide a <date> in the near future, our
        tests could use any valid value for <date>.

        Assume this happens before any of the trips have reached <fid>.
        """
        try:
            # TODO: implement this method
            pass
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            # raise ex
            return 0

    # =========================== Helper methods ============================= #

    @staticmethod
    def _read_qualifications_file(file: TextIO) -> list[list[str, str, str]]:
        """Helper for update_technicians. Accept an open file <file> that
        follows the format described on the A2 handout and return a list
        representing the information in the file, where each item in the list
        includes the following 3 elements in this order:
            * The first name of the technician.
            * The last name of the technician.
            * The truck type that the technician is currently qualified to work
              on.

        Pre-condition:
            <file> follows the format given on the A2 handout.
        """
        result = []
        employee_info = []
        for idx, line in enumerate(file):
            if idx % 2 == 0:
                info = line.strip().split(' ')[-2:]
                fname, lname = info
                employee_info.extend([fname, lname])
            else:
                employee_info.append(line.strip())
                result.append(employee_info)
                employee_info = []

        return result


def setup(dbname: str, username: str, password: str, file_path: str) -> None:
    """Set up the testing environment for the database <dbname> using the
    username <username> and password <password> by importing the schema file
    and the file containing the data at <file_path>.
    """
    connection, cursor, schema_file, data_file = None, None, None, None
    try:
        # Change this to connect to your own database
        connection = pg.connect(
            dbname=dbname, user=username, password=password,
            options="-c search_path=waste_wrangler"
        )
        cursor = connection.cursor()

        schema_file = open("./waste_wrangler_schema.sql", "r")
        cursor.execute(schema_file.read())

        data_file = open(file_path, "r")
        cursor.execute(data_file.read())

        connection.commit()
    except Exception as ex:
        connection.rollback()
        raise Exception(f"Couldn't set up environment for tests: \n{ex}")
    finally:
        if cursor and not cursor.closed:
            cursor.close()
        if connection and not connection.closed:
            connection.close()
        if schema_file:
            schema_file.close()
        if data_file:
            data_file.close()


def test_preliminary() -> None:
    """Test preliminary aspects of the A2 methods.
    We have included some assert statements at the end of a2.py in the test_preliminary function. These
are meant to assure you that you have started off on the right track, and you will earn 20% of the
assignment grade for passing these.
    """
    ww = WasteWrangler()
    qf = None
    try:
        # TODO: Change the values of the following variables to connect to your
        #  own database:
        #dbname = 'postgres'
        dbname = 'csc343h-hanwei1'
        user = 'hanwei1'
        password = ''

        connected = ww.connect(dbname, user, password)

        # The following is an assert statement. It checks that the value for
        # connected is True. The message after the comma will be printed if
        # that is not the case (connected is False).
        # Use the same notation to thoroughly test the methods we have provided
        assert connected, f"[Connected] Expected True | Got {connected}."

        # TODO: Test one or more methods here, or better yet, make more testing
        #   functions, with each testing a different aspect of the code.

        # The following function will set up the testing environment by loading
        # the sample data we have provided into your database. You can create
        # more sample data files and use the same function to load them into
        # your database.
        # Note: make sure that the schema and data files are in the same
        # directory (folder) as your a2.py file.
        setup(dbname, user, password, './waste_wrangler_data.sql')

        # --------------------- Testing schedule_trip  ------------------------#

        # You will need to check that data in the Trip relation has been
        # changed accordingly. The following row would now be added:
        # (1, 1, '2023-05-04 08:00', null, 2, 1, 1)
        scheduled_trip = ww.schedule_trip(1, dt.datetime(2023, 5, 4, 8, 0))
        assert scheduled_trip, \
            f"[Schedule Trip] Expected True, Got {scheduled_trip}"

        # Can't schedule the same route of the same day.
        scheduled_trip = ww.schedule_trip(1, dt.datetime(2023, 5, 4, 13, 0))
        assert not scheduled_trip, \
            f"[Schedule Trip] Expected False, Got {scheduled_trip}"

        # -------------------- Testing schedule_trips  ------------------------#

        # All routes for truck tid are scheduled on that day
        scheduled_trips = ww.schedule_trips(1, dt.datetime(2023, 5, 3))
        assert scheduled_trips == 0, \
            f"[Schedule Trips] Expected 0, Got {scheduled_trips}"

        # ----------------- Testing update_technicians  -----------------------#

        # This uses the provided file. We recommend you make up your custom
        # file to thoroughly test your implementation.
        # You will need to check that data in the Technician relation has been
        # changed accordingly
        qf = open('qualifications.txt', 'r')
        updated_technicians = ww.update_technicians(qf)
        assert updated_technicians == 2, \
            f"[Update Technicians] Expected 2, Got {updated_technicians}"

        # ----------------- Testing workmate_sphere ---------------------------#

        # This employee doesn't exist in our instance
        workmate_sphere = ww.workmate_sphere(2023)
        assert len(workmate_sphere) == 0, \
            f"[Workmate Sphere] Expected [], Got {workmate_sphere}"

        workmate_sphere = ww.workmate_sphere(3)
        # Use set for comparing the results of workmate_sphere since
        # order doesn't matter.
        # Notice that 2 is added to 1's work sphere because of the trip we
        # added earlier.
        assert set(workmate_sphere) == {1, 2}, \
            f"[Workmate Sphere] Expected {{1, 2}}, Got {workmate_sphere}"

        # ----------------- Testing schedule_maintenance ----------------------#

        # You will need to check the data in the Maintenance relation
        scheduled_maintenance = ww.schedule_maintenance(dt.date(2023, 5, 5))
        assert scheduled_maintenance == 7, \
            f"[Schedule Maintenance] Expected 7, Got {scheduled_maintenance}"

        # ------------------ Testing reroute_waste  ---------------------------#

        # There is no trips to facility 1 on that day
        reroute_waste = ww.reroute_waste(1, dt.date(2023, 5, 10))
        assert reroute_waste == 0, \
            f"[Reroute Waste] Expected 0. Got {reroute_waste}"

        # You will need to check that data in the Trip relation has been
        # changed accordingly
        reroute_waste = ww.reroute_waste(1, dt.date(2023, 5, 3))
        assert reroute_waste == 1, \
            f"[Reroute Waste] Expected 1. Got {reroute_waste}"
    finally:
        if qf and not qf.closed:
            qf.close()
        ww.disconnect()


if __name__ == '__main__':
    # Un comment-out the next two lines if you would like to run the doctest
    # examples (see ">>>" in the methods connect and disconnect)
    # import doctest
    # doctest.testmod()

    # TODO: Put your testing code here, or call testing functions such as
    #   this one:
    test_preliminary()
