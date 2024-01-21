create database office;
use office;

create table employee1(
EmployeeID int primary key,
firstname varchar(50),
lastname varchar(50),
position varchar(50),
salary int);

--trigger to automatically insert the salary based on the position of the employeee

create trigger UpdateSalaryBasedOnPositionTrigger
on employee1
after insert 
as 
begin
    update e 
	set e.salary=
	case 
	   when i.position ='Manager' then 80000
	   when i.position = 'Supervisor' then 60000
	   when i.position = 'Employee' then 50000
	   else 0

end

from employee1 e
inner join inserted i on e.EmployeeID = i.EmployeeID;
end;



insert into employee1(EmployeeID, firstname, lastname, position)
             values
			        (2, 'sam', 'dee', 'supervisor');



			 select * from employee1