# rsnapshot-docker-compose-backup

This program can be used to create config to back up docker compose container with rsnapshot.

## Get Started

### Prerequisites

This script expects a folder structure in the following scheme:  
``` 
docker-compose-root/  
  - projectDir1/  
      - docker-compose.yml  
  - projectDir2/  
      - docker-compose.yml  
      - ...  
  - ...
``` 
The config file for this script has to be in the docker compose root.

### Quick Start

1. Execute the Script
2. Examine Output
3. Change newly generated backup.ini in docker compose root directory if necessary
4. Create backup.ini files in projectDirs that need special configuration

## Steps

The Backup process is divided in steps.
There are 7 Steps:
- runtime_backup 
- pre_stop
- stop
- pre_backup 
- backup
- post_backup 
- restart
- post_restart

The steps are executed in that order.  
The Idea is that the first step `runtime_backup` can be used for everything where the service can still be running, like backup of the image.  
The `stop` step can be used to stop the container, so that the `backup` step can be used for a backup of the volumes.  
After that the container can be restarted in the `restart` step.  

Every command that gets executed in one of the steps is defined in the config file and can be changed fit your need.

## Config File

This script is completely controlled via config files. There are two different type of config files:
1. global config
2. project level config

The **global config** is created with the first start of the script. 
It contains the default configuration for all projects and some more settings.  
The **project level config** is not necessary but can be used to override the default configuration for individual services.

All config files are named backup.ini. The config file is divided in different sections and all entries are in the `key=value` schema like in other .ini files. 
All keys and sections are case-insensitive.
### Default files
#### Global config
```ini
#Start of main section
[default_config]
#Specific commands for each step
backup = backup	$projectFolder	$backupPrefixFolder/$serviceName/projectDir
[default_config.settings]
logTime = True
[default_config.actions]
stopContainer = true
volumeBackup = true
yamlBackup = false
[default_config.vars]
prefix = docker-compose

[predefined_actions]
[predefined_actions.volumeBackup]
backup = backup	$volumes.path	$prefix/$serviceName/$volumes.name
    
[predefined_actions.yamlBackup]
runtime_backup = backup	$projectFolder	$prefix/$serviceName/yaml	+rsync_long_args=--include=*.yml,+rsync_long_args=--include=*.yaml

[predefined_actions.stopContainer]
stop = backup_exec	cd $projectFolder; /usr/bin/docker-compose stop
restart = backup_exec	cd $projectFolder; /usr/bin/docker-compose start

```
#### Project level config
```ini
[Nextcloud]
pre_backup=backup_exec  docker exec -u www-data nextcloud /var/www/html/occ maintenance:mode --on
post_backup=backup_exec docker exec -u www-data nextcloud /var/www/html/occ maintenance:mode --off

[Nextcloud.Actions]
yamlBackup=true
stopContainer=false
[MariaDB]
runtime_backup=backup_script   $projectFolder/dump_database.sh    /backupDir
pre_stop=backup_exec  docker exec -u www-data nextcloud /var/www/html/occ maintenance:mode --on
post_restart=backup_exec docker exec -u www-data nextcloud /var/www/html/occ maintenance:mode --off
```
### Sections
The **global config** file has to main sections:
    - default_config
    - predefined_actions

The **project level config** file has a main section for every service that should be specially configured.  

The main sections from the **project level config** and the `default_config` section of the **global_config** have the same structure.

It is possible to define commands that should be executed directly in this section. 
The commands are defined with the step, where they apply, as key and the rsnapshot command as value. 
The command can be multiple lines long.

The section also has different subsections:
- `{main_section}.Actions`: This Section defines which of the actions that are defined in the global config should be activated or deactivated. That can be done with the action Name as Key and `true` or `false` as value.
- `{main_section}.Vars`: This Section is used to define variables that can be used in rsnapshot commands.
Variables can be defined with `{var_name}={value}`. The Variables can only be used for simple text replacement and no complex actions. Some variables are predefined. They are listed in the default Variables section.
- `{main_section}.Settings`: This Section is used to set settings. All supported settings are documented in the following table.

| Setting | Description | Default Value | 
| ----------- | ----------- | ----- |
| logTime | If enabled adds backup steps to allow logging how long steps take | True |
| onlyRunning | If enabled only creates backup config for containers that are currently running | True |

In the **global config** is a second main section with the name `predefined_actions`. 
This section contains actions that can be activated in the before explained `.Actions` section. 
The actions can be used to modularise the commands and for a possibility to disable actions on service level that are activated in the global config. 

Every action has an own section with the name `prefefined_actions.{action_name}`. 
This section can contain RSnapshot commands like the other main section. 
It is also possible that an action has subsections that are defined like this: `actions={one ore more actions}`. 
These subsections can only be one level deep. 

### Default Variables
Some Variables are predefined and can be used in the backup.ini without being defined explicitly. These are the variables:

- $serviceName: The name of the Service
- $containerName: The name of the Container
- $projectName: The name of the Project
- $containerID: The ID of the Container
- $projectFolder: The Path of the Project Folder
- $volumes: A List of the volumes that are defined for the service. The backup commands are copied for each volume.
