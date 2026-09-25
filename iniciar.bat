@echo off
rem Abre Mil Palabras en el navegador sirviendo esta carpeta en http://localhost:8080
rem (el modo sin conexion y la instalacion como app requieren http, no funcionan abriendo index.html directamente)
cd /d "%~dp0"
start "" "http://localhost:8080/index.html"
python -m http.server 8080 --bind 127.0.0.1
