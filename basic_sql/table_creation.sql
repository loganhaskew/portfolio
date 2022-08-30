-----------------------------------------------------------------
-- use Kaggle books dataset for basic SQL practice
-- https://www.kaggle.com/datasets/saurabhbagchi/books-dataset
-----------------------------------------------------------------


-- create table to hold book information
create table books(
	isbn varchar(25) not null,
	book_title varchar(255) not null,
	book_author varchar(255) not null,
	pub_year smallint,
	publisher varchar(255),
	image_s varchar(255),
	image_m varchar(255),
	image_l varchar(255),
	primary key (isbn)
);

-- copy book data from csv (in tmp folder so PG can access it)
copy books
from '/private/tmp/books.csv'
delimiter ';'
escape '\'
csv header;


-- create ratings table
-- specifying a primary key does not make sense here
create table ratings(
	user_id int,
	isbn varchar(25) not null,
	rating smallint
);

-- import csv data for ratings
copy ratings
from '/private/tmp/ratings.csv'
delimiter ';'
escape '\'
csv header;


-- create user table
create table users(
	user_id int not null,
	location varchar(100),
	age smallint,
	primary key (user_id)
);

-- import csv data for users
copy users
from '/private/tmp/users.csv'
delimiter ';'
escape '\'
-- there are some nuanced characters in this csv
-- we can use specify encoding that can deal with these
encoding 'ISO-8859-1'
null as 'NULL'
csv header;