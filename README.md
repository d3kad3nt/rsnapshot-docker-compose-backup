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
  
### Backup Dateien

Die Backup-Dateien für die Docker-Container müssen in dem gleichen Verzeichnis wie die docker-compose.yml Dateien liegen und backup.ini heißen.  
Struktur:
Die Struktur der Datei ist eine INI Datei, welche in verschiedene Sektionen unterteilt sein kann. Hierbei ist jede Sektion für einen Container in der compose Datei. Wenn in der Comose-Datei nur ein einziger Container definiert ist, dann kann die Sektion weggelassen werden.

Innerhalb einer Sektion kann angepasst werden wie das Backup des Containers abläuft. Wenn ein Schritt nicht angepasst wird, dann wird der Schritt so ausgeführt wie er in der default-config definiert ist.  
Schritte können angepasst werden indem der Schritt als Key genannt wird und dann als Value der angepasste Schritt beschrieben wird. Hierbei kann ein Value aus mehreren Zeilen bestehen, wenn die weiteren Zeilen eingerückt sind.  
In diesen Zeilen sind die Befehle die von RSnapshot ausgeführt werden sollen definiert. An dieser Stelle können normale RSnapshot befehle wie "backup" oder "backup_script" verwendet werden. Des weiteren ist es aber auch möglich einige erweiterungen zu verwenden die in RSnapshot Befehle umgewandelt werden.  
Es existieren folgende Erweiterungen:
  "cmd": Dieser Befehl nimmt als Argument einen Shell Befehl an der von RSnapshot ausgeführt werden soll. Intern wird dies zu einem backup_script befehl bei dem die Ausgabe verworfen wird.  
Des weiterem können in der Konfiguration verschiedene Variablen verwendet werden. Die Variablen fangen mit einem "$"-Zeichen an. Wenn ein normalen "$"-Zeichen geschrieben werden soll muss dies escaped werden mithilfe eines weitren "$"-Zeichens (also "$$").  
Es existieren folgende Variablen:

- $volumeRootDir
- $containerConfigDir
- $containerName

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

```bash
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
