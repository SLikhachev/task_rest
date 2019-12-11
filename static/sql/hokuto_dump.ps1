$date = Get-Date -F "%d-MM-%y"
$BACKUP_DIR = "E:\pgsql\dump\"
$BACKUP_FILE = $BACKUP_DIR + "hokuto_" + $date + ".backup"
#echo $BACKUP_FILE
 $env:PGPASSWORD="boruh"
 "pg_dump -h localhost -p 5432 -U postgres -F c -b -v -f " + $BACKUP_FILE  + " hokuto" | iex
 