# coding: utf-8
print("INFO: Se intentará importar y/o instalar todos los módulos necesarios.")
print("INFO: Es probable que deba ejecutar el script varias veces hasta recibir el mensaje: 'TODOS LOS MODULOS CORRECTAMENTE VERIFICADOS'")
print("INFO: Es probable que deba interactuar con el instalador de paquetes pip desde la consola. Lea atentamente cada línea.")
print("INFO: Es importante que ejecute el scrip desde la carpeta local de 'recursos' del proyecto.")
desea_comenzar = input("¿Desea comenzar? Ingrese 'y' para empezar, 'n' para abortar:\n")

def mensajeFallidoLibStand(modulo):
	print("FALLO: Verificación del módulo [" +modulo+ "] fallida.")
	print("IMPORTANTE: El módulo pertenece a la librería standard de Python. Chequee su instalación de Python.")

def mensajeFallido(modulo):
	print("FALLO: Verificación del módulo [" +modulo+ "] fallida.")

def mensajeExitoso(modulo):
	print("EXITOSO: Verificación del módulo [" +modulo+ "] exitosa.")

def install(package):
	subprocess.check_call([sys.executable,"-m", "pip", "install", package])

modulos_standard = ["subprocess","sys","logging","socket","time","threading","tkinter","os"]
modulos_pip = ["numpy", "cv2", "pygame"]
modulos_proyecto = ["decorators","moduloTello", "moduloInterfaz"]

if desea_comenzar=="y":
	for modulo in modulos_standard:
		try:
			exec("import " + modulo)
			mensajeExitoso(modulo)
		except:
			mensajeFallido(modulo)

	debe_continuar = True

	for modulo in modulos_pip:
		try:
			exec("import " + modulo)
			mensajeExitoso(modulo)
		except:
			exitoacumulado = False
			mensajeFallido(modulo)
			print("INFO: Es un paquete instalable. Se intantará instalar. Vuelva a ejecutar el programa al finalizar.")
			debe_continuar=False
			if modulo == "cv2":
				install("opencv-python")
			else:
				install(modulo)
			print("INFO: Se completó el intento de instalación del modulo [" +modulo+ "].")
			print("--- IMPORTANTE --- Vuelva a ejecutar para seguir cheuqeando hasta obenter mensaje final.")
			break

	if debe_continuar:
		print("INFO: Módulos de la librería estandard y/o instalables via controlador de paquetes pip verificados correctamente.")
		print("INFO: Comenzando a verificar módulos del proyecto en archivos locales.")
		for modulo in modulos_proyecto:
			try:
				exec("import " + modulo)
				mensajeExitoso(modulo)
			except:
				mensajeFallido(modulo)
				print("--- IMPORTANTE --- Chequee estar ejecutando el módulo desde la carpeta local 'recursos'.")
				print("--- IMPORTANTE --- Chequee que el archivo '"+ modulo +".py' esté ubicadoen la carpeta local 'recursos'.")
				break

		#Fin bucle
		print("""
---     ¡¡EXITOSO!!     ---


--- TODOS LOS MODULOS CORRECTAMENTE VERIFICADOS ---


--- IMPORTANTE --- Puede proceder a ejecutar los archivos 'test_'
	Recuerde deshabilitar Firewall y conectar el dron mediante wifi antes de ejecutar.

[TEST] 'test_video.py' - Para corroborar transmisión y procesamiento de video del dron y descartar problemas con Firewall.
[TEST] 'test_imagenes.py' - Para corroborar la transmisión de imagen y descartar problemas con Firewall más allá del procesamiento de video.

[TEST] 'test_mensajes_basico.py - Para conocer la version SDK de su dron y corroborar recepción contínua de estados y compatibilidad entre modulo y version SDK.
[TEST] 'test_mensajes_forzado.py' - Para chequear funcionamiento forzando recepción de mensajes pese a incompatibilidad entre módulo y versión SDK.
[TEST] 'test_mensajes_deshabilitado.py' - Para chequear funcionamiento deshabilitando completamente recepción de estados incluso si se detecta SDK supuestamente compatible.

[TEST] 'test_gamepad_botones.py' - Para corroborar conexión gamepad y los valores de cada botón.
[TEST] 'test_gamepad_ejes.py' - Para corroborar en tiempo real el valor leido de cada eje del gamepad.
		
--- FIN EXITOSO ---
""")

else:
	print("--- PROCESO ABORTADO - No se verificó ni instaló ningún módulo - FIN ---")


