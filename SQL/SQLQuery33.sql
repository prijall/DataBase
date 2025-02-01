create database twentyone_fall;
use twentyone_fall;

create table Chef_1(
chef_liscense int primary key,
cf_name varchar(50),
cl_name varchar(50),
c_dob date,
c_gender varchar(20),
c_experience_hours int,
c_photo varchar(200));

select * from Chef_1;

insert into Chef_1(chef_liscense, cf_name, cl_name, c_dob, c_gender, c_experience_hours, c_photo)
           VALUES(1, 'prijal', 'khadka', '2002-10-21', 'male', 4000, 'sdsds'),
		          (2, 'ashum', 'shrestha', '2003-09-14', 'male', 233, 'dsdsd'),
				  (3, 'sristi', 'mandal', '2001-02-15', 'female', 3443, 'dsdssdf'),
				  (4, 'puja', 'rai', '1988-06-23', 'female', 2323, 'dsds');





	update Chef_1 set c_experience_hours = 1000 where  chef_liscense = 2;

	select SUM(c_experience_hours) as 'total_hours' from Chef_1;


	create view Details_1 as 
	select cf_name, cl_name, c_dob, chef_liscense from Chef_1
	where c_gender = 'female';


	select * from Details_1;



SELECT * 
FROM Chef_1
WHERE cl_name IN ('khadka', 'shrestha', 'mandal', 'rai') 
ORDER BY cl_name DESC, cf_name ASC;


DELETE FROM Chef_1
WHERE cf_name LIKE '_r%';
