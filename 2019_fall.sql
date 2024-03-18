create database Hospital_Management

use Hospital_Management


create table Doctors(
DoctorId int primary key,
DoctorName varchar(50), 
Department varchar(50),
Address varchar(50),
Salary float);

select * from Doctors;


create table Patients(
PatientId int primary key,
PatientName varchar(50),
Address varchar(50),
Age int,
Gender varchar(50));

select * from Patients;


create table Hospital(
PatientId int references Patients(PatientId),
DoctorId int references Doctors(DoctorId),
HospitalName varchar(50),
Location varchar(50));

select * from Hospital;


---Q.no.1---

SELECT h.PatientId
FROM Hospital h
JOIN Patients p ON h.PatientId = p.PatientId
WHERE h.Location = 'Pokhara' AND p.PatientName LIKE '%s';


--Q no 2--

DELETE FROM Doctors
WHERE Salary > (
    SELECT AVG(Salary)
    FROM Doctors
);

--Q no 3---

update Doctors set Salary =  Salary * 1.185  where Department = 'OPD';

-- Q no 4 ----

SELECT Address, AVG(Salary) AS AverageSalary
FROM Doctors
GROUP BY Address
HAVING AVG(Salary) > 55000;
