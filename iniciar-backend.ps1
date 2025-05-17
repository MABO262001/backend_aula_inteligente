Write-Host "🚀 Iniciando backend con Docker Compose..."
docker-compose up -d --build

Start-Sleep -Seconds 5

$backendName = docker ps --format "{{.Names}}" | Where-Object { $_ -like "*-backend-1" }

if ($backendName) {
    Write-Host "🗂️ Ejecutando init-db en $backendName"
    docker exec -it $backendName flask init-db

    Write-Host "🌱 Ejecutando seed-db en $backendName"
    docker exec -it $backendName flask seed-db

    Write-Host "✅ Backend iniciado correctamente. Puedes abrir http://localhost:5000"
}
else {
    Write-Host "❌ No se pudo encontrar el contenedor del backend. Verifica docker ps."
}
