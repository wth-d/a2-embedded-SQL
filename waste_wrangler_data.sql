-- a few employees
insert into employee values (1, 'Frank Zappa', '1965-05-01');
insert into employee values (2, 'Clara Zetkin', '1901-10-11');
insert into employee values (3, 'Rigoberta Menchu', '1974-06-01');
insert into employee values (4, 'Chico Mendes', '1983-05-01');
insert into employee values (5, 'Bertholt Brecht', '1983-03-01');
insert into employee values (6, 'Pablo Picasso', '1975-07-15');
insert into employee values (7, 'Vandana Shiva', '1996-09-28');
insert into employee values (8, 'Angela Davis', '2008-11-13');
insert into employee values (9, 'Mercedes Sosa', '2013-02-23');
--
-- some drivers...
--
insert into driver values
(1, 'A'), (1, 'C'), (1, 'E');
insert into driver values
(2, 'B'), (2, 'D');
insert into driver values
(3, 'A'), (3, 'D');
insert into driver values
(4, 'C'), (4, 'E');
--
-- some technicians
--
insert into technician values
(5, 'A'), (5, 'B'), (5, 'C');
insert into technician values
(6, 'D'), (6, 'E');
insert into technician values
(7, 'A'), (7, 'C'), (7, 'E');
insert into technician values
(8, 'D'), (8, 'E');
insert into technician values
(9, 'C'), (9, 'A');
--
-- a few wastetypes
--
insert into wastetype values('plastic recycling');
insert into wastetype values('compost');
insert into wastetype values('paper recycling');
insert into wastetype values('landfill');
insert into wastetype values('aluminum containers');
insert into wastetype values('large items');
insert into wastetype values('electronic waste');
--
-- a few trucktypes
--
insert into trucktype values('A', 'plastic recycling');
insert into trucktype values('A', 'paper recycling');
insert into trucktype values('B', 'plastic recycling');
insert into trucktype values('C', 'compost');
insert into trucktype values('C', 'landfill');
insert into trucktype values('D', 'large items');
insert into trucktype values('D', 'electronic waste');
insert into trucktype values('E', 'aluminum containers');
insert into trucktype values('E', 'electronic waste');
--
-- a few trucks
--
insert into truck values(1, 'A', 23); -- capacity is in cubic metres
insert into truck values(2, 'B', 20);
insert into truck values(3, 'C', 19);
insert into truck values(4, 'C', 21);
insert into truck values(5, 'D', 12);
insert into truck values(6, 'E', 15);
insert into truck values(7, 'E', 13);
--
-- a few facilities
--
insert into facility values
(1, '15 Drury Lane, M7F 2L2', 'plastic recycling'),
(2, '13 The Esplanade, M8G 932', 'paper recycling'),
(3, '993 Dundas West, M5T 1J3', 'compost'),
(4, '67 Commissioners Street, M3B 5S2', 'landfill'),
(5, '993 Eastern Avenue, M2J 1E1', 'aluminum containers'),
(6, '4023 Markham Ave, M1F 2J2', 'large items'),
(7, '3023 Kipling Ave, M9H 1K8', 'electronic waste'),
(8, '400 Eastern Ave, M4M 1B9', 'plastic recycling');
--
-- some maintenance
--
insert into maintenance values
(1, 5, '2022-09-15'), (5, 6, '2022-07-11'),
(3, 7, '2021-10-25'), (6, 8, '2021-03-02');
insert into maintenance values
(4, 9, '2021-05-01'), (2, 5, '2022-02-24'), (7, 8, '2021-12-13');
--
-- a few routes
--
insert into route values
(1, 'plastic recycling', 15);
--
-- a few trips
--
insert into trip values
(1, 1, '2023-05-03 08:15:06', 17, 3, 1, 1);
