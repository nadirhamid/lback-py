LBack - a backup tool for linux
===============================

![alt tag](http://infinitet3ch.com/assets/lback-logo.png)


A Simple way to do remote / local backups. Hassle free,
using your favorite db. 

Requirements
------------------------------------------------------
```
+ Python >= 2.7
+ Pip for Python 2.7 
+ MySQL
```

Installing
------------------------------------------------------

```
make  
```
    	

Regular Backups (Local)
-------------------------------------------------------

to run a local backup you can use:

```
lback --client --local --backup --folder "/folder/"
```

this will instruct the program to backup the folder/" locally
and when done send a success message telling you it is complete.

Regular Restores (Local)
---------------------------------------------------

to restore a folder having backed it up, you need
to have its id. Which can be found in the database or
whenever a transaction is complete. For example:

```
lback --client --local --restore --id "cb73eb0155af5a3da3bb4a63646b40201ab650c4"
```

OR short ids

```
lback --local --restore --id "cb73eb0"
```



this will fully restore this archive back to its initial
state. Should it result in any error, it will throw a warning
telling you what went wrong.

REMOTE backups:

To start a server. You may use:

```
lback --server
```

OR equivalently:

```
lback-server
```


this will start the program in server mode and listen to any
connections

IMPORTANT: For the client, a running server 'must' be set up for remote backups.
You can set this in "settings.json". "server_ip" and "server_port"
the client will attempt to communicate on this tcip channel.
The commands for a restore and backup are analagous to local. For example:

```
lback --client --remote --backup --folder "/folder/"
```

```
lback --client --remote --restore --id "cb73eb0155af5a3da3bb4a63646b40201ab650c4"
```



When done successfully, 
database transactions kept should be similar on both the client and server.

More on servers:
-------------------------------------------------

This program makes no optimizations for server vs client. And both
machines can run as either. The implementor must decide which to
use as a server, client. Moreover settings.json 'should' be identical
on both machines.

Whenever a client successfully transfers data to the server. The data 'will'
not be available immediately. Full propagation can take time depending
on the folder's size.

Benchmark results:

108 megabytes (transfering XUL SDK)
took ~ 3 minutes to archive and delivery
another 3 minutes


Generating a list of backups:

To fetch all backups to date, you can use:

```
lback --list
```
