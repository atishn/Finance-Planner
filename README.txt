HugePlanner README
==================
Getting Started
---------------

sudo apt-get install python-devsudo
sudo apt-get install libffi-devsudo
sudo apt-get install libmysqlclient-dev

sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev


- cd <directory containing this file>

- python setup.py develop


1. Create database hr;
2. Create user 'hup' identified by 'password123'
3. grant all privileges on hr.* to hup@localhost;


- initialize_hr_db development.ini

- pserve development.ini

