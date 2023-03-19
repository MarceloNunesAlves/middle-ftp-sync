# Import Module
import paramiko
import os
import ffmpeg

# Fill Required Information
host = os.getenv("SSH_HOSTNAME", "192.168.0.1")
username = os.getenv("SSH_USERNAME", "user")
password = os.getenv("SSH_PASSWORD", "pass")
path_dest = os.getenv("SSH_PATH_DEST_VIDEO", "/home/local_user/")

def download_file(path_file, location):

    # Cria a conexão com o servidor SSH
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host, username=username, password=password)

    # Caminho do arquivo no servidor remoto
    remote_path = path_file

    # Nome do arquivo
    filename = path_file.split("/")[-1]

    # Caminho onde será salvo o arquivo
    path_dest_full = path_dest + "/" + location
    if not os.path.exists(path_dest_full):
        os.makedirs(path_dest_full)

    path_dest_temp_full = path_dest + "/temp/" + location
    if not os.path.exists(path_dest_temp_full):
        os.makedirs(path_dest_temp_full)

    local_path = path_dest + "/" + location + "/" + filename
    local_tmp = path_dest + "/temp/" + location + "/" + filename

    # Copia o arquivo do servidor para o diretório atual
    ftp_client = ssh_client.open_sftp()
    ftp_client.get(remote_path, local_tmp)

    # Fecha a conexão com o servidor SSH e o cliente SFTP
    ftp_client.close()
    ssh_client.close()

    convert_video(local_tmp, local_path)

    return local_path

def convert_video(local_tmp, local_path):
    input_file = local_tmp
    output_file = local_path

    # Configura o processo de conversão
    (
        ffmpeg
        .input(input_file)
        .output(output_file, vcodec="h264", acodec="aac", strict="experimental")
        .overwrite_output()
        .run()
    )