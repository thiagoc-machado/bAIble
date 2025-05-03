# biblia_contexto/memory_cleaner.py
import time
from threading import Thread
from biblia_contexto import buscar_contexto

def start_memory_cleaner():
    def cleaner():
        while True:
            time.sleep(10)  # checagem a cada 10s (ou mais, se quiser)
            now = time.time()
            if buscar_contexto._cache['model'] and now - buscar_contexto._cache['last_used'] > buscar_contexto.TIMEOUT:
                print('🧹 Limpando modelo da memória...')
                buscar_contexto._cache['model'] = None
            if buscar_contexto._cache['index'] and now - buscar_contexto._cache['last_used'] > buscar_contexto.TIMEOUT:
                print('🧹 Limpando índice da memória...')
                buscar_contexto._cache['index'] = None
                buscar_contexto._cache['metadados'] = None

    Thread(target=cleaner, daemon=True).start()
    
