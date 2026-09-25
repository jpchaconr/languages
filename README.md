# Mil Palabras

Aprende las **1000 palabras más frecuentes** de **inglés, alemán y ruso** con tarjetas y repetición espaciada. Funciona en el navegador, sin cuenta, sin anuncios y sin instalar nada.

Con esas 1000 palabras entiendes buena parte de lo que se dice y se lee a diario en un idioma, así que empiezas por lo que más te va a servir.

## Qué incluye

- **3 idiomas:** inglés, alemán y ruso, 1000 palabras cada uno, ordenadas de la más común a la menos común.
- **Cada palabra trae:** pronunciación (IPA), categoría gramatical, traducciones al español y dos frases de ejemplo traducidas.
- **Género de los sustantivos** en alemán y ruso (m, f, n, pl), y el **acento marcado** en ruso.
- **Pronunciación en voz alta:** toca el altavoz y tu dispositivo la lee con la mejor voz disponible en ese idioma.
- **Modo claro y oscuro,** según la configuración de tu dispositivo.

## Cómo se estudia

Desde la pantalla de inicio de cada idioma tienes dos modos:

- **Palabras nuevas:** tarjetas que aún no has visto. Salen en orden aleatorio, pero las más frecuentes tienen más probabilidad de aparecer antes.
- **Repasar:** las palabras que ya te toca volver a ver.

En cada tarjeta, toca para voltearla y decide si **la sabías** (desliza a la derecha) o **no la sabías** (desliza a la izquierda). También puedes usar los botones.

Al terminar una sesión ves un resumen y puedes repasar de inmediato las que fallaste.

### Repetición espaciada

Cada palabra pasa por seis «cajas». Si la aciertas, sube y tardará más en volver a aparecer (1, 3, 7, 16 y 35 días). Si la fallas, vuelve a empezar. Así dedicas tu tiempo a lo que realmente te cuesta.

El **mapa de frecuencia** de la pantalla de inicio te muestra de un vistazo cuáles has visto, cuáles estás aprendiendo y cuáles ya dominas.

### Ajustes

- **Mostrar primero:** empezar por la palabra o por la traducción.
- **Tarjetas por sesión:** sesiones más cortas o más largas.
- **Reiniciar progreso** de un idioma.

## Tu progreso

Tu avance se guarda **en tu propio dispositivo**, no en un servidor. Eso implica que:

- Cada dispositivo o navegador tiene su propio progreso.
- Si borras los datos del navegador, lo pierdes. Usa **Exportar copia** de vez en cuando; con **Importar copia** lo recuperas o lo pasas a otro dispositivo.
- En modo privado puede que el navegador no permita guardarlo (la app te avisa).

Si quien te dio la app activó la sincronización, verás un bloque **«Copia en tu Google Drive»** para conectar tu propio Drive y llevar el progreso entre dispositivos. Solo se guarda un archivo en una carpeta oculta de tu Drive: la app no ve tus demás archivos y nadie más recibe tus datos. Puedes desconectarte cuando quieras.

## Instalarla como app

Puedes usarla como una app más, incluso **sin conexión**:

- **Android / PC (Chrome, Edge):** pulsa **Instalar como app** en la pantalla de inicio.
- **iPhone / iPad:** en Safari, Compartir → **Añadir a pantalla de inicio**.

## Mejorar las voces en iPhone / iPad

La app usa las voces que tiene instalado tu dispositivo, y las que vienen por defecto suenan bastante robóticas. Puedes descargar otras de mejor calidad gratis:

1. Abre **Ajustes → Accesibilidad → Contenido leído → Voces**.
2. Elige el idioma (**Inglés**, **Alemán** o **Ruso**) y el acento que prefieras.
3. Toca una voz y pulsa el icono de descarga. Busca las que digan **Mejorada** o **Premium**; son las más naturales.
4. Vuelve a la app. Si no notas el cambio, ciérrala del todo y ábrela de nuevo.

La app elige sola la mejor voz instalada para cada idioma, así que no hay nada que configurar dentro de ella. Los nombres de los menús pueden variar un poco según la versión de iOS.

## Usarla en tu computadora

1. Instala [Python](https://www.python.org/downloads/) si no lo tienes.
2. En Windows, haz doble clic en `iniciar.bat`. Se abrirá el navegador en `http://localhost:8080`.

   En otros sistemas, ejecuta `python -m http.server 8080` dentro de la carpeta y abre `http://localhost:8080`.

> Abrir `index.html` con doble clic funciona a medias: el modo sin conexión y la instalación necesitan que se sirva por `http`.

## Para quien quiera saber más

- Las palabras salen de [wordfreq](https://github.com/rspeer/wordfreq) y otras fuentes de frecuencia; el detalle está en [`data/README.md`](data/README.md).
- Cómo activar la sincronización con Google Drive: [`SINCRONIZACION.md`](SINCRONIZACION.md).
