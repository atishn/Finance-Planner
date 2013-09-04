HugePlanner README
==================
Getting Started
---------------

sudo  easy_install pip
sudo pip install pyramid_jinja2
pip install supervisor --upgrade

// If Jinja2 is not installed: http://jinja.pocoo.org/docs/intro/#installation
// Jinja2-2.6
//- cd <directory containing this file>

//This may need to be run in sudo
- python setup.py develop

In MySql
1. Create database hr;
2. Create user 'hup' identified by 'password123';
3. grant all privileges on hr.* to hup@localhost;
4. grant usage on *.* to hup@localhost identified by 'password123';

//IF the following error occurs:
//    Library not loaded: libmysqlclient.18.dylib
//THEN TRY
//   sudo ln -s /usr/local/mysql/lib/libmysqlclient.18.dylib /usr/lib/libmysqlclient.18.dylib
- initialize_hr_db development.ini

- pserve --reload development.ini



For ubuntu box.

sudo apt-get install python-dev python-setuptools libffi-devs libmysqlclient-dev
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
