HugePlanner README
==================
Getting Started
---------------

sudo  easy_install pip
sudo pip install pyramid_jinja2
pip install supervisor --upgrade

- cd <directory containing this folder>

- python setup.py develop

In MySql
1. Login to root/admin
2. Create database hr;
3. Create user 'hup' identified by 'password123';
4. grant all privileges on hr.* to hup@localhost;
5. grant usage on *.* to hup@localhost identified by 'password123';


- initialize_hr_db development.ini

- pserve --reload development.ini



For ubuntu box.

sudo apt-get install python-dev python-setuptools libffi-devs libmysqlclient-dev
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev