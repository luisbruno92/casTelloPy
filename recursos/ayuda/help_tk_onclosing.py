# HANDLE CIERRE DE VENTANAS EN TKINTER CON PROTOCOLO DE ROOT
import tkinter as tk

se_puede = True

def on_closing():
	print ("INTENTANDO CERRAR")
	if se_puede:
		print("CERRASTE")
		root.destroy()

root = tk.Tk()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

