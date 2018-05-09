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
  "dbname": "",
  "user" : "foo",
  "password": "foobar",
  "backup_dir": "/home/user/backup",
  "name": "etc",
  "compression": "gz"
}
```
