# coding: utf8
# COMPRENDER PASO DE CALLBACKS PARA SETEO DE INTERFACES Y CONTROLES, 
# CON FUNCIONES GLOBALES/EXTERNAS A LA CLASE QUE SE EJECUTARÁN EN MÉTODOS DE OBJETOS INSTANCIADOS.

def controladorGamepad(unDron, boton):
	# En realidad conlleva procesos más complejos, pero se testea con print ajustado
	print(unDron.nombre + " dice: Me estan controlando presionando el boton '" + boton + "'.")


class FalsoTello:
	def __init__(self, nom):
		self.nombre = nom
		self.callBack = False
		self.interface = False

	def setearControl(self, funcion):
		self.callBack = funcion

	def setearVentana(self, vent):
		self.ventana = vent

	def controlarDron (self, btn=False): # "NOTA" sobre kwarg al final.
		if(self.callBack):
			self.callBack(self, btn)
		else:
			print(self.nombre + " dice: No tengo control para procesar botones.")
			# o bien sin else, o bien...
			#pass
	
	def mostrarVideo (self):
		if(self.interface):
			# Deberá hacer algo que seguiria la siguiente logica:
			# self.interface.alimentarConFeedVideoStream(self.sistemaRecepecionVideo)
			# Pero testeo con un print ajustado:
			print(self.nombre + "dice: estoy mostrando video en " + self.ventana)
		else:
			print(self.nombre + " dice: No tengo ventana para mostrar video.")
			# o bien sin else, o bien...
			#pass 

dron1 = FalsoTello("Juliana")
dron1.controlarDron("key_down_ESC") # esta no es la sintaxis fiel de pygame
dron1.mostrarVideo()

dron2 = FalsoTello("Roberta")
dron2.setearControl(controladorGamepad) # es decir, la función global, que puede estar en otro archivo
dron2.controlarDron("key_up_W") # esta no es la sintaxis fiel de pygame

dron3 = FalsoTello("Emilia")
dron3.setearVentana("miVentana falsa") # imaginar, en cambio, variable donde se aloja root de Tk()
dron3.mostrarVideo()

# NOTA
# btn=False para evitar errores si usuario-programador escribe...
# dron1.controlarDron() # sin agrumentos - descomentar para chequear.



