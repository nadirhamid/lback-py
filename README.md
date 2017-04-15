LBack - a backup tool for linux
===============================

![alt tag](./lback.png)

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
git clone https://github.com/nadirhamid/lback-py
cd lback-py
git submodule update --init
pip install -r requirements.txt
python setup.py build
python setup.py install
```

LBACK server
------------------------------------------------------

Running the lback server is required for local and non-local
backup/restores. Please start the Lback server with

```
lback-server
```

You will also need to start the local agent.

```
lback-agent
```
    
Regular Backups (Local)
-------------------------------------------------------

to run a local backup you can use:

```
lback backup "./folder"
```

this will instruct the program to backup the ./folder" locally
and when done send a success message telling you it is complete.

Regular Restores (Local)
---------------------------------------------------

to restore a folder having backed it up, you need
to have its id. Which can be found in the database or
whenever a transaction is complete. For example:

```
lback restore "./folder"
```



this will fully restore this archive back to its initial
state. Should it result in any error, it will throw a warning
telling you what went wrong.

Other Commands
------------------------------------------------------

Removing a Backup

```
lback rm "./folder"
```

Listing all Backups

```
lback ls
```

Moving a backup

```
lback mv ./folder ./new_folder
```

REMOTE agents
------------------------------------------------------

To start an agent. Please use

```
lback-agent --host {host} --port {port}
```

Register this agent

```
lback agent-add {host} {port}
```

Verify the agent is registered and alive

```
lback agent-ls
```

NOTE: When you register agents your backups will be stored across
all agents. And by default your CLI lback will use all agents
for backup/restore lookup, moving, etc.

More coming soon..


