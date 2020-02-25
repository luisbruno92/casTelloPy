# coding: utf8
print("""
Chequear funcionamiento de CV2 OPENCV para procesamiento obtención de IMÁGENES
Descartar errores Pygame (no utiliza)
Descartar problemas con VIDEO
De no funcionar:
	a) chequear configuración de recepción de estados según SDK.
	b) chequear firewall y antivirus activos.
Creará imágenes en la carpeta local. Tener a bien eliminarlas al finalizar.
""")

import os, sys, inspect

directorio_actual = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
directorio_padre = os.path.dirname(directorio_actual)
sys.path.insert(0,directorio_padre)

from moduloTello import Tello
import cv2
import time

miRuta = os.path.dirname(os.path.abspath(__file__))

miDron = Tello()
miDron.conectar()
miDron.setear_stream_on()
contador = 0
print(miDron.obtener_udp_video_address())
capturaDeVideo = cv2.VideoCapture(miDron.obtener_udp_video_address())
success,image = capturaDeVideo.read()
success = True

while success and contador<50:
    print (contador)
    capturaDeVideo.set(cv2.CAP_PROP_POS_MSEC,(contador*1000))
    success,image = capturaDeVideo.read()
    print ('Read a new frame: ', success)
    cv2.imwrite(miRuta+ "/imagenesTest/frame%d.jpg" % contador, image) # save frame as JPEG file
    contador = contador + 5

miDron.end()
