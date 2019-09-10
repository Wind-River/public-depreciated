# Software Parts Catalog #

## Installation ##

#### Install dependencies ####

The following are required packages for Debian-based systems. Open a terminal as root and run the following commands:

    $ apt-get update

    $ apt install git python3 python3-pip apache2 libapache2-mod-wsgi-py3 postgresql postgresql-contrib

    $ pip3 install --upgrade pip

    $ pip3 install flask sqlalchemy psycopg2 requests

## Start Services ##

#### Start Apache service ####
    $ service apache2 start

#### Start Postgres database ####
First, determine the version of Postgres cluster installed by running

    $ pg_lsclusters

The output will be similar to `9.5 main    5432 down   postgres /var/lib/postgresql/9.5/main /var/log/postgresql/postgresql-9.5-main.log`. Here, `9.5` is the version. Run the following command to start the cluster:

    $ pg_ctlcluster <version> main start


## Create the database ##
Start by selecting a username and a password for a database account. You should also select a name for the database. As an example, here we choose the username to be `sparts_admin`, password is `mypassword`, and the database is called `sparts_catalog`. Run the following commands to create the database and an admin user.

    $ su - postgres

    $ createdb sparts_catalog

    $ psql sparts_catalog

    $ create user sparts_admin with password 'mypassword';

    $ grant all privileges on database "sparts_catalog" to sparts_admin;

    $ \q

    $ exit

## Configure the web server ##
#### Clone server files ####
Run the following commands to clone the sparts project in `/var/www/sparts` folder.

    $ git clone https://github.com/Wind-River/software-parts-ledger /var/www/sparts

#### Listen on desired port ####

If you require your app to run on a different port than port 80, you should make sure that Apache listens to incoming traffic on that port. open `/etc/apache2/ports.conf` with a text editor and add the following line after `Listen 80`:

    Listen 80
    Listen 6000

You may open as many ports as you need based on how many different concurrent apps you need to run via Apache.

#### Create Apache configuration file ####
In this example, we serve this app on localhost with port 6000. You can choose whichever port you like. If you have several sparts apps running on the same machine, you can do this same procedure and create a similar config file but with different ports. Browse to `/etc/apache2/sites-available/` and create a file in there called `sparts_catalog.conf` with the following content:

    <VirtualHost *:6000>
    ServerName localhost

    <IfModule !wsgi_module>
    LoadMOdule wsgi_module wsgi.so
    </IfModule>

    WSGIScriptAlias / /var/www/sparts/apps/catalog/catalog.wsgi

    <Directory /var/www/sparts/apps/catalog>
        <Files catalog.wsgi>
            Require all granted
        </Files>

        Order allow,deny
        Allow from all
    </Directory>

    </VirtualHost>

#### Enable this configuration ####
To enable the above config file, you must make a soft link in `/etc/apache2/sites-enabled` to this file. Run the following:

    $ cd /etc/apache2/sites-enabled

    $ ln -s ../sites-available/sparts_catalog.conf

#### Disable the default app ####
Apache comes bundled with a 'Hello, World' type app that only shows the user that Apache is running. We will disable this using the following command:

    $ rm /etc/apache2/sites-enabled/000-default.conf

#### Prepare server directories ####
Now, we create two directories for upload data and artifacts data. Upload directory is where envelopes get copied when the user uploads an envelope. Artifacts folder is used to hold the artifacts after they are extracted from the envelopes. You can choose the path of these directories. Here as an example, we use `/var/www/sparts/apps/catalog/upload` for the upload folder and similarly `/var/www/sparts/apps/catalog/artifacts` for the artifacts directory. We also have to make sure `www-data` is the owner of these directories so that Apache has the permission to write to them.

    $ mkdir -p /var/www/sparts/apps/catalog/upload

    $ mkdir -p /var/www/sparts/apps/catalog/artifacts

    $ chown www-data:www-data /var/www/sparts/apps/catalog/upload

    $ chown www-data:www-data /var/www/sparts/apps/catalog/artifacts

#### Configure Flask ####

Create a file `config.py` in `/var/www/sparts/apps/catalog` and paste the following in it:

    DEBUG = False
    APP_PATH = "/var/www/sparts/apps/catalog"
    UPLOAD_FOLDER = "/var/www/sparts/apps/catalog/upload"
    ARTIFACT_FOLDER = "/var/www/sparts/apps/catalog/artifacts"
    SAMPLE_DATA_FOLDER = "/var/www/sparts/apps/catalog/sample-data"
    DATABASE_URI = "postgresql://sparts_admin:mypassword@localhost:5432/sparts_catalog"
    BLOCKCHAIN_API = "http://147.11.176.31:3075/api/sparts"
    DEFAULT_API_TIMEOUT = 45
    BYPASS_API_CALLS = False
    BYPASS_LEDGER_CALLS = False
    PRODUCTION = False

`BLOCKCHAIN_API` is the hard-coded address of the conductor service.

`DEFAULT_API_TIMEOUT` is the number of seconds to wait for a response in an API call.

`BYPASS_API_CALSS` is a flag to bypass making API calls for debugging purposes.

`BYPASS_LEDGER_CALLS` is a flag to bypass making calls to the ledger service.

`PRODUCTION` is a boolean indicating whether this is the production server.


#### Restart Apache ####
Restart the webserver for changes to take effect.

    $ service apache2 restart

## Configure the database ##
Next we need to create the tables. Run the following commands to do so:

    $ cd /var/www/sparts/apps/catalog

    $ python3

	>>> from sparts.database import init_db

	>>> init_db()

	>>> exit()

At this point, you should be able to browse the app via any browser at http://localhost:6000.


## Populate database and blockchain with sample data (*optional) ##

Visit this url (change the port according to your configuration) `http://localhost:6000/api/sparts/reset`. It should return the following

    {
      "status": "success"
    }
