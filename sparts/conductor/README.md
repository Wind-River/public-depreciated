## The Conductor

The conductor is a server side component written in Go that provides various services to the different running components of a supply chain network. For example, the following api call provides the entry point for the ledger:
```
  /api/sparts/ledger/address
```
Because it provides services to all the other applications and blockchain nodes it must be started before the others. Each of the other services and applications must register with the conductor first. Therefore the conductor's IP address and listening port needs to be known by all the participants. 

The conductor provides all services via a RESTful API. You can find the documantation in the /data directory or by making the following  request:

http://[conductor-host-address]/api/sparts/help



## Build & Run

The conductor is written in Go and therefore you will need to compile it for your platform. If Go is not installed you can find the instructions here:
```
https://golang.org/doc/install#install
```

Installing the following dependencies:

```
go get github.com/gorilla/mux
go get github.com/russross/blackfriday
go get github.com/nu7hatch/gouuid
go get github.com/mattn/go-sqlite3   ## You may need to install gcc for this dependency
```

In the conductor directory execute the following build command

```
go build -o conductor
```

Copy the conductor and directory data/ to a directory where you want to run it and execute the conductor:

```
conductor  /data
```

There is a configuration file conductor_config.json in directory /data that you can set certain parameters such as the the ip port to listen on, to turn on or off verbose message mode and so forth. 

```
    "database_file":            "./data/db/conductor_data.db",
    "help_file":                "./data/docs/SpartsConductorAPI.md",
    "http_port":                8080,
    "ledger_api_passwd":        "6172d350-6959-4e3d-7906-6feb99d9030e",
    "debug_on":                 true,
    "debug_db_on":              true,
    "verbose_on":               true,
    "config_reload_allowed":    true
```


The first time you run the conductor it will create a database file in subdirectory /data so make sure the program has read/write permissions. 



