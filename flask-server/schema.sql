drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null,
  password text not null,
  mail text not null
);
drop table if exists files;
create table files (
  id integer primary key autoincrement,
  id_usr integer not null,
  folder integer not null,
  name text not null,
  type text not null
);