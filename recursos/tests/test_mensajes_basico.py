# coding: utf8
print("""
Chequear recepción de mensajes según SDK.
En caso de informar errores:
	a) chequear firewall y antivirus activos.
	b) forzar obtención de estados según documentación módulo Tello [Puede generar otro tipo de errores]
	c) inicializar módulo Tello como TelloSinEstados() - RECOMENDADO.
	""")

print("Este test es muy similar al test_video, solo agrega teclas para imprimir estados")

print("""
CONTROLES:

t: despegar (takeoff)
l: aterrizar (land)
b: imprimir batería
n: imprimir tof
m: imprimir temp
w-a-s-d: up-down-yaw

---

IMPORTANTE:
Presione Q para finalizar.""")

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

miDron.setear_datos_sdk()
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
	elif key == ord('b'):
		x = miDron.bat
		print("Batería es: " + str(x))
	elif key == ord('n'):
		x = miDron.tof
		print("TOF es: " + str(x))
	elif key == ord('m'):
		x = miDron.temph
		print("Temperatura es: " + str(x))

miDron.end()