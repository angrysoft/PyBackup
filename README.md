# Backaup
 Simple backup solution for backuping directory and databases.

## Configs
 Configs files are json files for example:
```json
{
  "type": "dir",
  "path": "/etc",
  "backup_dir": "/home/user/backup",
  "name": "etc",
  "compression": "gz"
}
```
## type
#### dir - Create a new tar archive with directory as source
* path - source directory path
* name - archive name
* backup_dir - output path for archive
* compression - compression type
    * gz   - gzip compression
    * bz2  - bzip compression
    * xz   - lzma compression
    * none - without compression
```json
{
  "type": "dir",
  "path": "/etc",
  "backup_dir": "/home/user/backup",
  "name": "etc",
  "compression": "gz"
}
```

#### files - Create a new tar archive with file list as source
* path - file list 
* backup_dir - output path for archive
* compression - compression type
    * gz   - gzip compression
    * bz2  - bzip compression
    * xz   - lzma compression
    * none - without compression
```json
{
  "type": "dir",
  "path": ["/etc/locale.conf", "/etc/vconsole.conf"],
  "backup_dir": "/home/user/backup",
  "name": "etc",
  "compression": "gz"
}
```

#### mariadb - create database dump
* dbname - database name when name is "*" dumps all databases 
* mode  - type of backup
    * dump  - [mysqdump](https://mariadb.com/kb/en/library/mysqldump/)
    * json - human frendly json files ( not implemented )
* user - db user name
* password - db password
* backup_dir - output path for 
* compression - compression type
    * gz   - gzip compression
    * bz2  - bzip compression
    * xz   - lzma compression
    * none - without compression
```json
{
  "type": "mariadb",
  "dbname": "foodb",
  "mode": "dummp",
  "user" : "foo",
  "password": "foobar",
  "backup_dir": "/home/user/backup",
  "name": "foodb",
  "compression": "gz"
}
```

### Example of use
Run all backup congfigs end with .json in directory /etc/PyBackup
```bash
pybackup -d /etc/PyBackup
```

Run list configs.
```bash
pybackup -d /etc/PyBackup -c db.json etc.json
``` 