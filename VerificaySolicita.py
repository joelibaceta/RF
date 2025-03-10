import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime
from twilio.rest import Client
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()
smtp_password = os.getenv("PASSWORD")

def enviar_correo(destinatario, asunto, mensaje):
    # Configuración del servidor SMTP de Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "j.torres.gpm@gmail.com"  # Reemplaza con tu dirección de correo de Gmail
    #  smtp_password = os.getenv("PASSWORD")

    # Crear el mensaje
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = destinatario
    msg["Subject"] = asunto

    # Agregar el cuerpo del mensaje
    msg.attach(MIMEText(mensaje, "plain"))

    try:
        # Conectar al servidor SMTP y enviar el correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Iniciar la conexión TLS
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, destinatario, msg.as_string())
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

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
    cursor.execute('''INSERT INTO invitados (socio, dni, nombre, paterno, materno, motivo, tipo, fecha_evento, ubicacion, fecha_autorizacion, hora_autorizacion, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (socio, dni, nombre, paterno, materno, motivo, tipo, fecha_evento, ubicacion, "", "", "", "", "", ""))
    conn.commit()
    conn.close()
    messagebox.showinfo("Guardado", "Invitado guardado con éxito.")
    update_guest_list(socio, fecha_evento, ubicacion)

    # Envio de correo
    destinatario = "juanperu2006@gmail.com"
    asunto = "Su invitado "+nombre+" "+paterno+" solicita ingresar a "+ubicacion+" por "+motivo+" ingrese al aplicativo y registre a su invitado"
    mensaje = "Su invitado "+nombre+" "+paterno+" solicita ingresar a "+ubicacion+" por "+motivo+" ingrese al aplicativo y registre a su invitado"
    enviar_correo(destinatario, asunto, mensaje)

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
    listbox.insert(tk.END, f"{'DNI':<15} {'Nombre':<20} {'Paterno':<20} {'Materno':<20} {'Motivo':<15} {'Tipo':<10} {'Fecha Autorización':<15} {'Hora Autorización':<15} {'Fecha Ingreso':<15} {'Hora Ingreso':<15}")
    listbox.insert(tk.END, "-"*180)
    for guest in guests:
        listbox.insert(tk.END, f"{guest[0]:<15} {guest[1]:<20} {guest[2]:<20} {guest[3]:<20} {guest[4]:<15} {guest[5]:<10} {guest[6]:<15} {guest[7]:<15} {guest[8]:<15} {guest[9]:<15}")

# Función para actualizar la fecha y hora de ingreso al hacer clic en un invitado
def actualizar_ingreso(event):
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        if index > 1:  # Ignorar encabezado y línea divisoria
            guest_info = listbox.get(index).split()
            dni = guest_info[0]
            socio = entry_socio.get().strip()
            fecha_evento = date_var.get().strip()
            ubicacion = location_var.get().strip()
            fecha_ingreso = datetime.datetime.now().strftime("%Y-%m-%d")
            hora_ingreso = datetime.datetime.now().strftime("%H:%M:%S")
            conn = sqlite3.connect('invitados.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE invitados SET fecha_ingreso=?, hora_ingreso=? WHERE socio=? AND dni=? AND fecha_evento=? AND ubicacion=?", (fecha_ingreso, hora_ingreso, socio, dni, fecha_evento, ubicacion))
            cursor.execute("SELECT dni, nombre, paterno, materno FROM invitados WHERE socio=? AND dni=? AND fecha_evento=? AND ubicacion=?", (socio, dni, fecha_evento, ubicacion))
            guest = cursor.fetchone()
            conn.commit()
            conn.close()
            update_guest_list(socio, fecha_evento, ubicacion)

            # envio correo
            destinatario = "juanperu2006@gmail.com"
            asunto = "Su invitado con DNI "+guest[0] + " y nombre "+ guest[1] + " "+ guest[2]+ " " + guest[3] + " acaba de ingresar"
            mensaje = "Su invitado con DNI "+guest[0] + " y nombre "+ guest[1] + " "+ guest[2]+ " " + guest[3] + " acaba de ingresar"
            enviar_correo(destinatario, asunto, mensaje)

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
location_var.set("Lima")
location_label = tk.Label(step1_frame, text="Ubicación:", font=("Helvetica", 12))
location_label.pack(pady=5)
location_options = ["Lima", "Playa", "Chosica"]
location_menu = tk.OptionMenu(step1_frame, location_var, *location_options)
location_menu.config(font=("Helvetica", 12))
location_menu.pack(pady=5)

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

motivo_label = tk.Label(step2_frame, text="Motivo:", font=("Helvetica", 12))
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

button_guardar = tk.Button(step2_frame, text="Guardar Invitado", font=("Helvetica", 12), command=guardar_invitado)
button_guardar.pack(pady=20)

# Lista para mostrar los invitados registrados
listbox_label = tk.Label(step2_frame, text="Invitados Registrados:", font=("Helvetica", 12))
listbox_label.pack(pady=10)
listbox = tk.Listbox(step2_frame, font=("Helvetica", 12), width=180, height=10)
listbox.pack(pady=5)
listbox.bind('<<ListboxSelect>>', actualizar_ingreso)

root.mainloop()