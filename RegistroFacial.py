import tkinter as tk
from tkinter import messagebox
import sqlite3
import cv2
import os
import imutils
entry_codigo = 3045

def capturar_rostros(personName):
    dataPath = 'C:\g0\VS\Data' #Cambia a la ruta donde hayas almacenado Data
    personPath = dataPath + '/' + personName
    cantidadrostros = 300
    count = 0
    if not os.path.exists(personPath):
        print('Carpeta creada: ',personPath)
        os.makedirs(personPath)
        cantidadrostros = 300
        count = 0
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    #cap = cv2.VideoCapture('Donald.mp4')  video

    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
   

    while True:
        ret, frame = cap.read()
        if ret == False: break
        frame =  imutils.resize(frame, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        auxFrame = frame.copy()
        faces = faceClassif.detectMultiScale(gray,1.3,5)

        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
            rostro = auxFrame[y:y+h,x:x+w]
            rostro = cv2.resize(rostro,(150,150),interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(personPath + '/rostro_{}.jpg'.format(count),rostro)
            count = count + 1
        cv2.imshow('frame',frame)

        k =  cv2.waitKey(1)
        if k == 27 or count >= cantidadrostros:
            break

    cap.release()
    cv2.destroyAllWindows()

def buscar_datos():
    codigo = entry_codigo.get()
    
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, tipo FROM socio WHERE id=?", (codigo,))
    results = cursor.fetchall()
    
    listbox.delete(0, tk.END)
    if results:
        for result in results:
            listbox.insert(tk.END, f"{result[0]} \t {result[2]} \t {result[1]}")
    else:
        messagebox.showwarning("Error", "Código no encontrado")
    
    conn.close()

def seleccionar_fila(event):
    seleccion = listbox.curselection()
    if seleccion:
        index = seleccion[0]
        data = listbox.get(index)
        data_parts = data.split('\t')
        personName = f"{data_parts[0]}-{data_parts[1]}-{data_parts[2]}"
        personName = personName.replace(" ", "")
        messagebox.showinfo("Fila Seleccionada", personName)
        capturar_rostros(personName)  # Execute script

# Crear la base de datos y la tabla de usuarios si no existen
def setup_db():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS socio
                      (id INTEGER KEY, username TEXT, tipo TEXT)''')
    conn.commit()
    conn.close()

def validasocio():
    global listbox 
    global entry_codigo
# Crear la ventana principal
    root = tk.Tk()
    root.title("Buscar Datos por Número de Socio")
    root.geometry("400x400")
    root.configure(bg="#2c3e50")

    # Crear y colocar los widgets
    frame = tk.Frame(root, bg="#34495e", bd=5)
    frame.place(relx=0.5, rely=0.1, anchor="n")

    tk.Label(frame, text="Número de Socio:", bg="#34495e", fg="white", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_codigo = tk.Entry(frame, font=("Helvetica", 14))
    entry_codigo.grid(row=0, column=1, padx=10, pady=10)

    tk.Button(frame, text="Buscar", command=buscar_datos, bg="#1abc9c", fg="white", font=("Helvetica", 14)).grid(row=1, column=0, columnspan=2, pady=20)

    # Add header labels
    header_frame = tk.Frame(root, bg="#34495e")
    header_frame.place(relx=0.5, rely=0.25, anchor="n", relwidth=0.8)
    tk.Label(header_frame, text="ID", bg="#34495e", fg="white", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=5)
    tk.Label(header_frame, text="Tipo", bg="#34495e", fg="white", font=("Helvetica", 14)).grid(row=0, column=1, padx=10, pady=5)
    tk.Label(header_frame, text="Nombre", bg="#34495e", fg="white", font=("Helvetica", 14)).grid(row=0, column=2, padx=10, pady=5)

    listbox = tk.Listbox(root, font=("Helvetica", 14), bg="#34495e", fg="white")
    listbox.place(relx=0.5, rely=0.3, anchor="n", relwidth=0.8, relheight=0.6)
    listbox.bind('<<ListboxSelect>>', seleccionar_fila)

    # Configurar la base de datos
    setup_db()

    # Iniciar el bucle principal de la interfaz gráfica
#    root.mainloop()

def login():
    username = entry_username.get()
    password = entry_password.get()
    
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    cursor_temp = conn.cursor()
    
    cursor_temp.execute("SELECT * FROM usuarios")
    print(cursor_temp.fetchone()[0])
    
    
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    
    
    
    result = cursor.fetchone()
    
    if result:
        messagebox.showinfo("Login Info", f"Bienvenido {username}")
        validasocio()  # Execute the validasocio.py script
    else:
        messagebox.showwarning("Input Error", "Usuario o clave incorrectos")
    
    conn.close()

# Crear la base de datos y la tabla de usuarios si no existen
def setup_db():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                      (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

# Crear la ventana principal
root = tk.Tk()
root.title("Sistema de Reconocimiento Facial")
root.geometry("400x300")
root.configure(bg="#2c3e50")

# Crear y colocar los widgets
frame = tk.Frame(root, bg="#34495e", bd=5)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Usuario:", bg="#34495e", fg="white", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_username = tk.Entry(frame, font=("Helvetica", 14))
entry_username.grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame, text="Clave:", bg="#34495e", fg="white", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_password = tk.Entry(frame, show="*", font=("Helvetica", 14))
entry_password.grid(row=1, column=1, padx=10, pady=10)

tk.Button(frame, text="Ingresar", command=login, bg="#1abc9c", fg="white", font=("Helvetica", 14)).grid(row=2, column=0, columnspan=2, pady=20)

# Configurar la base de datos
setup_db()

# Iniciar el bucle principal de la interfaz gráfica
root.mainloop()
