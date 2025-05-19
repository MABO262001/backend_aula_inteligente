Write-Host "🚀 Iniciando backend con Docker Compose..."
docker-compose up -d --build

# Intentar obtener el contenedor backend hasta 60 segundos
$backendName = $null
$maxWait = 60
$waited = 0

while (-not $backendName -and $waited -lt $maxWait) {
    Start-Sleep -Seconds 5
    $waited += 5
    $backendName = docker ps --format "{{.Names}}" | Where-Object { $_ -like "*-backend-1" } | Select-Object -First 1
    Write-Host "⏳ Buscando contenedor backend... Esperado $waited segundos"
}

if ($backendName) {
    Write-Host "`n⏳ Contenedor encontrado: $backendName. Esperando 5 segundos para estabilizar..."
    Start-Sleep -Seconds 5

    Write-Host "`n🗂️ Ejecutando init-db en $backendName"
    docker exec -it $backendName flask init-db
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al ejecutar init-db"
        exit 1
    }

    Write-Host "`n🌱 Ejecutando seed-db en $backendName"
    docker exec -it $backendName flask seed-db
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al ejecutar seed-db"
        exit 1
    }

    Write-Host "`n✅ Backend iniciado correctamente. Puedes abrir http://localhost:5000"
}
else {
    Write-Host "❌ No se pudo encontrar el contenedor del backend después de esperar $maxWait segundos. Verifica con 'docker ps'."
    exit 1
}
