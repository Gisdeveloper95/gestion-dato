param(
    [Parameter(Mandatory=$false)]
    [string]$PostgresHost = "172.19.3.196",
    [Parameter(Mandatory=$false)]
    [int]$PostgresPort = 5432,
    [Parameter(Mandatory=$false)]
    [string]$PostgresUser = "postgres",
    [Parameter(Mandatory=$true)]
    [string]$PostgresPassword="1234",
    [Parameter(Mandatory=$false)]
    [string]$PostgresDatabase = "gestion_dato_db"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "RESOLVER SIDs DE WINDOWS A NOMBRES DE USUARIO" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar dominio
try {
    $domain = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()
    Write-Host "OK Conectado al dominio: $($domain.Name)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Este script debe ejecutarse desde un equipo unido al dominio" -ForegroundColor Red
    exit 1
}

# Funcion para resolver SID
function Resolve-SIDToUsername {
    param([string]$SID)
    try {
        $objSID = New-Object System.Security.Principal.SecurityIdentifier($SID)
        $objUser = $objSID.Translate([System.Security.Principal.NTAccount])
        $fullName = $objUser.Value

        if ($fullName -match '\\') {
            $username = $fullName.Split('\')[1]
        } else {
            $username = $fullName
        }

        # Intentar obtener display name
        try {
            $searcher = New-Object System.DirectoryServices.DirectorySearcher
            $searcher.Filter = "(objectSid=$SID)"
            $searcher.PropertiesToLoad.Add("displayName") | Out-Null
            $searcher.PropertiesToLoad.Add("sAMAccountName") | Out-Null
            $result = $searcher.FindOne()

            if ($result) {
                $displayName = $result.Properties["displayName"][0]
                $samAccountName = $result.Properties["sAMAccountName"][0]
                return @{
                    Username = $samAccountName
                    DisplayName = $displayName
                }
            }
        } catch {}

        return @{
            Username = $username
            DisplayName = $null
        }
    } catch {
        return $null
    }
}

Write-Host ""
Write-Host "Conectando a PostgreSQL..." -ForegroundColor Cyan
Write-Host "  Host: $PostgresHost"
Write-Host "  Puerto: $PostgresPort"
Write-Host "  Base de datos: $PostgresDatabase"

# Obtener SIDs sin resolver usando psql
$env:PGPASSWORD = $PostgresPassword
$query = "SELECT sid, usuario_windows FROM mapeo_sids WHERE resuelto = FALSE"

try {
    $output = psql -h $PostgresHost -p $PostgresPort -U $PostgresUser -d $PostgresDatabase -t -A -F '|' -c $query 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR conectando a PostgreSQL" -ForegroundColor Red
        Write-Host $output
        exit 1
    }

    $sids = @()
    foreach ($line in $output) {
        if ($line -match '\|') {
            $parts = $line.Split('|')
            $sids += @{
                sid = $parts[0]
                usuario_windows = $parts[1]
            }
        }
    }
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}

if ($sids.Count -eq 0) {
    Write-Host "OK No hay SIDs pendientes de resolver" -ForegroundColor Green
    exit 0
}

Write-Host "  Encontrados: $($sids.Count) SIDs sin resolver" -ForegroundColor Yellow
Write-Host ""

# Procesar cada SID
$resueltos = 0
$fallidos = 0

foreach ($sid in $sids) {
    Write-Host "Procesando: $($sid.sid)" -ForegroundColor Gray
    Write-Host "  Usuario temporal: $($sid.usuario_windows)" -ForegroundColor DarkGray

    $userInfo = Resolve-SIDToUsername -SID $sid.sid

    if ($userInfo) {
        Write-Host "  OK Resuelto: $($userInfo.Username)" -ForegroundColor Green
        if ($userInfo.DisplayName) {
            Write-Host "    Nombre completo: $($userInfo.DisplayName)" -ForegroundColor DarkGray
        }

        # Usar COPY con CSV para evitar problemas de encoding
        $username = $userInfo.Username
        $displayName = if ($userInfo.DisplayName) { $userInfo.DisplayName } else { "" }
        $sidValue = $sid.sid

        # Crear archivo temporal CSV con encoding UTF-8 sin BOM
        $tempCsv = [System.IO.Path]::GetTempFileName() + ".csv"
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false

        # Formato CSV: sid|username|displayname
        $csvLine = "$sidValue`t$username`t$displayName"
        [System.IO.File]::WriteAllText($tempCsv, $csvLine, $utf8NoBom)

        # Crear script SQL que usa el CSV
        $tempSql = [System.IO.Path]::GetTempFileName() + ".sql"
        $sqlScript = @"
-- Crear tabla temporal
CREATE TEMP TABLE temp_sid_update (
    sid VARCHAR(200),
    username VARCHAR(100),
    displayname VARCHAR(200)
);

-- Cargar datos desde CSV con encoding UTF-8
\copy temp_sid_update FROM '$($tempCsv.Replace('\', '\\'))' WITH (FORMAT csv, DELIMITER E'\t', ENCODING 'UTF8', HEADER false);

-- Actualizar mapeo_sids desde temp
UPDATE mapeo_sids
SET usuario_windows = temp_sid_update.username,
    nombre_completo = temp_sid_update.displayname,
    resuelto = TRUE,
    notas = 'Resuelto desde Windows/AD'
FROM temp_sid_update
WHERE mapeo_sids.sid = temp_sid_update.sid;

-- Verificar
SELECT 'OK' as resultado WHERE EXISTS (
    SELECT 1 FROM mapeo_sids WHERE sid = '$sidValue' AND resuelto = TRUE
);
"@

        [System.IO.File]::WriteAllText($tempSql, $sqlScript, $utf8NoBom)

        # Ejecutar
        $env:PGPASSWORD = $PostgresPassword
        $output = psql -h $PostgresHost -p $PostgresPort -U $PostgresUser -d $PostgresDatabase -f $tempSql 2>&1 | Out-String

        # Limpiar archivos temporales
        Remove-Item $tempSql -Force -ErrorAction SilentlyContinue
        Remove-Item $tempCsv -Force -ErrorAction SilentlyContinue

        if ($output -match 'OK') {
            $resueltos++
        } else {
            Write-Host "  ERROR actualizando BD" -ForegroundColor Red
            Write-Host "    Output: $($output.Trim())" -ForegroundColor DarkRed
            $fallidos++
        }
    } else {
        Write-Host "  ERROR No se pudo resolver (SID invalido o usuario eliminado)" -ForegroundColor Red
        $fallidos++
    }

    Write-Host ""
}

# Resumen
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "RESUMEN" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SIDs resueltos: $resueltos" -ForegroundColor Green
$failColor = if ($fallidos -gt 0) { "Red" } else { "Gray" }
Write-Host "  SIDs fallidos: $fallidos" -ForegroundColor $failColor
Write-Host "  Total procesados: $($sids.Count)" -ForegroundColor Cyan
Write-Host ""
