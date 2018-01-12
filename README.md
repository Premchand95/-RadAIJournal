# Flaskapp
```
Utilities Used:
```
Python 3.6

Mysql


Command to install python modules:


py -m pip install module_name

```
modules used:
```


flask

flask-mysql

passlib

wtforms

functools 

flask_mail

itsdangerous

Example:  py -m pip install flask-mysql


```
Database:
```
CREATE DATABASE flaskapp;

USE flaskapp;

CREATE TABLE USER(first_name VARCHAR(30) NOT NULL,middle_name VARCHAR(30),last_name VARCHAR(30),npi VARCHAR(30),doctor VARCHAR(30),radiologist VARCHAR(30),training VARCHAR(30),clinical_practice VARCHAR(30),clinical_specality VARCHAR(30),institution_type VARCHAR(30),country VARCHAR(30),state VARCHAR(30),email VARCHAR(30),PRIMARY KEY (email));

SELECT * FROM USER;


