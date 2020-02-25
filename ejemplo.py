 # coding: utf8
import recursos.moduloTello as moduloTello
import recursos.moduloInterfaz as moduloInterfaz
import pygame
import tkinter
import threading
import datetime

miDron = moduloTello.Tello()
interfaz = moduloInterfaz.Interfaz()
interfaz.setear_dron_controlado(miDron)


pygame.init()
pygame.display.set_caption("Ejemplo Tello Video")
pygameWindow = pygame.display.set_mode([960, 720])

interfaz.setear_ventana_pygame(pygameWindow)

interfaz.activar_video()

velocidadBase = 70

def keyDown(tecla):
	if tecla == pygame.K_w:
		interfaz.velocidad_abajo_arriba = velocidadBase
	elif tecla == pygame.K_s:
		interfaz.velocidad_abajo_arriba = -velocidadBase
	elif tecla == pygame.K_UP:
		interfaz.velocidad_adelante_atras = velocidadBase
	elif tecla == pygame.K_DOWN:
		interfaz.velocidad_adelante_atras = -velocidadBase
	elif tecla == pygame.K_LEFT:
		interfaz.velocidad_izq_der = -velocidadBase
	elif tecla == pygame.K_RIGHT:
		interfaz.velocidad_izq_der = velocidadBase
	elif tecla == pygame.K_a:
		interfaz.velocidad_rotacion = -velocidadBase
	elif tecla == pygame.K_d:
		interfaz.velocidad_rotacion = velocidadBase

interfaz.setear_controles_key_down(keyDown)

def keyUp(tecla):
	if tecla == pygame.K_w or tecla == pygame.K_s:
		interfaz.velocidad_abajo_arriba = 0
	elif tecla == pygame.K_t:
		miDron.despegar()
		interfaz.habilitar_controles_remotos()
	elif tecla == pygame.K_l:
		miDron.aterrizar()
		interfaz.deshabilitar_controles_remotos()
	elif tecla == pygame.K_v:
		if interfaz.videoActivo:
			interfaz.desactivar_video()
		else:
			interfaz.activar_video()
	elif tecla == pygame.K_j:
		interfaz.setear_logger_debug()
	elif tecla == pygame.K_k:
		interfaz.setear_logger_info()
	elif tecla == pygame.K_UP or tecla == pygame.K_DOWN:
		interfaz.velocidad_adelante_atras = 0
	elif tecla == pygame.K_LEFT or tecla == pygame.K_RIGHT:
		interfaz.velocidad_izq_der = 0
	elif tecla == pygame.K_a or tecla == pygame.K_d:
		interfaz.velocidad_rotacion = 0
	elif tecla == pygame.K_b:
		print("Batería: " + str(miDron.bat))
		# print("Batería: " + str(miDron.obtener_bateria())) 

interfaz.setear_controles_key_up(keyUp)

interfaz.correr()