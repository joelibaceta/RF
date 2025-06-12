import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import datetime

# Función para crear la base de datos y la tabla si no existen
def create_db():
    conn = sqlite3.connect('invitados.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS invitados (
                        socio INTEGER,
                        dni TEXT,
                        nombre TEXT,
                        paterno TEXT,
                        materno TEXT,
                        motivo TEXT,
                        tipo TEXT,
                        fecha_evento TEXT,
                        ubicacion TEXT,
                        fecha_autorizacion TEXT,
                        hora_autorizacion TEXT,
                        fecha_ingreso TEXT,
                        hora_ingreso TEXT,
                        fecha_salida TEXT,
                        hora_salida TEXT,
                        UNIQUE(socio, dni, fecha_evento, ubicacion)
                      )''')
    conn.commit()
    conn.close()

# Función para guardar un invitado en la base de datos
def save_invitado(socio, fecha_evento, dni, nombre, paterno, materno, motivo, tipo, ubicacion):
    conn = sqlite3.connect('invitados.db')
    cursor = conn.cursor()
    fecha_autorizacion = datetime.datetime.now().strftime("%Y-%m-%d")
    hora_autorizacion = datetime.datetime.now().strftime("%H:%M:%S")
    cursor.execute('''INSERT INTO invitados (socio, dni, nombre, paterno, materno, motivo, tipo, fecha_evento, ubicacion, fecha_autorizacion, hora_autorizacion, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (socio, dni, nombre, paterno, materno, motivo, tipo, fecha_evento, ubicacion, fecha_autorizacion, hora_autorizacion, "", "", "", ""))
    conn.commit()
    conn.close()
    messagebox.showinfo("Guardado", "Invitado guardado con éxito.")
    update_guest_list(socio, fecha_evento, ubicacion)

# Función para pasar del paso 1 al paso 2
def go_to_step2():
    socio = entry_socio.get().strip()
    if not socio.isdigit():
        messagebox.showerror("Error", "El código de socio debe ser un número.")
        return
    step1_frame.pack_forget()
    step2_frame.pack(fill="both", expand=True)
    update_guest_list(socio, date_var.get(), location_var.get())
    label_encabezado.config(text=f"Socio: {socio} - Fecha Evento: {date_var.get()} - Ubicación: {location_var.get()}")

# Función para procesar y guardar los datos del invitado
def guardar_invitado():
    dni = entry_dni.get().strip()
    nombre = entry_nombre.get().strip()
    paterno = entry_paterno.get().strip()
    materno = entry_materno.get().strip()
    motivo = entry_motivo.get().strip()
    tipo = tipo_var.get()
    fecha_evento = date_var.get().strip()
    socio = entry_socio.get().strip()
    ubicacion = location_var.get().strip()
    if dni == "" or nombre == "" or paterno == "" or materno == "" or motivo == "":
        messagebox.showerror("Error", "Todos los campos deben ser completados.")
        return

    save_invitado(socio, fecha_evento, dni, nombre, paterno, materno, motivo, tipo, ubicacion)
    # Limpiar campos
    entry_dni.delete(0, tk.END)
    entry_nombre.delete(0, tk.END)
    entry_paterno.delete(0, tk.END)
    entry_materno.delete(0, tk.END)
    entry_motivo.delete(0, tk.END)

# Función para actualizar la lista de invitados
def update_guest_list(socio, fecha_evento, ubicacion):
    conn = sqlite3.connect('invitados.db')
    cursor = conn.cursor()
    cursor.execute("SELECT dni, nombre, paterno, materno, motivo, tipo, fecha_autorizacion, hora_autorizacion, fecha_ingreso, hora_ingreso FROM invitados WHERE socio=? AND fecha_evento=? AND ubicacion=?", (socio, fecha_evento, ubicacion))
    guests = cursor.fetchall()
    conn.close()

    listbox.delete(0, tk.END)
    listbox.insert(tk.END, f"{'DNI':<15} {'Nombre':<20} {'Paterno':<20} {'Materno':<20} {'Motivo':<15} {'Tipo':<10} {'Fec Autoriz':<15} {'Hora Autoriza':<15} {'Fecha Ingreso':<15} {'Hora Ingreso':<15}")
    listbox.insert(tk.END, "-"*180)
    for guest in guests:
        listbox.insert(tk.END, f"{guest[0]:<15} {guest[1]:<20} {guest[2]:<20} {guest[3]:<20} {guest[4]:<15} {guest[5]:<10} {guest[6]:<15} {guest[7]:<15} {guest[8]:<15} {guest[9]:<15}")

