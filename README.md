# rsnapshot-docker-compose-backup

## Anforderungen

### Sachen für jeden Container

## Aufbau

Immer   Aufgabe  
    In jedem Unterordner schauen ob es docker-compose ist  
√   docker-compose.yml sichern (ist besser als config wegen Kommentaren)  
√   source env vars  
    ggf. dump der Anwendung (z.B. mysqldump)  
√   jeden Service der Compose Datei anschauen  
√       Image  

### Ordnerstruktur

/config-root  

### Compose spezifisch Backup

yml file format

[ContainerName]

RuntimeBackup (z.B. minecraft message: 1 min to stop)

PreStop  
Stop  
  
PreBackup  
Backup  
PostBackup  
  
Restart  
PostRestart  
  
[ContainerName2]
  
RuntimeBackup  
  
PreStop  
Stop  
  
PreBackup  
Backup  
PostBackup  
  
Restart  
PostRestart  
  
### Einbindung in Rsnapshot

Beispiel für container-spezifische Sicherung (MariaDB):
```
backup_script	/usr/bin/docker exec mariadb /usr/bin/mysqldump -u root --password=XXX --databases nextcloudNC --default-character-set=utf8mb4 > backup_nextcloudNC.sql	localhost/special/docker/${CONTAINER_NAME}/backup-nextcloudNC/ 
```

Helper-Skript in Rsnapshot nutzen:
```
include_conf    `/bin/bash /root/skripte/docker-containers/001_utils/containerbackup_helper.sh`
```

Ansatz für Helper-Skript:
```
#!/bin/bash
# Prints all backup commands from underlying files to STDOUT for usage with Rsnapshot

ENV_FILENAME=.env
BACKUPSCRIPT_FILENAME=containerbackup.conf

cd /root/skripte/docker-containers/

for dir in */
do
  PATH_ENV=$dir$ENV_FILENAME
  PATH_BACKUPSCRIPT=$dir$BACKUPSCRIPT_FILENAME
  if [[ -e $PATH_ENV ]] && [[ -e $PATH_BACKUPSCRIPT ]]; then
    # Directory does contain both ENV_FILENAME and BACKUPSCRIPT_FILENAME
    # Exports all variables from docker-compose's .env file and ignores comments
    source ${PATH_ENV}
    export $(grep --regexp ^[A-Z] ${PATH_ENV} | cut -d= -f1)
    # Substitutes placeholders inside the backup script with the variables value from ENV_FILENAME
    envsubst < $PATH_BACKUPSCRIPT
  fi
done
```
