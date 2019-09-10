# Blockchain Dashboard #

## Installation ##

#### Install dependencies ####

The following are required packages for Debian-based systems. Open a terminal as root and run the following commands:

    $ apt-get update
    
    $ apt install git python3 python3-pip apache2 libapache2-mod-wsgi-py3

    $ pip3 install --upgrade pip
    
    $ pip3 install flask requests

## Configure the web server ##
#### Clone server files ####
Run the following commands to clone the sparts project in `/var/www/sparts` folder.

    $ git clone https://github.com/Wind-River/software-parts-ledger /var/www/sparts

#### Listen on desired port ####

If you require your app to run on a different port than port 80, you should make sure that Apache listens to incoming traffic on that port. open `/etc/apache2/ports.conf` with a text editor and add the following line after `Listen 80`:

    Listen 80
    Listen 7000
    
You may open as many ports as you need based on how many different concurrent apps you need to run via Apache.

#### Create Apache configuration file ####
In this example, we serve this app on localhost with port 6000. You can choose whichever port you like. If you have several sparts apps running on the same machine, you can do this same procedure and create a similar config file but with different ports. Browse to `/etc/apache2/sites-available/` and create a file in there called `blockchain-dashboard.conf` with the following content:

    <VirtualHost *:7000>
    ServerName localhost

    <IfModule !wsgi_module>
    LoadMOdule wsgi_module wsgi.so
    </IfModule>

    WSGIScriptAlias / /var/www/sparts/apps/blockchain-dash/bcdash.wsgi

    <Directory /var/www/sparts/apps/blockchain-dash>
        <Files bcdash.wsgi>
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

#### Configure Flask ####

Create a file `config.py` in `/var/www/sparts/apps/blockchain-dash` and paste the following in it:

    DEBUG = True
    APP_PATH = "/var/www/sparts/apps/blockchain-dash"
    BLOCKCHAIN_API = "http://147.11.176.31:3075/api/sparts"
    DEFAULT_API_TIMEOUT = 45
    BYPASS_API_CALLS = False

`BLOCKCHAIN_API` is the hard-coded address of the conductor service.

`DEFAULT_API_TIMEOUT` is the number of seconds to wait for a response in an API call.

`BYPASS_API_CALSS` is a flag to bypass making API calls for debugging purposes.


#### Retart Apache service ####
    $ service apache2 restart
