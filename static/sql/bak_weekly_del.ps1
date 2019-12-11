$date = (Get-Date).AddDays(-7)
$path = `
"C:\Program Files\Microsoft SQL Server\MSSQL11.MSSQLSRV1\MSSQL\Backup\Poliklinika",`
"C:\Program Files\Microsoft SQL Server\MSSQL11.MSSQLSRV1\MSSQL\Backup\Laboratoria", `
"C:\Program Files\Microsoft SQL Server\MSSQL11.MSSQLSRV1\MSSQL\Backup\Buh", `
"C:\Program Files\Microsoft SQL Server\MSSQL11.MSSQLSRV1\MSSQL\Backup\HRM"

foreach ($p in $path) {
    #echo $p
    ls $p | ? {$_.Creationtime -lt $date; } | del -Force

}

#ls "C:\Program Files\Microsoft SQL Server\MSSQL11.MSSQLSRV1\MSSQL\Backup\Poliklinika" | `
#? {$_.Creationtime -lt $date;  } | del