# Función para actualizar la fecha y hora de autorización al hacer clic en un invitado
def actualizar_autorizacion(event):
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        if index > 1:  # Ignorar encabezado y línea divisoria
            guest_info = listbox.get(index).split()
            dni = guest_info[0]
            socio = entry_socio.get().strip()
            fecha_evento = date_var.get().strip()
            ubicacion = location_var.get().strip()
            fecha_autorizacion = datetime.datetime.now().strftime("%Y-%m-%d")
            hora_autorizacion = datetime.datetime.now().strftime("%H:%M:%S")
            conn = sqlite3.connect('invitados.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE invitados SET fecha_autorizacion=?, hora_autorizacion=? WHERE socio=? AND dni=? AND fecha_evento=? AND ubicacion=?", 
                           (fecha_autorizacion, hora_autorizacion, socio, dni, fecha_evento, ubicacion))
            cursor.execute("SELECT dni, nombre, paterno, materno FROM invitados WHERE socio=? AND dni=? AND fecha_evento=? AND ubicacion=?", 
                           (socio, dni, fecha_evento, ubicacion))
            guest = cursor.fetchone()
            conn.commit()
            conn.close()
            update_guest_list(socio, fecha_evento, ubicacion)

# Crear la ventana principal
root = tk.Tk()
root.title("Solicitud de autorización al socio")
root.geometry("1200x600")
create_db()

# --- Paso 1: Selecciona fecha y ubicación ---
step1_frame = tk.Frame(root)
step1_frame.pack(fill="both", expand=True)

label_step1 = tk.Label(step1_frame, text="Paso 1: Selecciona fecha y ubicación", font=("Helvetica", 16))
label_step1.pack(pady=10)

# Ingreso del código de socio
socio_label = tk.Label(step1_frame, text="Código de Socio:", font=("Helvetica", 12))
socio_label.pack(pady=5)
entry_socio = tk.Entry(step1_frame, font=("Helvetica", 12))
entry_socio.pack(pady=5)

# Mostrar fecha de hoy (se puede modificar)
date_var = tk.StringVar()
date_var.set(datetime.date.today().strftime("%Y-%m-%d"))
date_label = tk.Label(step1_frame, text="Fecha Evento (YYYY-MM-DD):", font=("Helvetica", 12))
date_label.pack(pady=5)
date_entry = tk.Entry(step1_frame, textvariable=date_var, font=("Helvetica", 12))
date_entry.pack(pady=5)

# Menú desplegable para elegir ubicación
location_var = tk.StringVar()
location_var.set("San Isidro")  # Valor por defecto
location_label = tk.Label(step1_frame, text="Ubicación:", font=("Helvetica", 12))
location_label.pack(pady=5)
location_options = ["San Isidro", "Ricado Palma", "Asia","Restaurant","Peña","Bar","Invitado Academia"]
location_menu = tk.OptionMenu(step1_frame, location_var, *location_options)
location_menu.config(font=("Helvetica", 12))
location_menu.pack(pady=5)

# Label para mostrar el mensaje según la ubicación
mensaje_ubicacion_label = tk.Label(step1_frame, text="", font=("Helvetica", 12), fg="blue", justify="left")
mensaje_ubicacion_label.pack(pady=5)

def actualizar_mensaje_ubicacion(*args):
    if location_var.get() == "San Isidro":
        mensaje_ubicacion_label.config(
            text="INGRESO DE INVITADOS SEDE PRINCIPAL\n\n•De lunes a viernes\n\nIngreso máximo de 2 invitados sin costo."
        )
    elif location_var.get() == "Restaurant":
        mensaje_ubicacion_label.config(
            text="INGRESO DE INVITADOS RESTAURANT\n\n"
                 "•De lunes a viernes\n"
                 "Ingreso máximo de 8 invitados sin costo por día.\n\n"
                 "•Sábado y Domingo\n"
                 "Ingreso máximo de 4 invitados sin costo por día.\n\n"
                 "S/. 5 por invitado adicional."
        )
    elif location_var.get() == "Peña":
        mensaje_ubicacion_label.config(
            text="INGRESO DE INVITADOS A LA PEÑA\n\n"
                 "•viernes\n"
                 "Ingreso máximo de 4 invitados sin costo.\n\n"
                 "S/. 15 por invitado adicional."
        )
    elif location_var.get() == "Bar":
        mensaje_ubicacion_label.config(
            text="INGRESO DE INVITADOS RESTAL BAR\n\n"
                 "•De lunes a Domingo\n"
                 "Ingreso máximo de 4 invitados sin costo por día.\n\n"
                 "S/. 10 por invitado adicional."
        )
    elif location_var.get() == "Asia":
        mensaje_ubicacion_label.config(
            text="INGRESO DE INVITADOS SEDE Asia\n\n"
                 "•De lunes a Domingo\n\n"
                 "Ingreso máximo de 4 invitados pagantes.\n\n"
                 "S/. 50 Adultos / 12 o más años   o    S/25 Niños / de 3 a 11."
        )
    elif location_var.get() == "Invitado Academia":
        mensaje_ubicacion_label.config(
            text="INGRESO DE INVITADOS ACADEMIA\n\n"
                 "se activa 30 minutos antes de academia"
        )
    else:
        mensaje_ubicacion_label.config(text="INGRESO DE INVITADOS SEDE Ricado Palma\n\n"
                 "•De lunes a Domingo\n\n"
                 "S/. 30 Adultos / 12 o más años   o    S/10 Niños / De 3 a  11.")

