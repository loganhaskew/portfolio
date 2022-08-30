------------------------------------------------------------------------
-- This script houses the queries shown in the book_sql.ipynb file
------------------------------------------------------------------------

-- show tables in schema
select table_name 
from information_schema.tables
where table_schema = 'public';

-- the next few queries are just to become familiar with data
select * from books limit 5;
select * from ratings limit 5;
select * from users limit 5;

select 
(select count(*) from books) as book_count,
(select count(*) from users) as user_count,
(select count(*) from ratings) as rating_count

-----------------------------------------------
-- 1. What users have written the most reviews?
select user_id, count(user_id)
from ratings
group by user_id
order by count(user_id) desc
limit 20;

-----------------------------------------------
-- 2. Which users tend to write the highest reviews?
-- What about the lowest reviews?
select user_id, round(avg(rating), 2) as average_rating, count(user_id) as num_of_reviews
from ratings
group by user_id
having count(user_id) > 10
order by avg(rating) desc
limit 10;
-- now for lowest ratings, we will remove folks that only leave negative reviews here
-- even though that seems that is still what is occuring here
select user_id, round(avg(rating), 2) as average_rating, count(user_id) as num_of_reviews
from ratings
group by user_id
having count(user_id) > 10 and avg(rating) > 0
order by avg(rating)
limit 10;

-----------------------------------------------
-- 3. Which books are the most highly reviewed?
select books.isbn, book_title, book_author, avg(rating) as average_rating, count(rating) as num_of_ratings
from books
inner join ratings on books.isbn = ratings.isbn
group by books.isbn
having count(rating) > 50
order by avg(rating) desc
limit 10;

-----------------------------------------------
-- 4. Which authors are the most highly reviewed?
select book_author, avg(rating) as average_rating, count(rating) as num_of_ratings
from books
inner join ratings on books.isbn = ratings.isbn
group by book_author
having count(rating) > 50
order by avg(rating) desc
limit 25;

-----------------------------------------------
-- 5. Is there any trend in rating vs published year?
-- select the average book rating per year
select b.pub_year, avg(r.rating) as average_rating, 
       count(r.rating) as num_of_ratings
from books b
inner join ratings r on b.isbn = r.isbn
group by b.pub_year
having b.pub_year <= 2021 and b.pub_year > 0;

-----------------------------------------------
-- 6. How many books were published each year?
select pub_year, count(isbn)
from books b
group by pub_year
having pub_year > 0 and pub_year <= 2021
order by count(isbn) desc;

-----------------------------------------------
-- 7. Which publishers release the most book per year?
-- query which publishers release the most books
select publisher, count(publisher)
from books
group by publisher
order by count(publisher) desc
limit 15;

-----------------------------------------------
--8. Which publishers are rated the highest and lowest?
-- select publisher with highest average rating and more than 50 reviews
select publisher, avg(rating) as avg_rating, count(rating) as num_of_ratings
from books b
inner join ratings r on b.isbn = r.isbn
group by publisher
having count(rating) > 50
order by avg(rating) desc
limit 1;

-- select publisher with lowest average rating and more than 50 reviews
select publisher, avg(rating) as avg_rating, count(rating) as num_of_ratings
from books b
inner join ratings r on b.isbn = r.isbn
group by publisher
having count(rating) > 50
order by avg(rating)
limit 1;
-----------------------------------------------
-- 9. Which authors have the most books?
select book_author, count(isbn)
from books
group by book_author
order by count(isbn) desc
limit 15;

-----------------------------------------------
-- 10. Which authors have the most reviews?
-- Is there any correlation to the authors with the most books?
-- create a view with the query information of authors and their rating counts
create view rating_counts as
select b.book_author, count(r.rating) as num_of_ratings
from books b
inner join ratings r on b.isbn = r.isbn
group by book_author;

select b.book_author, b.num_of_books, r.num_of_ratings
from (select book_author, count(isbn) as num_of_books 
      from books
      group by book_author
     ) as b
inner join rating_counts r on b.book_author = r.book_author
order by num_of_books desc
limit 30;

-----------------------------------------------
-- Bonus: Use a window function to show average ratings per author.
with windowed as(
    select b.book_author, b.book_title,
           round(avg(r.rating) over(partition by(b.book_author)), 2) as avg_author_rating
    from books b
    inner join ratings r on b.isbn = r.isbn
)

select * from windowed
where avg_author_rating < 8 and avg_author_rating > 7
limit 20;