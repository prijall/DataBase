create database spring_2021;

use spring_2021;

create table sailors(
sid int primary key,
sname varchar(50),
rating float,
age int);

create table Boats(
bid int primary key,
bname varchar(50),
color varchar(40));


create table Reserves(
sid int references sailors(sid),
bid int references Boats(bid),
day date);


--Q no 1----

SELECT sailors.sid, sailors.sname, sailors.rating, sailors.age
FROM sailors
INNER JOIN Reserves ON sailors.sid = Reserves.sid
WHERE Reserves.bid = 103;

--Q no 2----

update Boats set color = 'green' where bid=103

---Q3----

SELECT DISTINCT sailors.sname
FROM sailors
INNER JOIN Reserves ON sailors.sid = Reserves.sid
INNER JOIN Boats ON Reserves.bid = Boats.bid
WHERE Boats.color IN ('red', 'green');


--Q4---

SELECT DISTINCT sailors.sname
FROM sailors
INNER JOIN Reserves ON sailors.sid = Reserves.sid
INNER JOIN Boats ON Reserves.bid = Boats.bid
WHERE Reserves.bid = 103 AND Reserves.day = '2024-03-05';


--Q5----
SELECT sname
FROM sailors
WHERE sname != 'Ram';


---Q6---

SELECT bname
FROM Boats;