# Asociar la función al cambio de valor de location_var
location_var.trace("w", actualizar_mensaje_ubicacion)

# Mostrar el mensaje inicial si la ubicación es Lima
actualizar_mensaje_ubicacion()

button_continue = tk.Button(step1_frame, text="Continuar", font=("Helvetica", 12), command=go_to_step2)
button_continue.pack(pady=20)

# --- Paso 2: Agrega a tus invitados ---
step2_frame = tk.Frame(root)

# Esta pantalla se mostrará luego de presionar "Continuar"
label_step2 = tk.Label(step2_frame, text="Solicitud de autorización al socio", font=("Helvetica", 16))
label_step2.pack(pady=10)

# Mostrar encabezado
label_encabezado = tk.Label(step2_frame, text="", font=("Helvetica", 12))
label_encabezado.pack(pady=10)

dni_label = tk.Label(step2_frame, text="DNI:", font=("Helvetica", 12))
dni_label.pack(pady=5)
entry_dni = tk.Entry(step2_frame, font=("Helvetica", 12))
entry_dni.pack(pady=5)

nombre_label = tk.Label(step2_frame, text="Nombre:", font=("Helvetica", 12))
nombre_label.pack(pady=5)
entry_nombre = tk.Entry(step2_frame, font=("Helvetica", 12))
entry_nombre.pack(pady=5)

paterno_label = tk.Label(step2_frame, text="Apellido Paterno:", font=("Helvetica", 12))
paterno_label.pack(pady=5)
entry_paterno = tk.Entry(step2_frame, font=("Helvetica", 12))
entry_paterno.pack(pady=5)

materno_label = tk.Label(step2_frame, text="Apellido Materno:", font=("Helvetica", 12))
materno_label.pack(pady=5)
entry_materno = tk.Entry(step2_frame, font=("Helvetica", 12))
entry_materno.pack(pady=5)

motivo_label = tk.Label(step2_frame, text="Observacion:", font=("Helvetica", 12))
motivo_label.pack(pady=5)
entry_motivo = tk.Entry(step2_frame, font=("Helvetica", 12))
entry_motivo.pack(pady=5)

# Menú desplegable para seleccionar si es pago o gratuito
tipo_label = tk.Label(step2_frame, text="Tipo:", font=("Helvetica", 12))
tipo_label.pack(pady=5)
tipo_var = tk.StringVar()
tipo_var.set("Pago")
tipo_options = ["Pago", "Gratuito"]
tipo_menu = tk.OptionMenu(step2_frame, tipo_var, *tipo_options)
tipo_menu.config(font=("Helvetica", 12))
tipo_menu.pack(pady=5)

# Botones para agregar invitado y pago online en la misma fila
button_frame = tk.Frame(step2_frame)
button_frame.pack(pady=20)

button_guardar = tk.Button(button_frame, text="Agregar Invitado", font=("Helvetica", 12), command=guardar_invitado)
button_guardar.pack(side="left", padx=10)

button_pago_online = tk.Button(button_frame, text="Pago on line de invitados", font=("Helvetica", 12))
button_pago_online.pack(side="left", padx=10)

# Lista para mostrar los invitados registrados
listbox_label = tk.Label(step2_frame, text="Invitados Agregados:", font=("Helvetica", 12))
listbox_label.pack(pady=10)
listbox = tk.Listbox(step2_frame, font=("Helvetica", 12), width=180, height=10)
listbox.pack(pady=5)
listbox.bind('<<ListboxSelect>>', actualizar_autorizacion)

root.mainloop()
