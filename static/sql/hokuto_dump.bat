 @echo off
   for /f "tokens=1-3 delims=. " %%i in ("%date%") do (
     set day=%%i
     set month=%%j
     set year=%%k
   )
   set datestr=%day%_%month%_%year%
   echo datestr is %datestr%
   goto end
   set BACKUP_DIR=E:\pgsql\pg_backup\
   set BACKUP_FILE=%BACKUP_DIR%hokuto_%datestr%.backup
   echo backup file name is %BACKUP_FILE%
   SET PGPASSWORD=boruh
   echo on
   pg_dump -h localhost -p 5432 -U postgres -F c -b -v -f %BACKUP_FILE% hokuto
   :end