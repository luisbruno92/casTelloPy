# coding: utf8
try:
	import moduloTello
except:
	pass
import cv2
import pygame
import numpy as np
import time
import logging

# Frames per second of the pygame window display
FPS = 25

class Interfaz(object):
	HANDLER = logging.StreamHandler()
	#FORMATTER = logging.Formatter('[%(asctime)s.%(msecs)03d %(levelname)8s] [%(filename)-17s %(lineno)003d] %(message)s', "%H:%M:%S")
	FORMATTER = logging.Formatter('[%(asctime)s.%(msecs)03d | %(filename)-17s %(lineno)003d] - %(message)s', "%H:%M:%S")
	HANDLER.setFormatter(FORMATTER)
	LOGGER_LEVEL = logging.INFO

	LOGGER = logging.getLogger('modulointerfaz')

	LOGGER.addHandler(HANDLER)
	LOGGER.setLevel(LOGGER_LEVEL)


	def __init__(self):
		self.LOGGER.info("Creando Interfaz")

		self.dron_controlado = False

		self.ventana_tkinter = False

		# Drone velocities between -100~100
		self.velocidad_adelante_atras = 0
		self.velocidad_izq_der = 0
		self.velocidad_abajo_arriba = 0
		self.velocidad_rotacion = 0
		self.speed = 10

		self.envio_controles_remotos_habilitado = False

		self.ventana_pygame = False
		self.should_pygame_stop = True
		self.videoActivo = False

		self.controles_key_down_callback_externa = False
		self.controles_key_up_callback = False
		self.controles_botones_gamepad_callback = False
		self.controles_ejes_gamepad_callback = False

		self.archivo_mision = False
		self.modo_archivo_unico = False

	# LOGGING
	def setear_logger_debug(self):
		self.LOGGER_LEVEL = logging.DEBUG
		self.LOGGER.setLevel(self.LOGGER_LEVEL)
		self.dron_controlado.setear_logger_debug()
		self.LOGGER.info("Seteando nivel de logger a: DEBUG")

	def setear_logger_info(self):
		self.LOGGER_LEVEL = logging.INFO
		self.LOGGER.setLevel(self.LOGGER_LEVEL)
		self.dron_controlado.setear_logger_info()
		self.LOGGER.info("Seteando nivel de logger a: INFO")

	def setear_logger_warning(self):
		self.LOGGER_LEVEL = logging.WARNING
		self.LOGGER.setLevel(self.LOGGER_LEVEL)
		self.dron_controlado.setear_logger_info()
		self.LOGGER.info("Seteando nivel de logger a: INFO")  

	# DRON
	def setear_dron_controlado(self, dron=False):
		if not dron:
			self.dron_controlado = moduloTello.Tello()
		else:
			self.dron_controlado = dron

		self.LOGGER.info("Intentando conectar enlace de control")
		if not self.dron_controlado.conectar():
			self.LOGGER.error("Dron Tello no conectado / No se pudo conectar")
			return

		if not self.dron_controlado.setear_datos_sdk():
			self.LOGGER.warning("Datos SDK no recibidos - no se podrá leer estados en segundo plano (a menos que se fuerce el modo)")

		if not self.dron_controlado.setear_velocidad(self.speed):
			self.LOGGER.error("No se pudo setear la velocidad - al mínimo posible")
			return

		# In case streaming is on. This happens when we quit this program without the escape key.
		if not self.dron_controlado.setear_stream_off():
			self.LOGGER.warning("No fue necesario detener el stream de video")

	# ARCHIVOS MISION Y MODOS
	def setear_archivo_inicio(self, archivo):
		self.modo_archivo_unico = True
		self.setear_archivo(archivo)

	def setear_archivo(self,archivo):
		self.archivo_mision = archivo

	def ejecutar_mision_archivo(self):
		if self.archivo_mision:
			ar = open(self.archivo_mision,"r")
			for l in ar.readlines():
				try:
					self.dron_controlado.enviar_comando_con_respuesta(l.replace("\n",""))
				except:
					self.dron_controlado.enviar_comando_con_respuesta("land")
			# self.finalizar() # innecesario porque saltea bucle de correr() y llega a finalizar()
			# MEJORAR: Se podria iniciar ventana pygame, con imagen de fondo: "Ejecutando mision de archivo", habilitando ESC para finalizar
		else:
			self.LOGGER.error("No hay archivo de misión.")
			return

	# TKINTER

	def setear_ventana_tkinter(self, ventana):
		self.ventana_tkinter = ventana

		def on_closing():
			self.LOGGER.warning("Cerrando ventaka TKINTER")
			# if not self.ventana_pygame:
			#	 self.finalizar()
			self.ventana_tkinter.destroy()

		self.ventana_tkinter.protocol("WM_DELETE_WINDOW", on_closing)


	# PYGAME
	def setear_ventana_pygame(self, ventana=False):
		if (not ventana):
			self.LOGGER.info("NO HAY VENTANA!")
		else:
			self.ventana_pygame = ventana
			pygame.time.set_timer(pygame.USEREVENT + 1, 50)
			should_pygame_stop = False
			self.LOGGER.info("Ventana Pygame agregada. Esperando para 'correr'")

	# VIDEO
	def activar_video(self):
		self.LOGGER.info("Intentando activar video")
		if not self.videoActivo:
			if not self.dron_controlado.setear_stream_on():
				self.LOGGER.error("No se pudo inicializar el stream de video (y/o su visualización en Pygame)")
				return
			else:
				self.videoActivo = True
				self.frame_read = self.dron_controlado.obtener_frame_read()
				self.LOGGER.info("Video activado exitosamente")

	def desactivar_video(self):
		self.LOGGER.info("Intentando desactivar video")
		if self.videoActivo:
			if not self.dron_controlado.setear_stream_off():
				self.LOGGER.error("No se pudo detener el stream de video (y/o su visualización en Pygame)")
				return
			else:
				self.videoActivo = False
				self.frame_read = False
				self.LOGGER.info("Video desactivado exitosamente")


	# CONTROLES
	# Envio de Controles Remotos
	def habilitar_controles_remotos(self):
		self.envio_controles_remotos_habilitado = True

	def deshabilitar_controles_remotos(self):
		self.envio_controles_remotos_habilitado = False
	# Key Down
	def setear_controles_key_down(self, funcion):
		self.controles_key_down_callback_externa = funcion

	def controlar_key_Down_con_callback(self, teclaDown):
		if(self.controles_key_down_callback_externa):
			self.controles_key_down_callback_externa(teclaDown)

	#Key Up
	def setear_controles_key_up(self, funcion):
		self.controles_key_up_callback = funcion

	def controlar_key_up_con_callback(self, teclaUp):
		if(self.controles_key_up_callback):
			self.controles_key_up_callback(teclaUp)

	# Botones Gamepad
	def setear_controles_botones_gamepad(self,funcion):
		self.controles_botones_gamepad_callback = funcion

	def controlar_botones_gamepad_con_callback(self, botonDown):
		# No necesito chequear que haya gamepad porque lo controla el bucle en cada paso.
		if self.controles_botones_gamepad_callback:
			self.controles_botones_gamepad_callback(botonDown)

	# Ejes Gamepad
	def setear_controles_ejes_gamepad(self,funcion):
		self.controles_ejes_gamepad_callback = funcion

	def controlar_ejes_gamepad_con_callback(self):
		# No necesito chequear que haya gamepad porque lo controla el bucle en cada paso.
		if self.controles_ejes_gamepad_callback:
		 	self.controles_ejes_gamepad_callback()

	def setear_velocidades(self, izq_der, ad_atr, ab_arr, yaw):
		self.velocidad_izq_der = int(izq_der)
		self.velocidad_adelante_atras = int(ad_atr)
		self.velocidad_abajo_arriba = int(ab_arr)
		self.velocidad_rotacion = int(yaw)


	# CORRER & UPDATE
	def correr(self):
		counter = 0
		if self.modo_archivo_unico:
			self.LOGGER.info("Corriendo Interfaz en Modo Archivo Único Autónomo")
			self.ejecutar_mision_archivo()
		elif self.ventana_pygame:
			# BUCLE MAINLOOP PYGAME
			self.should_pygame_stop = False
			self.LOGGER.info("Corriendo Interfaz en Modo Pygame")
			while not self.should_pygame_stop:
				if self.ventana_pygame:
					for event in pygame.event.get():
						if event.type == pygame.USEREVENT + 1:
							if pygame.joystick.get_count() > 0:
								 # LEE VALOR EJES, NO EVENTOS PUNTUALES.
								self.controlar_ejes_gamepad_con_callback()
							self.update() # UPDATE CADA 0.050' DEL USEREVENT+1
						elif event.type == pygame.QUIT:
							self.should_pygame_stop = True
						elif event.type == pygame.KEYDOWN:
							if event.key == pygame.K_ESCAPE:
								# "ESC" TERMINACIÓN SEGURA SIEMPRE DISPONIBLE
								self.should_pygame_stop = True
							else:
								self.controlar_key_Down_con_callback(event.key)
						elif event.type == pygame.KEYUP:
							self.controlar_key_up_con_callback(event.key)
						elif event.type == pygame.JOYBUTTONDOWN: #NO NECESITO DETECTAR EL COUNT, seria imposible True
							self.controlar_botones_gamepad_con_callback(event.button)

				if self.videoActivo:
					if self.frame_read.stopped:
						self.frame_read.stop()
						break
					if self.ventana_pygame:
						self.ventana_pygame.fill([0, 0, 0])

					frame = cv2.cvtColor(self.frame_read.frame, cv2.COLOR_BGR2RGB)
					frame = np.rot90(frame)
					frame = np.flipud(frame)
					frame = pygame.surfarray.make_surface(frame)
					
					if self.ventana_pygame:
						self.ventana_pygame.blit(frame, (0, 0))
						pygame.display.update()

				time.sleep(1 / FPS)

		# FIN DEL BUCLE PYGAME INTERFAZ CORRIENDO
		# END DEL DRON
		# Call it always before finishing. To deallocate resources.
		self.finalizar()


	def update(self):
		""" Update routine. Send velocities to Tello."""
		if self.envio_controles_remotos_habilitado:
			self.dron_controlado.enviar_velocidades_control_remoto(self.velocidad_izq_der, self.velocidad_adelante_atras, self.velocidad_abajo_arriba,self.velocidad_rotacion)

	def finalizar (self):
		self.LOGGER.info("Intentando finalizar las interfaces")
		if (self.dron_controlado):
			if(self.dron_controlado.end()):
				if self.ventana_pygame:
					self.LOGGER.warning("La interfaz de control remoto y video (Pygame) se finalizó correctamente")
				else:
					self.LOGGER.warning("La interfaz se finalizó correctamente")
			else:
				self.LOGGER.error("Inconvenientes al finalizar las interfaces")
		else: 
			self.LOGGER.warning("La interfaz se finalizó correctamente")

		self.should_pygame_stop = True # Tener en cuenta que puede ocurrir por otros eventos, no importa repetición.
	
	def guardar_foto(self, ruta, nomb):
		nombre = str(str(nomb).replace(":","-")).replace(".","-")
		archivo= ruta+nombre+".jpg"
		print(archivo)
		image = self.dron_controlado.background_frame_read.frame
		cv2.imwrite(archivo, image)
