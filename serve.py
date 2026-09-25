"""Servidor estático para probar Mil Palabras. Usa el puerto de la variable PORT (o 8080 si no existe)."""
import functools, http.server, os

port = int(os.environ.get("PORT", "8080"))
root = os.path.dirname(os.path.abspath(__file__))
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
print(f"Sirviendo {root} en http://localhost:{port}", flush=True)
http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
