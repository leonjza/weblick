# Weblick

![logo](http://i.imgur.com/j0zMRrs.png)

###### This is an experiment

### About
This tool basically scratches an itch I have had for quite some time. I have asked myself plenty of times; What
information do some high profile sites simply *give away*? By *give away*, I actually mean accidentally leak. Stuff such as headers,
cookies, HTML comments and SSL certificates all have plenty of opportunity to contain some information an administrator or
developer may have not thought through. With Weblick, I hope to scrape all of the possible information into a database
for later analysis.

### Installation
I'll suggest you create yourself a new python [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/).
This will allow you to install all of the required dependencies without touching your operating systems base python installation.

Weblick supports many database backends as it makes use of the [peewee ORM](https://peewee.readthedocs.org/en/latest/). At the moment
though, only SQLite and MySQL/MariaDB has been tested. Theoretically PostgresSQL should work do, but some work is needed to
add support for that to this tool.

##### Clone
 - Clone the repository with:
 
 ```bash
 $ git clone https://github.com/leonjza/weblick.git
 ```
 
 This will leave you with a new directory called `weblick`
 
##### Dependencies
Weblick has a few dependencies that need to be resolved. All of these are defined in the [requirements.txt](https://github.com/leonjza/weblick/blob/master/requirements.txt) file.  
**Recommended:** Create a new python virtual environment with `$ virtualenv env` in the `weblick` directory. Once this is
finished, source the new environment with `$ source env/bin/activate`. Your python interpreter will now use the one in your
newly installed environment.
  
  - Install the required dependencies with:
  
  ```bash
  $ pip install -r requirements.txt
  ```
  
##### DB Setup
If you are going to be using the MySQL/MariaDB backend, prepare a database and credentials so that Weblick may create tables,
insert and update there. Update the `[mysql]` section in the [settings.ini](https://github.com/leonjza/weblick/blob/master/settings.ini) file too.  
For the default SQLite driver no configuration should be needed. The database file for SQLite will live in the `var` directory.

 - With the database configured in the `settings.ini` file, create the schema with:

 ```bash
 $ python lick.py setupdb
 ```

##### Source Data
This tool was written to use the [Aleksa Top 1 Million](https://support.alexa.com/hc/en-us/articles/200461990-Can-I-get-a-list-of-top-sites-from-an-API-) data export.

 - Download the source data to the `var/` directory with:

 ```bash
 $ curl -O http://s3.amazonaws.com/alexa-static/top-1m.csv.zip
 ```

 - Extract the downloaded `zip` file:
 
 ```bash
 $ unzip top-1m.csv.zip
 ```
 
 **Note:** If you prefer to have this csv somewhere else, just update the `settings.ini` `aleksa_csv` section.

**That should be it**. You should now be able to run it with `$ python lick.py` and watch your database grow!

### Future / TODO

With all of the information gathered, I am thinking of attempting to make it possible to alert if things have changed. Ie;
 - New / Missing cookies
 - New / Missing HTTP headers
 - New / Missing comments in HTML sources
 - SSL certificate expiry / changes
 
I should also make it so that a custom CSV can be used as a commandline argument.
