-- This schema applies some (NOT all) of the constraints enforced in A1.
-- You may not assume that a constraint holds unless it is clearly indicated.
-- Some of the constraints are enforced using SQL notation.
-- We have included the constraint as a comment in cases where enforcing
-- the constraint would be costly.

drop schema if exists waste_wrangler cascade;
create schema waste_wrangler;
set search_path to waste_wrangler;

-- A type of collectible waste.
create table WasteType (
	wasteType varchar(50) primary key
);

-- A row in this table indicates that the trucktype
-- can collect this wastetype.
create table TruckType (
	truckType varchar(50),
	wasteType varchar(50) references WasteType,
	primary key (truckType, wasteType)
);

-- A waste collection truck. tID is its id, trucktype is
-- its type, and capacity is the maximum volume of waste
-- in cubic metres that this truck can hold.
-- You may assume that every truckType is a valid truck type i.e.
-- it is recorded in the TruckType relation.
create table Truck (
	tID int primary key,
	truckType varchar(50) not null,
	capacity float not null
);

-- A waste collection facility (i.e. where trucks empty their
-- loads after a trip). Each facility has an ID fID, is located
-- at address, and collects waste of type wasteType.
create table Facility (
	fID int primary key,
	address varchar(50) not null,
	wasteType varchar(50) not null references WasteType
);

-- An employee, with employee ID eID, named name, who
-- was hired on day hiredate.
-- [MT] You may assume that an employee can not be a driver and a technician.
create table Employee (
	eID int primary key,
	name varchar(50) not null,
	hireDate date not null
);

-- A row in this table indicates that the employee with
-- employee ID eID is a driver, who can drive trucks of type
-- truckType.
-- You may assume that every truckType is a valid truck type i.e.
-- it is recorded in the TruckType relation.
create table Driver (
	eID integer references Employee,
	truckType varchar(50),
	primary key (eID, truckType)
);

-- A row in this table indicates that the employee with
-- employee ID eID is a technician, who can maintain
-- trucks of type truckType.
-- You may assume that every truckType is a valid truck type i.e.
-- it is recorded in the TruckType relation.
create table Technician (
	eID integer references Employee,
	truckType varchar(50),
	primary key (eID, truckType)
);

-- A row in this table indicates that maintainenace on
-- truck tID is scheduled to be performed by the technician eID on date mDate.
-- You may assume that:
--	* Employee eID is a technician.
--	* Technician eID can maintain the truck type of truck tID
--  * The hire date of technician eID <= date(mDate)
create table Maintenance (
	tID integer references Truck,
	eID integer references Employee,
	mDATE date,
	primary key (tID, mDATE)
);

-- A scheduled waste collection route with route ID rID.
-- wastetype is the type of waste collected on this route,
-- and length is the distance in kilometers that must be
-- driven for the route.
create table Route (
	rID int primary key,
	wasteType varchar(50) not null references WasteType,
	length float not null
);

-- A stop on a collection route (e.g., a house or apartment building).
-- address is the street address of the stop, rID is the route the stop is
-- on, and assisstance is a boolean value that indicates whether the resident
-- of this stop requires assisstance with bringing their waste to
-- the curb.
create table Stop (
	address varchar(100),
	rID integer references Route,
	assistance boolean not null,
	primary key (address, rID)
);

-- A collection trip made at time tTime by truck tID on route rID with drivers
-- eID1 and eID2, collecting volume amount of waste in cubic metres,
-- which was taken to facility fID.
-- You may assume that:
-- 	* tID has had maintenance in the last 100 days before each trip.
--	* The hire date of eID1 <= date(tTime)
--	* The hire date of eID2 <= date(tTime)
--  * Both eID1 and eI2 are drivers and at least one can drive
--	  the truck type of tID.
--  * A driver can be on one trip at a time.
--	* Similarly, a truck can be on one trip at a time and can't have
--	  maintenance on the day of a trip.
-- 	* Trips made by the same truck/driver must be 0.5 an hour apart.
--  * volume <= tID's capacity
-- 	* tID, rID and fID all have the same waste type

create table Trip (
	rID integer references Route,
	tID integer references Truck,
	tTIME timestamp,
	volume float,
	eID1 integer not null references Employee,
	eID2 integer not null references Employee,
	fID integer not null references Facility,
	primary key (rID, tTime),
	unique (tID, tTime),
	check (eID1 >= eID2),
	check (tTime::time between '8:00' and '16:00')
);

-- The following ensures that a route can be scheduled at most once per day
create unique index service_unique on Trip(rID, date(tTime));
