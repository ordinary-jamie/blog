---
id: 4
title: SQL Server & Docker
date: 2021-07-06
preview: |
  Setting up a persistent SQL Server Docker container
section: dev
tags:
  - devops
draft: false
type: blog
---

[TOC]

In this tutorial, we're going to setup a docker image for running a SQL-Server database.
This will be useful for prototyping/developing containerized applications that require a database and where local storage options such as SQLite won't do.

In the end, we'll have a simple docker image that can be brought up with docker-compose alongside your app.
We'll make sure its easy to configure, and that the persistent data can be managed easily.

## Downloads and Installations

- **Install: Docker Desktop**: this will provide the docker engine and the useful desktop interface for managing your containers and images. See [docker.com](https://www.docker.com/products/docker-desktop).
- **Install: Microsoft SQL Server Management Studio**: this is the tool you will use to interface with the database directly. See [docs.microsoft.com](https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver15)
- **Download: Docker Image `mcr.microsoft.com/mssql/server`**: this is the docker image we will be using to create our SQL-Server container. See [hub.docker.com](https://hub.docker.com/_/microsoft-mssql-server)

## Project layout

I like to keep this database docker image, or similar images, in its separate `db/` folder as I can organise it with other applications, like a web-service for example.

This project will be laid out as follows:

```
root
│
├─ db
│   ├─ entrypoint.sh
│   ├─ init.sql
│   ├─ mssql.Dockerfile
│   └─ mssql.env
│
├─ db-data
├─ .dockerignore
└─ docker-compose.yml
```

## The Docker Image

The docker image is fairly straight-forward, it consists of 4 key files in the `db/` dir:

- `mssql.Dockerfile`: The Dockerfile itself
- `init.sql`: An initialisation script to setup the initial schema
- `mssql.env`: For environement variables (to configure the database)
- `entrypoint.sh`: To determine if database initialisation needs to be run or not

### `db/mssql.Dockerfile`

Simply building from Microsoft's sql server image, copying over our files described above, and correctly setting the entrypoint to our script.

``` dockerfile
FROM mcr.microsoft.com/mssql/server
COPY . /
ENTRYPOINT [ "/bin/bash", "entrypoint.sh" ]
CMD [ "/opt/mssql/bin/sqlservr" ]
```

### `db/init.sql`

This is up to you, it should contain the schema of your database that needs to be setup for your project.

As an example, let's just make one single user table:

``` sql
drop table if exists [dbo].[user];
go
create table [dbo].[user] (
    id int identity(1,1) primary key
    ,username varchar(50) not null
    ,email varchar(100) not null
);
go
```

### `db/mssql.env`

This is where we will keep all of our key environment information such as credentials for our database.

```
SA_PASSWORD=
ACCEPT_EULA="Y"
DB_NAME=learnsql
DB_USER=
DB_PASSWORD=
```

Fill in the values as you deem fit, and make sure to keep this secret!

Below is a table of their usage:

| Env. var      | Usage                                                                                                                                            |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| `SA_PASSWORD` | This is a MS-SQL environment variable for system administration                                                                                  |
| `ACCEPT_EULA` | This is a MS-SQL environement variable to confirm the acceptance of the End-User Licensing Agreement. Required setting for the SQL Server image. |
| `DB_NAME`     | The database to initialise, this is the database that the `init.sql` script will run under                                                       |
| `DB_USER`     | The SQL credentials to login to the database                                                                                                     |
| `DB_PASSWORD` | The SQL credentials to login to the database                                                                                                     |



### `db/entrypoint.sh`

This script is used to determine if the database is configured or not yet.
We will need this because we want persistent database storage, even despite the container being taken offline.
To achieve this, we rely on a simple 'flag-file' (`/tmp/app-initialized`) in the persistent storage to indicate if this is the first time running this container, or if it is a reboot.

``` bash
#!/bin/bash
set -e
SA_PASSWORD=${SA_PASSWORD}

if [ "$1" = '/opt/mssql/bin/sqlservr' ]; then
  # If this is the container's first run, initialize the application database
  if [ ! -f /tmp/app-initialized ]; then
    # Initialize the application database asynchronously in a background process.
    # This allows:
    #   a) the SQL Server process to be the main process in the container, which allows graceful shutdown and other goodies, and
    #   b) us to only start the SQL Server process once, as opposed to starting, stopping, then starting it again.
    function initialize_app_database() {

      # Wait a bit for SQL Server to start. SQL Server's process doesn't provide a clever way to check if it's up or not,
      # and it needs to be up before we can import the application database
      sleep 30s

      # run the setup script to create the DB and the schema in the DB
      /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d master -Q "CREATE LOGIN ${DB_USER} WITH PASSWORD = '${DB_PASSWORD}';"

      # TODO: sysadmin is only needed for Azure Data Studio, an active bug prevents the Object Explorer from loading for any login that does not have sysadmin access
      # see: https://github.com/microsoft/azuredatastudio/issues/13915
      /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d master -Q "ALTER SERVER ROLE sysadmin ADD MEMBER ${DB_USER};"
      /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d master -Q "CREATE DATABASE ${DB_NAME};"
      /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d master -Q "ALTER AUTHORIZATION ON DATABASE::${DB_NAME} TO ${DB_USER};"
      /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d master -i init.sql

      # Note that the container has been initialized so future starts won't wipe changes to the data
      touch /tmp/app-initialized
    }
    initialize_app_database &
  fi
fi
exec "$@"
```

### Testing

With this all setup, you can do a quick test to see if it all works:

``` bash
cd root/db/
docker build -f mssql.Dockerfile -t mssql-test:latest .
```

You should see something along the lines of:

``` bash
[+] Building 0.1s (7/7)
 => [internal] load build definition from mssql.Dockerfile
 => => transferring dockerfile: 37B
 => [internal] load .dockerignore
 => => transferring context: 2B
 => [internal] load metadata for mcr.microsoft.com/mssql/server:latest
 => [internal] load build context
 => => transferring context: 125B
 => [1/2] FROM mcr.microsoft.com/mssql/server
 => CACHED [2/2] COPY . /
 => exporting to image
 => => exporting layers
 => => writing image sha256:1d1e1ed799ad61d43e3a37a18...
 => => naming to docker.io/library/mssql-test:latest
```

Then to run the image as a container, we will use the command:

```
docker run -p 1433:1433 --env-file mssql.env mssql-test:latest
```

If all goes well, you should see a bunch of lines printing to stdout. When you see that SQL-Server has started up the database, then you can try connect to it:

``` bash
spid10s     Starting up database 'tempdb'.
spid10s     The tempdb database has 1 data file(s).
spid27s     The Service Broker endpoint is in disabled or stopped state.
spid27s     The Database Mirroring endpoint is in disabled or stopped state.
spid27s     Service Broker manager has started.
spid8s      Database 'msdb' running the upgrade step from version 902 to version 903.
spid8s      Database 'msdb' running the upgrade step from version 903 to version 904.
spid8s      Recovery is complete. This is an informational message only. No user action is required.
spid23s     The default language (LCID 0) has been set for engine and full-text services.
spid23s     The tempdb database has 2 data file(s).
```

To connect to the database, simply open **Microsoft SQL Server Management Studio** (SSMS) and enter the values when trying to connect to a new server:

| Field              | Value                                                    |
|--------------------|----------------------------------------------------------|
| **Server type**    | Database Engine                                          |
| **Server name**    | 127.0.0.1, 1433                                          |
| **Authentication** | SQL Server Authentication                                |
| **Login**          | (Whatever you set `DB_USER` to equal in `mssql.env`)     |
| **Password**       | (Whatever you set `DB_PASSWORD` to equal in `mssql.env`) |

Don't forget to stop and remove the image when you're done with it:

``` bash
docker ps -a -q --filter="name=mssql-test:latest"
docker rmi mssql-test:latest
```

## With docker-compose

Of course, because we didn't specify a volume in our `docker run` command, we won't have persistent storage.
When you shut down this container, all of the tables and table data will be lost.

A handy way to get around this, is by using [bind-mounted volumes](https://docs.docker.com/storage/bind-mounts/).
Using bind-mounts has its limitations, but it does remove a lot of docker abstraction and keep it easier to manage the persistent storage.
This is most suitable for development/prototyping projects.

### `docker-compose.yml`
Now this is simple, we will simply use `docker-compose` to manage this.

In your root folder:

``` yaml
version: '3'

services:
  db:
    build:
      context: ./db
      dockerfile: mssql.Dockerfile
    env_file:
      - db/mssql.env
    ports:
      - 1433:1433
    volumes:
      - ./db-data:/var/opt/mssql
```

### Running

Now, when we want to `up` the container:

```
cd root/
docker-compose up
```

N.b. make sure your previous container during testing is down, or you might see `0.0.0:1433 failed: port is already allocated`.

With this image up -- similar to the testing section -- open **Microsoft SQL Server Management Studio** (SSMS) and enter the values when trying to connect to a new server:

| Field              | Value                                                    |
|--------------------|----------------------------------------------------------|
| **Server type**    | Database Engine                                          |
| **Server name**    | 127.0.0.1, 1433                                          |
| **Authentication** | SQL Server Authentication                                |
| **Login**          | (Whatever you set `DB_USER` to equal in `mssql.env`)     |
| **Password**       | (Whatever you set `DB_PASSWORD` to equal in `mssql.env`) |


You'll notice that the folder `db-data/` will be populated now. This is where the database storage is now pointing to.

## Wrap-up
Now we have a simple database container we can use for prototyping/development and persist the storage.

You can try add data/tables to the database, shut-it down, restart it, and the data will still all be there.