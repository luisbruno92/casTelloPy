# Chequear y conocer valores del Gamepad conectado mediante PYGAME
# De no funcionar:
#	a) Chequear configuración y/o calibración desde Panel de Control del SO
#	b) Testear online buscando "Online Gamepad Test"

import os, sys, inspect

directorio_actual = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
directorio_padre = os.path.dirname(directorio_actual)
sys.path.insert(0,directorio_padre)

import pygame
import moduloInterfaz as moduloInterfaz

interfaz = moduloInterfaz.Interfaz()
pygame.init()
pygame.display.set_caption("Test Botones")
ventana = pygame.display.set_mode([350, 100])
interfaz.setear_ventana_pygame(ventana)
if pygame.joystick.get_count() > 0:
	gamepad = pygame.joystick.Joystick(0)
	gamepad.init()

def controlCallback():
	print(str(gamepad.get_axis(0)) + " " + str(gamepad.get_axis(1)) + " " + str(gamepad.get_axis(2)) + " " + str(gamepad.get_axis(3)))

interfaz.setear_controles_ejes_gamepad(controlCallback)
interfaz.correr()

