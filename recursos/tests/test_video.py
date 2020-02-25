# coding: utf8
print("""
Objetivos:
Chequear funcionamiento de CV2 OPENCV para procesamiento de Video
Descartar errores Pygame (no utiliza)

CONTROLES: 

t: (takeoff)
l: aterrizar (land)
w-a-s-d: up-down-yaw

---

IMPORTANTE:
Q: para finalizar.

---

De no funcionar:
	a) chequear configuración de recepción de estados según SDK.
	b) chequear firewall y antivirus activos.
	""")

import cv2, math, time

import os, sys, inspect
directorio_actual = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
directorio_padre = os.path.dirname(directorio_actual)
sys.path.insert(0,directorio_padre)
from moduloTello import Tello

miDron = Tello()
if not miDron.conectar():
	print("No se pudo conectar con Tello - ¡Abortando!")
	exit(1)

miDron.setear_stream_off()
time.sleep(1)

miDron.setear_stream_on()

cv2.namedWindow("drone")
frame_read = miDron.obtener_frame_read()
while True:
	img = frame_read.frame
	cv2.imshow("drone", img)

	key = cv2.waitKey(1) & 0xff
	if key == ord('q'):
		miDron.aterrizar()
		frame_read.stop()
		miDron.setear_stream_off()
		break
	if key == ord('t'):
		miDron.despegar()
	if key == ord('l'):
		miDron.aterrizar()
	elif key == ord('w'):
		miDron.mover_arriba(30)
	elif key == ord('s'):
		miDron.mover_abajo(30)
	elif key == ord('a'):
		miDron.rotar_anti_sentido_horario(20)
	elif key == ord('d'):
		miDron.rotar_sentido_horario(20)

miDron.end()