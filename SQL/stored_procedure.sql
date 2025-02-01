--practicising stored procedure--

use college;
select * from student;


--creating stored procedure--

create procedure SelectStudent
@dept varchar(30)
as 
begin
select * from student 
where dept = @dept;
end;


exec SelectStudent @dept = 'IT';
exec SelectStudent @dept = 'CVL';


--creating multiple parameter stored procedure---

create procedure studentdetails 
@id int , @dept varchar(30)
as 
begin 
select * from student
where id =@id and dept =@dept;
end;


exec studentdetails @id = 3 ^ @dept = 'CVL';