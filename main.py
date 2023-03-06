import exception
from process_log import config_log
from flask import Flask, request
import requests
import ftp_download
import threading
import queue
import os

logger = config_log(__name__)

app = Flask(__name__)
q = queue.Queue()

url_analisys = os.getenv("URL_SERVER_DETECTOR_VIDEO", "http://localhost:5001/")

def send_to_analysis(path, location, start_hour_email, end_hour_email):
    try:
        # Serviço de detecção de pessoa no video
        url = url_analisys

        payload = {
            "path_video": path,
            "location": location,
            "hour_start_email": start_hour_email,
            "hour_end_email": end_hour_email
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            print("Requisição realizada com sucesso.")
        else:
            print("Ocorreu um erro ao realizar a requisição.")
    except:
        print("Erro no envio ao serviço de analise de imagem")

@app.route("/", methods=['POST'])
def push_message():
    requisicao = request.get_json(force=True)
    try:
        path        = str(requisicao['path_video'])
        location    = str(requisicao['location'])
        try:
            hour_start = int(requisicao['hour_start_email'])
        except:
            hour_start = None
        try:
            hour_end = int(requisicao['hour_end_email'])
        except:
            hour_end = None

        q.put({"path": path,
               "hour_start_email": hour_start,
               "hour_end_email": hour_end,
               "location": location})
    except:
        raise exception.InvalidUsage('Não foi possivel enviar para a fila!', status_code=400)

    return "OK"

def delete_file(file_save):
    os.remove(file_save)

def worker():
    while True:
        item = q.get()

        logger.debug(f"Inicio da sincronização do arquivo: {item['path']}")

        # Copia o video para o repositorio local
        local_path = ftp_download.download_file(item['path'], item['location'])

        # Envia para o processo de detecção de pessoas no video
        send_to_analysis(local_path, item['location'], item['hour_start_email'], item['hour_end_email'])

        logger.debug(f"Final da sincronização do arquivo: {item['path']}")
        q.task_done()

# Turn-on the worker thread.
threading.Thread(target=worker, daemon=True).start()

# Block until all tasks are done.
if __name__ == '__main__':
    logger.debug('Inicio do endpoint')
    app.run(host="0.0.0.0", port=5002, load_dotenv=False)
