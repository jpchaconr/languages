# Sincronizar el progreso con Google Drive

La app guarda el progreso en el dispositivo (`localStorage`). Si configuras un **ID de cliente de Google**, aparece el bloque
«Copia en tu Google Drive» en *Tu progreso* y cada usuario puede conectar **su propio Drive**. Sin ID de cliente ese bloque no aparece.

## Qué hace (y qué no)
- Guarda un archivo `progreso.json` en la **carpeta oculta de la app** de su Drive (permiso `drive.appdata`). La app **no puede ver** ningún otro archivo.
- Tú, como desarrollador, **no recibes ningún dato**: todo va del navegador del usuario a su Drive.
- Combina palabra a palabra: gana el registro más reciente de cada palabra. «Reiniciar progreso» también se propaga.
- Funciona sin conexión: los cambios se suben cuando vuelve internet.
- El usuario puede desconectar desde la app (revoca el permiso) y borrar el archivo en Drive → Ajustes → *Administrar aplicaciones*.
- Requiere que los dispositivos tengan la hora razonablemente bien puesta (las marcas de tiempo deciden qué respuesta es más reciente).

## Configuración (una vez, ~10 minutos)
Necesitas una cuenta de Google. Nombres de menú según la documentación actual de Google (pueden cambiar de sitio).

1. **Proyecto:** entra en la [Google Cloud Console](https://console.cloud.google.com/) → selector de proyectos → *Proyecto nuevo* (p. ej. «Mil Palabras»).
2. **Activar Drive:** *APIs y servicios → Biblioteca* → busca **Google Drive API** → *Habilitar*.
3. **Pantalla de consentimiento:** menú → **Google Auth platform → Branding** (*Comenzar*):
   - *Branding:* nombre de la app y correo de asistencia.
   - *Audience:* tipo de usuario **Externo**.
   - Correo de contacto, aceptar la política de datos de usuario de las API de Google → *Crear*.
4. **Permiso:** **Google Auth platform → Data Access → Add or remove scopes** y añade solo
   `https://www.googleapis.com/auth/drive.appdata` (si no aparece en la lista, pégalo en «Manually add scopes») → *Update / Save*.
5. **Quién puede usarla:** en **Audience**:
   - En estado *Testing*, solo entran los correos que añadas como **usuarios de prueba** (*Add users*, máx. 100).
   - Para abrirla a cualquiera pulsa **Publish app** (*En producción*). Google clasifica `drive.appdata` como permiso no sensible, por lo que **no requiere verificación** de la app.
6. **ID de cliente:** **Google Auth platform → Clients → Create client** → tipo **Web application**. En **Authorized JavaScript origins** añade (sin barra final, sin ruta, sin comodines):
   - tu URL HTTPS de producción, p. ej. `https://usuario.github.io` o `https://mi-app.netlify.app`
   - para probar en local: **`http://localhost`** y **`http://localhost:8080`** (Google pide ambos; si usas otro puerto, ese también). La vista previa de Claude usa un puerto que cambia en cada arranque: para probar Google con ella arranca `python serve.py` con `PORT=8080`.
   - No hace falta «Authorized redirect URIs».

   Copia el **Client ID** (`xxxxxxxx.apps.googleusercontent.com`). Los cambios de orígenes pueden tardar desde unos minutos hasta unas horas en aplicarse.
7. **Pegar el ID** en [`config.js`](config.js):
   ```js
   window.MILPALABRAS_CONFIG = { googleClientId: "xxxxxxxx.apps.googleusercontent.com" };
   ```
8. **Publicar** de nuevo incluyendo `config.js` (ver abajo).
9. **Probar:** abre la URL → avatar de la esquina superior derecha → *Conectar con Google* → *Permitir* → debe pasar a «Sincronizado». La carpeta oculta se ve en Drive → Ajustes → *Administrar aplicaciones* → «Mil Palabras». Comprueba en un segundo dispositivo que el progreso llega.

## Publicar (archivos necesarios)
```
mkdir -p dist/data dist/icons && cp index.html config.js manifest.webmanifest sw.js dist/ && cp data/palabras.js dist/data/ && cp icons/*.png dist/icons/
```

## Problemas frecuentes
| Síntoma | Causa |
|---|---|
| `Error 400: origin_mismatch` | La URL desde la que abres la app no está en «Orígenes autorizados de JavaScript» (revisa https/http, dominio y puerto). |
| «Acceso bloqueado: la app no ha completado la verificación» | La app está «En pruebas» y el usuario no figura como usuario de prueba. |
| La app dice «Google rechazó el acceso» | Drive API sin activar en el proyecto o ID de cliente incorrecto. |
| «Hay que volver a autorizar el acceso» | El permiso dura 1 hora y la renovación silenciosa la puede bloquear el navegador. Toca **Sincronizar**. |
| En iPhone la ventana de Google no abre | Safari/PWA instalada bloquea a veces las ventanas emergentes. Prueba desde Safari sin instalar, o usa *Exportar copia*. |

## Privacidad (texto orientativo para tus usuarios)
> Si conectas Google Drive, Mil Palabras guarda un único archivo con tu progreso de estudio en una carpeta oculta de tu propio Drive. La app no puede leer tus otros archivos y el desarrollador no recibe ningún dato. Puedes desconectar en cualquier momento desde la app o revocar el acceso en tu cuenta de Google.
