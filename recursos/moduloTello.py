# coding: utf8
import logging
import socket
import time
import threading
import cv2
from threading import Thread
try:
	from .decorators import accepts
except:
	try:
		from decorators import accepts
	except:
		print("IMPOSIBLE IMPORTAR MODULO DECORATORS")

class Tello:
	"""Python wrapper to interact with the Ryze Tello drone using the official Tello api.
	Tello API documentation:
	https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf
	"""
	# Send and receive commands, client socket
	UDP_IP = '192.168.10.1'
	UDP_PORT = 8889
	RESPONSE_TIMEOUT = 7  # in seconds
	TIME_BTW_COMMANDS = 1  # in seconds
	TIME_BTW_RC_CONTROL_COMMANDS = 0.5  # in seconds
	RETRY_COUNT = 3
	last_received_comando = time.time()

	HANDLER = logging.StreamHandler()
	#FORMATTER = logging.Formatter('[%(asctime)s.%(msecs)03d %(levelname)8s] [%(filename)-17s %(lineno)003d] %(message)s', "%H:%M:%S")
	FORMATTER = logging.Formatter('[%(asctime)s.%(msecs)03d | %(filename)-17s %(lineno)003d] - %(message)s', "%H:%M:%S")
	HANDLER.setFormatter(FORMATTER)
	LOGGER_LEVEL = logging.INFO

	LOGGER = logging.getLogger('djitellopy')

	LOGGER.addHandler(HANDLER)
	LOGGER.setLevel(LOGGER_LEVEL)
	# use logging.getLogger('djitellopy').setLevel(logging.<LEVEL>) in YOUR CODE
	# to only receive logs of the desired level and higher

	# Video stream, server socket
	VS_UDP_IP = '0.0.0.0'
	VS_UDP_PORT = 11111

	STATE_UDP_PORT = 8890

	# VideoCapture object
	cap = None
	background_frame_read = None

	stream_on = False

	esta_volando = False

	#By LUCHO:
	mpads_enabled = False
	sdk = False # Esperada = 20
	obtencion_estados_forzada  = False
	estados = False

	def __init__(self,
				 host='192.168.10.1',
				 port=8889,
				 client_socket=None,
				 enable_exceptions=False,
				 retry_count=3,
				 forzar_obtener_estados = False, # By LUCHO
				 obtencion_estados_habilitada = True): # By LUCHO

		self.address = (host, port)
		self.response = None
		self.response_state = None  # to attain the response of the estados
		self.stream_on = False
		self.enable_exceptions = enable_exceptions
		self.retry_count = retry_count

		# Argumentos agregados al init by LUCHO
		self.obtencion_estados_forzada = forzar_obtener_estados  # By LUCHO
		self.obtencion_estados_habilitada = obtencion_estados_habilitada # By LUCHO

		if client_socket:
			self.clientSocket = client_socket
		else:
			self.clientSocket = socket.socket(socket.AF_INET,  # Internet
											  socket.SOCK_DGRAM)  # UDP
			self.clientSocket.bind(('', self.UDP_PORT))  # For UDP response (receiving data)

		self.stateSocket = socket.socket(socket.AF_INET,
										 socket.SOCK_DGRAM)
		self.stateSocket.bind(('', self.STATE_UDP_PORT))  # for accessing the estados of Tello

		# Run tello udp receiver on background
		thread1 = threading.Thread(target=self.run_udp_receiver, args=())
		thread1.daemon = True
		thread1.start()

		if self.obtencion_estados_habilitada:
			# Run state reciever on background
			thread2 = threading.Thread(target=self.obtener_estados, args=())
			thread2.daemon = True
			thread2.start()

	# LOGGING SETEO By LUCHO
	def setear_logger_debug(self):
		self.LOGGER_LEVEL = logging.DEBUG
		self.LOGGER.setLevel(self.LOGGER_LEVEL)
		self.LOGGER.info("Seteando nivel de logger a: DEBUG")

	def setear_logger_info(self):
		self.LOGGER_LEVEL = logging.INFO
		self.LOGGER.setLevel(self.LOGGER_LEVEL)
		self.LOGGER.info("Seteando nivel de logger a: INFO")

	def setear_logger_warning(self):
		self.LOGGER_LEVEL = logging.WARNING
		self.LOGGER.setLevel(self.LOGGER_LEVEL)
		self.LOGGER.info("Seteando nivel de logger a: INFO")

	def run_udp_receiver(self):
		"""Setup drone UDP receiver. This method listens for responses of Tello. Must be run from a background thread
		in order to not block the main thread."""
		while True:
			try:
				self.response, _ = self.clientSocket.recvfrom(1024)  # buffer size is 1024 bytes
			except Exception as e:
				self.LOGGER.error(e)
				break

	def obtener_estados(self):
		"""This runs on background to recieve the state of Tello"""
		# By LUCHO
		comandos_enteros = ["mid","x","y","z","pitch","roll","yaw","vgx","vgy","vgz","templ","temph","tof","h","bat"]
		comandos_flotantes = ["baro","time","agx","agy","agz"]
		while True:
			try:
				self.response_state, _ = self.stateSocket.recvfrom(256)
				if self.response_state != 'ok' and (int(self.sdk)==20 or self.obtencion_estados_forzada):
					self.response_state = self.response_state.decode('ASCII')
					list = self.response_state.replace(';', ':').replace("\n","").replace("\r", "").split(':')
					# METODO A - TESTEADO CON SDK 20
					# PROS: INTENTA ADAPTAR A CUALQUIER MENSAJE SDK 
					# PROS: USA SETATTR PARA PODER USAR ATRIBUTOS (y no diccionarios)
					# Ver archivo OTROS METODOS.TXT ANTE INCONVENIENTES
					for i in range(0, len(list)-1, 2):
					  # print(list[i] + " --> " + list[i+1])
					  if list[i] in comandos_enteros:
						  setattr(self,list[i],int(list[i+1]))
					  elif list[i] in comandos_flotantes:
						  setattr(self,list[i],float(list[i+1]))
					  else:
						  setattr(self,list[i],list[i+1])
			except Exception as e:
				self.LOGGER.error(e)
				self.LOGGER.error(f"El mensaje problemático recibido era: {self.response_state}")
				break

	def obtener_udp_video_address(self):
		return 'udp://@' + self.VS_UDP_IP + ':' + str(self.VS_UDP_PORT)  # + '?overrun_nonfatal=1&fifo_size=5000'

	def obtener_video_capture(self):
		"""Get the VideoCapture object from the camera drone
		Returns:
			VideoCapture
		"""

		if self.cap is None:
			self.cap = cv2.VideoCapture(self.obtener_udp_video_address())

		if not self.cap.isOpened():
			self.cap.open(self.obtener_udp_video_address())

		return self.cap

	def obtener_frame_read(self):
		"""Get the BackgroundFrameRead object from the camera drone. Then, you just need to call
		backgroundFrameRead.frame to get the actual frame received by the drone.
		Returns:
			BackgroundFrameRead
		"""
		if self.background_frame_read is None:
			self.background_frame_read = BackgroundFrameRead(self, self.obtener_udp_video_address()).start()
		return self.background_frame_read

	def stop_video_capture(self):
		return self.setear_stream_off()

	# --- ENVIO GENERAL DE COMANDOS ---

	# RECUPERAME MIS ACCEPTS LUIS
	def enviar_comando_con_respuesta(self, command, printinfo=True, timeout=RESPONSE_TIMEOUT, triedNums=False, limite = RETRY_COUNT):
		# Para "registro intento n° 1/3" by LUCHO triedNums by LUCHO
		if triedNums:
			intento_actual = " - intento "+str(triedNums)+'/'+ str(limite)
			splitterextra = " - "
		else:
			intento_actual = ""
			splitterextra = ""
		"""Send command to Tello and wait for its response.
		Return:
			bool: True for successful, False for unsuccessful
		"""
		# Commands very consecutive makes the drone not respond to them. So wait at least self.TIME_BTW_COMMANDS seconds
		diff = time.time() * 1000 - self.last_received_comando
		if diff < self.TIME_BTW_COMMANDS:
			time.sleep(diff)

		if printinfo:
			self.LOGGER.info('Enviando comando (esperando respuesta' + intento_actual + '): ' + command)
		timestamp = int(time.time() * 1000)

		self.clientSocket.sendto(command.encode('utf-8'), self.address)

		while self.response is None:
			if (time.time() * 1000) - timestamp > timeout * 1000:
				self.LOGGER.warning('Se excedió el tiempo de espera' + intento_actual + splitterextra + 'para el comando: ' + command)
				return False

		try:
			response = self.response.decode('utf-8').rstrip("\r\n")
		except UnicodeDecodeError as e:
			self.LOGGER.error(e)
			return None

		if printinfo:
			self.LOGGER.info(f'Respuesta recibida al comando {command} fue: {response}')

		self.response = None

		self.last_received_comando = time.time() * 1000

		return response

	@accepts(command=str)
	def enviar_comando_sin_respuesta(self, command):
		"""Send command to Tello without expecting a response. Use this method when you want to send a command
		continuously
			- go x y z speed: Tello fly to x y z in speed (cm/s)
				x: 20-500
				y: 20-500
				z: 20-500
				speed: 10-100
			- curve x1 y1 z1 x2 y2 z2 speed: Tello fly a curve defined by the current and two given coordinates with
				speed (cm/s). If the arc radius is not within the range of 0.5-10 meters, it responses false.
				x/y/z can’t be between -20 – 20 at the same time .
				x1, x2: 20-500
				y1, y2: 20-500
				z1, z2: 20-500
				speed: 10-60
			- rc a b c d: Send RC control via four channels.
				a: left/right (-100~100)
				b: forward/backward (-100~100)
				c: up/down (-100~100)
				d: yaw (-100~100)
		"""
		# Commands very consecutive makes the drone not respond to them. So wait at least self.TIME_BTW_COMMANDS seconds

		self.LOGGER.debug('Enviando comando (sin esperar respuesta): ' + command)
		self.clientSocket.sendto(command.encode('utf-8'), self.address)

	@accepts(command=str, timeout=int)
	def enviar_comando_de_control(self, command, timeout=RESPONSE_TIMEOUT):
		"""Send control command to Tello and wait for its response. Possible control commands:
			- command: entry SDK mode
			- takeoff: Tello auto takeoff
			- land: Tello auto land
			- streamon: Set video stream on
			- streamoff: Set video stream off
			- emergency: Stop all motors immediately
			- up x: Tello fly up with distance x cm. x: 20-500
			- down x: Tello fly down with distance x cm. x: 20-500
			- left x: Tello fly left with distance x cm. x: 20-500
			- right x: Tello fly right with distance x cm. x: 20-500
			- forward x: Tello fly forward with distance x cm. x: 20-500
			- back x: Tello fly back with distance x cm. x: 20-500
			- cw x: Tello rotate x degree clockwise x: 1-3600
			- ccw x: Tello rotate x degree counter- clockwise. x: 1-3600
			- flip x: Tello fly flip x
				l (left)
				r (right)
				f (forward)
				b (back)
			- speed x: set speed to x cm/s. x: 10-100
			- wifi ssid pass: Set Wi-Fi with SSID password
		Return:
			bool: True for successful, False for unsuccessful
		"""
		response = None
		if command == "land":
			limit = self.retry_count*2
		else:
			limit = self.retry_count

		for i in range(0, limit):
			response = self.enviar_comando_con_respuesta(command, timeout=timeout, triedNums=(i+1), limite =limit)

			if response == 'OK' or response == 'ok':
				return True

		return self.retornar_error_al_enviar_comando(command, response, self.enable_exceptions)

	@accepts(command=str, printinfo=bool)
	def enviar_comando_de_lectura(self, command, printinfo=True):
		"""Send set command to Tello and wait for its response. Possible set commands:
			- speed?: get current speed (cm/s): x: 1-100
			- battery?: get current battery percentage: x: 0-100
			- time?: get current fly time (s): time
			- height?: get height (cm): x: 0-3000
			- temp?: get temperature (°C): x: 0-90
			- attitude?: get IMU attitude data: pitch roll yaw
			- baro?: get barometer value (m): x
			- tof?: get distance value from TOF (cm): x: 30-1000
			- wifi?: get Wi-Fi SNR: snr
		Return:
			bool: The requested value for successful, False for unsuccessful
		"""

		response = self.enviar_comando_con_respuesta(command, printinfo=printinfo)

		try:
			response = str(response)
		except TypeError as e:
			self.LOGGER.error(e)
			pass

		if ('error' not in response) and ('ERROR' not in response) and ('False' not in response):
			if response.isdigit():
				return int(response)
			else:
				try:
					return float(response)  # isdigit() is False when the number is a float(barometer)
				except ValueError:
					return response
		else:
			return self.retornar_error_al_enviar_comando(command, response, self.enable_exceptions)

	def retornar_error_al_enviar_comando(self, command, response, enable_exceptions):
		"""Returns False and print an informative result code to show unsuccessful response"""
		msg = 'El comando ' + command + ' no tuvo éxito. Mensaje: ' + str(response)
		
		# MEDIDA SEGURIDAD by LUCHO
		if self.esta_volando:
			self.end()

		if enable_exceptions:
			raise Exception(msg)
		else:
			self.LOGGER.error(msg)
			return False

	# --- COMANDOS DERIVADOS ---
	# COMANDOS DE CONTROL (A - SETEOS)

	def conectar(self): # COMANDAR - NECESARIO PARA RECIBIR OTROS COMANDOS
		"""Entry SDK mode
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_de_control("command")

	def setear_credenciales_wifi(self, ssid, password):
		"""Set the Wi-Fi SSID and password. The Tello will reboot afterwords.
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_de_control('wifi %s %s' % (ssid, password))

	def conectar_a_wifi(self, ssid, password):
		"""Connects to the Wi-Fi with SSID and password.
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_de_control('ap %s %s' % (ssid, password))

	def setear_stream_on(self):
		"""Set video stream on. If the response is 'Unknown command' means you have to update the Tello firmware. That
		can be done through the Tello app.
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		# Primer condicional by LUCHO
		if not self.stream_on:
			result = self.enviar_comando_de_control("streamon") 
			if result is True:
				self.stream_on = True
			return result
		# else:
		#	 return False # by LUCHO

	def setear_stream_off(self):
		"""Set video stream off
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		# Primer condicional by LUCHO
		if self.stream_on:
			result = self.enviar_comando_de_control("streamoff")
			if result is True:
				self.stream_on = False
			return result
		# else:
		#	 return False # by LUCHO

	@accepts(x=int)
	def setear_velocidad(self, x):
		"""Set speed to x cm/s.
		Arguments:
			x: 10-100
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_de_control("speed " + str(x))

	def habilitar_mpads(self): # By LUCHO
		self.mpads_enabled = False
		return self.enviar_comando_de_control("moff")

	def deshabilitar_mpads(self): # By LUCHO
		self.mpads_enabled = True
		return self.enviar_comando_de_control("mon")


	# COMANDOS DE CONTROL (B - DESPEGUE - ATERRIZAJE - EMERGENCIA)

	def despegar(self):
		"""Tello auto takeoff
		Returns:
			bool: True for successful, False for unsuccessful
			False: Unsuccessful
		"""
		# Something it takes a looooot of time to take off and return a succesful take off. So we better wait. If not, is going to give us error on the following calls.
		# Primer Condicional by LUCHO
		if not self.esta_volando:
			if self.enviar_comando_de_control("takeoff", timeout=20):
				self.esta_volando = True
				return True
			else:
				return False
		else:
			self.LOGGER.warning("NO intentar despegar cuando el dron está en vuelo.")
			return False # by LUCHO

	def aterrizar(self):
		"""Tello auto land
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		# Primer Condicional by LUCHO
		if self.esta_volando:
			if self.enviar_comando_de_control("land"):
				self.esta_volando = False
				return True
			else:
				return False
		else:
			self.LOGGER.warning("NO intentar aterrizar cuando el dron no está en vuelo.")
			return False # by LUCHO

	def emergencia(self):
		"""Stop all motors immediately
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_de_control("emergency")


	# COMANDOS DE CONTROL (C - MOVIMIENTOS)

	@accepts(direction=str, x=int)
	def mover(self, direction, x):
		"""Tello fly up, down, left, right, forward or back with distance x cm.
		Arguments:
			direction: up, down, left, right, forward or back
			x: 20-500
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_de_control(direction + ' ' + str(x))

	@accepts(x=int)
	def mover_arriba(self, x):
		"""Tello fly up with distance x cm.
		Arguments:
			x: 20-500
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.mover("up", x)

	@accepts(x=int)
	def mover_abajo(self, x):
		"""Tello fly down with distance x cm.
		Arguments:
			x: 20-500
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.mover("down", x)

	@accepts(x=int)
	def mover_izquierda(self, x):
		"""Tello fly left with distance x cm.
		Arguments:
			x: 20-500
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.mover("left", x)

	@accepts(x=int)
	def mover_derecha(self, x):
		"""Tello fly right with distance x cm.
		Arguments:
			x: 20-500
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.mover("right", x)

	@accepts(x=int)
	def mover_adelante(self, x):
		"""Tello fly forward with distance x cm.
		Arguments:
			x: 20-500
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.mover("forward", x)

	@accepts(x=int)
	def mover_atras(self, x):
		"""Tello fly back with distance x cm.
		Arguments:
			x: 20-500
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.mover("back", x)

	@accepts(x=int)
	def rotar_sentido_horario(self, x):
		"""Tello rotate x degree clockwise.
		Arguments:
			x: 1-360
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_de_control("cw " + str(x))

	@accepts(x=int)
	def rotar_anti_sentido_horario(self, x):
		"""Tello rotate x degree counter-clockwise.
		Arguments:
			x: 1-3600
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_de_control("ccw " + str(x))

	@accepts(x=str)
	def voltear_flip(self, direction):
		"""Tello fly flip.
		Arguments:
			direction: l (left), r (right), f (forward) or b (back)
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_de_control("flip " + direction)

	def voltear_flip_izquierda(self):
		"""Tello fly flip left.
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.voltear_flip("l")

	def voltear_flip_derecha(self):
		"""Tello fly flip right.
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.voltear_flip("r")

	def voltear_flip_adelante(self):
		"""Tello fly flip left.
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.voltear_flip("f")

	def voltear_flip_atras(self):
		"""Tello fly flip left.
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.voltear_flip("b")


	# COMANDOS DE LECTURA

	def obtener_velocidad(self):
		"""Get current speed (cm/s)
		Returns:
			False: Unsuccessful
			int: 1-100
		"""
		return self.enviar_comando_de_lectura('speed?')

	def obtener_bateria(self):
		"""Get current battery percentage
		Returns:
			False: Unsuccessful
			int: -100
		"""
		return self.enviar_comando_de_lectura('battery?')

	def obtener_tiempo_vuelo(self):
		"""Get current fly time (s)
		Returns:
			False: Unsuccessful
			int: Seconds elapsed during flight.
		"""
		return self.enviar_comando_de_lectura('time?')

	def obtener_altura(self):
		"""Get height (cm)
		Returns:
			False: Unsuccessful
			int: 0-3000
		"""
		return self.enviar_comando_de_lectura('height?')

	def obtener_temperatura(self):
		"""Get temperature (°C)
		Returns:
			False: Unsuccessful
			int: 0-90
		"""
		return self.enviar_comando_de_lectura('temp?')

	def obtener_attitude(self):
		"""Get IMU attitude data
		Returns:
			False: Unsuccessful
			int: pitch roll yaw
		"""
		r = self.enviar_comando_de_lectura('attitude?').replace(';', ':').split(':')
		return dict(zip(r[::2], [int(i) for i in r[1::2]]))  # {'pitch': xxx, 'roll': xxx, 'yaw': xxx}

	def obtener_barometro(self):
		"""Get barometer value (m)
		Returns:
			False: Unsuccessful
			int: 0-100
		"""
		return self.enviar_comando_de_lectura('baro?')

	def obtener_distancia_tof(self):
		"""Get distance value from TOF (cm)
		Returns:
			False: Unsuccessful
			int: 30-1000
		"""
		return self.enviar_comando_de_lectura('tof?')

	def obtener_wifi(self):
		"""Get Wi-Fi SNR
		Returns:
			False: Unsuccessful
			str: snr
		"""
		return self.enviar_comando_de_lectura('wifi?')

	def obtener_numero_serie(self):
		"""Get Serial Number
		Returns:
			False: Unsuccessful
			str: Serial Number
		"""
		return self.enviar_comando_de_lectura('sn?')

	def obtener_version_sdk(self):
		"""Get SDK Version
		Returns:
			False: Unsuccessful
			str: SDK Version
		"""
		return self.enviar_comando_de_lectura('sdk?')

	def setear_datos_sdk(self):  #By LUCHO:
		sd = self.obtener_version_sdk()
		self.sdk = sd
		return sd


	# COMANDOS SIN RESPUESTA [VOLAR (GO) y CURVAS XYZ; ENVIAR VELOCIDADES CR]

	@accepts(x=int, y=int, z=int, speed=int)
	def volar_hacia_xyz_velocidad(self, x, y, z, speed):
		"""Tello fly to x y z in speed (cm/s)
		Arguments:
			x: 20-500
			y: 20-500
			z: 20-500
			speed: 10-100
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_sin_respuesta('go %s %s %s %s' % (x, y, z, speed))

	@accepts(x1=int, y1=int, z1=int, x2=int, y2=int, z2=int, speed=int)
	def curvar_xyz_velocidad(self, x1, y1, z1, x2, y2, z2, speed):
		"""Tello fly a curve defined by the current and two given coordinates with speed (cm/s).
			- If the arc radius is not within the range of 0.5-10 meters, it responses false.
			- x/y/z can’t be between -20 – 20 at the same time.
		Arguments:
			x1: 20-500
			x2: 20-500
			y1: 20-500
			y2: 20-500
			z1: 20-500
			z2: 20-500
			speed: 10-60
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		return self.enviar_comando_sin_respuesta('curve %s %s %s %s %s %s %s' % (x1, y1, z1, x2, y2, z2, speed))


	last_rc_control_sent = 0

	@accepts(left_right_velocity=int, forward_backward_velocity=int, up_down_velocity=int, yaw_velocity=int)
	def enviar_velocidades_control_remoto(self, left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity):
		"""Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
		Arguments:
			left_right_velocity: -100~100 (left/right)
			forward_backward_velocity: -100~100 (forward/backward)
			up_down_velocity: -100~100 (up/down)
			yaw_velocity: -100~100 (yaw)
		Returns:
			bool: True for successful, False for unsuccessful
		"""
		if int(time.time() * 1000) - self.last_rc_control_sent < self.TIME_BTW_RC_CONTROL_COMMANDS:
			pass
		else:
			self.last_rc_control_sent = int(time.time() * 1000)
			return self.enviar_comando_sin_respuesta('rc %s %s %s %s' % (self.round_to_100(left_right_velocity), self.round_to_100(forward_backward_velocity), self.round_to_100(up_down_velocity), self.round_to_100(yaw_velocity)))

	@accepts(x=int)
	def round_to_100(self, x):
		if x > 100:
			return 100
		elif x < -100:
			return -100
		else:
			return x

	# --- FINALIZACIÓN INSTANCIA ---

	def end(self):
		"""Call this method when you want to end the tello object"""
		# Condicional try except by LUCHO
		intentoExistoso = True
		try:
			if self.esta_volando:
				self.aterrizar()
			if self.stream_on:
				self.setear_stream_off()
			if self.background_frame_read is not None:
				self.background_frame_read.stop()
			if self.cap is not None:
				self.cap.release()
		except:
			intentoExistoso = False # by LUCHO

		if intentoExistoso:
			self.LOGGER.warning("La conexión con el Dron finalizó exitosamente") # by LUCHO
			return True
		else:
			self.LOGGER.warning("Inconvenientes al finalizar la conexión con el Dron") # by LUCHO
			return False


	def __del__(self):
		self.end()



