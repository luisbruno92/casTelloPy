# coding: utf8
# COMPRENDER USO DE ENVOLTORIO WRAPPER DECORATOR @ACCEPTS EN FUNCIONES MODULO TELLO
from decorators import accepts

# El decorador @acepts nos permitirá definir qué tipo de parámetros acepta cada función.
# Así, podríamos evitar errores "semánticos" al obtener resultados inesperados.

# Por ejemplo, la siguiente función, solo acepta enteros como argumentos al ejecutarse.
@accepts(numA=int, numB=int)
def sumar(numA, numB):
	print("EL RESULTADO ES...")
	print(numA + numB)

sumar(6,8) # --> Obtenemos 14

# Si intentamos...
def sumarCualquierCosa(datoA, datoB):
	print("EL RESULTADO ES...")
	print(datoA + datoB)

sumarCualquierCosa("6","8") # --> Obtenemos "68"

# Pero si usamos la función con el @accepts e intentamos hacer lo mismo
sumar("6","8") 
# --> Obtenemos un error en consola que nos informa la "situación problemática semánticamente"
# --> TypeError: arg 'numA'='6' does not match <class 'int'>
# --> (Es decir..)
# --> Error de Tipo: El argumento 'numA'='6' no coincide con <clase 'int'(entero)>