# --- VIDEO, CV2 ETC---

class BackgroundFrameRead:
	"""
	This class read frames from a VideoCapture in background. Then, just call backgroundFrameRead.frame to get the
	actual one.
	"""

	def __init__(self, tello, address):
		tello.cap = cv2.VideoCapture(address)
		self.cap = tello.cap

		if not self.cap.isOpened():
			self.cap.open(address)

		self.grabbed, self.frame = self.cap.read()
		self.stopped = False

	def start(self):
		Thread(target=self.update_frame, args=()).start()
		return self

	def update_frame(self):
		while not self.stopped:
			if not self.grabbed or not self.cap.isOpened():
				self.stop()
			else:
				(self.grabbed, self.frame) = self.cap.read()

	def stop(self):
		self.stopped = True

# PARA CONFIGURAR SIN NECESITAR INICIAR INTERFACES (ej: comandos desde script sin GUI)
class TelloAutomatico(Tello):
	def __init__(self, obtencion_estados_habilitada=True):
		super().__init__()

		if not self.conectar():
			self.LOGGER.error("Dron Tello no conectado / No se pudo conectar")
			return

		if not self.setear_datos_sdk():
			self.LOGGER.warning("Datos SDK no recibidos - no se podrá leer estados en segundo plano (a menos que se fuerce el modo)")

		if not self.setear_velocidad(10):
			self.LOGGER.error("No se pudo setear la velocidad - al mínimo posible")
			return

		# In case streaming is on. This happens when we quit this program without the escape key.
		if not self.setear_stream_off():
			self.LOGGER.warning("No fue necesario detener el stream de video")
			return

class TelloSinEstados(Tello):
	def __init__(self):
		super().__init__(obtencion_estados_habilitada=False)

class TelloAutomaticoSinEstados(TelloAutomatico):
	def __init__(self):
		super().__init__(obtencion_estados_habilitada=False)