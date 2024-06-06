import threading
from flask import Flask, render_template, request
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import ThemedTk
import matplotlib.pyplot as plt
import csv
import openpyxl
from reportlab.pdfgen import canvas
import os
import tempfile
import win32api
import win32print

# Configuración de la aplicación Flask
app = Flask('app')

@app.route('/')
def hello_world():
    print(request.headers)
    return render_template(
        'index.html',
        user_id=request.headers.get('X-Replit-User-Id', 'N/A'),
        user_name=request.headers.get('X-Replit-User-Name', 'N/A'),
        user_roles=request.headers.get('X-Replit-User-Roles', 'N/A'),
        user_bio=request.headers.get('X-Replit-User-Bio', 'N/A'),
        user_profile_image=request.headers.get('X-Replit-User-Profile-Image', 'N/A'),
        user_teams=request.headers.get('X-Replit-User-Teams', 'N/A'),
        user_url=request.headers.get('X-Replit-User-Url', 'N/A')
    )

# Función para iniciar Flask en un hilo separado
def start_flask():
    app.run(host='0.0.0.0', port=8080)

# Aquí empieza el código de Tkinter
PRECIO_60 = 200
PRECIO_REST_1 = 150
PRECIO_REST_2 = 100
PRECIO_REST_3 = 75

# Funciones para cálculos
def calcular_ingresos_y_costos(pallets, unidades_pallet, costo_pallet, costos_fijos, costos_ventas, margen_utilidad):
    total_ingresos = 0
    ingresos_semanales = []

    # Calcular el costo de venta por unidad
    costo_por_unidad = costo_pallet / unidades_pallet

    # Calcular el precio de venta basado en el margen de utilidad
    precio_venta_unidad = costo_por_unidad * (1 + margen_utilidad / 100)

    ventas_por_semana = [
        {"venta_60": unidades_pallet * 0.6, "precio_60": PRECIO_60},
        {"venta_60": unidades_pallet * 0.6, "precio_60": PRECIO_60, "venta_rest_1": unidades_pallet * 0.4, "precio_rest_1": PRECIO_REST_1},
        {"venta_60": unidades_pallet * 0.6, "precio_60": PRECIO_60, "venta_rest_2": unidades_pallet * 0.4, "precio_rest_2": PRECIO_REST_1, "venta_rest_1": unidades_pallet * 0.24, "precio_rest_1": PRECIO_REST_2},
        {"venta_60": unidades_pallet * 0.6, "precio_60": PRECIO_60, "venta_rest_3": unidades_pallet * 0.4, "precio_rest_3": PRECIO_REST_1, "venta_rest_2": unidades_pallet * 0.24, "precio_rest_2": PRECIO_REST_2, "venta_rest_1": unidades_pallet * 0.144, "precio_rest_1": PRECIO_REST_3}
    ]

    for semana in ventas_por_semana:
        ingreso_semana = 0
        for clave, valor in semana.items():
            if "venta" in clave:
                ingreso_semana += valor * semana[clave.replace("venta", "precio")]
        ingresos_semanales.append(ingreso_semana)
        total_ingresos += ingreso_semana

    # Calcular costos
    costo_pallets = pallets * costo_pallet
    costos_fijos_total = sum(costos_fijos.values())
    costo_bolsas = unidades_pallet * pallets * costos_ventas["Bolsas_para_empaquetado"]
    costo_publicidad = costos_ventas["Publicidad"]

    costos_totales = costo_pallets + costos_fijos_total + costo_bolsas + costo_publicidad

    # Beneficio
    beneficio = total_ingresos - costos_totales

    # Punto de equilibrio
    punto_equilibrio_unidades = costos_totales / precio_venta_unidad

    return {
        "ingresos_semanales": ingresos_semanales,
        "total_ingresos": total_ingresos,
        "costos_totales": costos_totales,
        "beneficio": beneficio,
        "punto_equilibrio_unidades": punto_equilibrio_unidades,
        "costo_por_unidad": costo_por_unidad,
        "precio_venta_unidad": precio_venta_unidad
    }

# Función para obtener entrada numérica
def obtener_entrada_numerica(entry_widget):
    try:
        return float(entry_widget.get())
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingresa un número válido.")
        return None

# Función para actualizar los resultados
def actualizar_resultados():
    global resultados
    pallets = obtener_entrada_numerica(entry_pallets)
    unidades_pallet = obtener_entrada_numerica(entry_unidades_pallet)
    costo_pallet = obtener_entrada_numerica(entry_costo_pallet)
    margen_utilidad = obtener_entrada_numerica(entry_margen_utilidad)

    costos_fijos = {
        "Renta": obtener_entrada_numerica(entry_renta),
        "Nómina": obtener_entrada_numerica(entry_nomina),
        "Internet": obtener_entrada_numerica(entry_internet),
        "Luz": obtener_entrada_numerica(entry_luz)
    }

    costos_ventas = {
        "Publicidad": obtener_entrada_numerica(entry_publicidad),
        "Bolsas_para_empaquetado": obtener_entrada_numerica(entry_bolsas)
    }

    if None not in [pallets, unidades_pallet, costo_pallet, margen_utilidad] and all(value is not None for value in costos_fijos.values()) and all(value is not None for value in costos_ventas.values()):
        resultados = calcular_ingresos_y_costos(pallets, unidades_pallet, costo_pallet, costos_fijos, costos_ventas, margen_utilidad)

        lbl_ingresos_semanales.config(text=f"Ingresos Semanales: {resultados['ingresos_semanales']}")
        lbl_total_ingresos.config(text=f"Ingreso Total del Mes: ${resultados['total_ingresos']:.2f}")
        lbl_costos_totales.config(text=f"Costos Totales Mensuales: ${resultados['costos_totales']:.2f}")
        lbl_beneficio.config(text=f"Beneficio Mensual: ${resultados['beneficio']:.2f}")
        lbl_punto_equilibrio.config(text=f"Punto de Equilibrio (unidades): {resultados['punto_equilibrio_unidades']:.2f}")
        lbl_costo_por_unidad.config(text=f"Costo de Venta por Unidad: ${resultados['costo_por_unidad']:.2f}")
        lbl_precio_venta_unidad.config(text=f"Precio de Venta por Unidad (con {margen_utilidad}% de margen): ${resultados['precio_venta_unidad']:.2f}")

# Función para guardar resultados en CSV
def guardar_resultados(resultados):
    with open('resultados.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Ingresos Semanales', 'Ingreso Total del Mes', 'Costos Totales Mensuales', 'Beneficio Mensual', 'Punto de Equilibrio (unidades)'])
        writer.writerow([resultados['ingresos_semanales'], resultados['total_ingresos'], resultados['costos_totales'], resultados['beneficio'], resultados['punto_equilibrio_unidades']])

# Función para exportar resultados a Excel
def exportar_a_excel(datos, nombre_archivo):
    wb = openpyxl.Workbook()
    hoja = wb.active
    hoja.append(['Ingresos Semanales', 'Ingreso Total del Mes', 'Costos Totales Mensuales', 'Beneficio Mensual', 'Punto de Equilibrio (unidades)'])
    hoja.append([datos['ingresos_semanales'], datos['total_ingresos'], datos['costos_totales'], datos['beneficio'], datos['punto_equilibrio_unidades']])
    wb.save(nombre_archivo + '.xlsx')

# Función para exportar resultados a PDF
def exportar_a_pdf(datos, nombre_archivo):
    c = canvas.Canvas(nombre_archivo + '.pdf')
    c.drawString(100, 800, 'Resumen Financiero')
    c.drawString(100, 780, f"Ingresos Semanales: {datos['ingresos_semanales']}")
    c.drawString(100, 760, f"Ingreso Total del Mes: ${datos['total_ingresos']:.2f}")
    c.drawString(100, 740, f"Costos Totales Mensuales: ${datos['costos_totales']:.2f}")
    c.drawString(100, 720, f"Beneficio Mensual: ${datos['beneficio']:.2f}")
    c.drawString(100, 700, f"Punto de Equilibrio (unidades): {datos['punto_equilibrio_unidades']:.2f}")
    c.drawString(100, 680, f"Costo de Venta por Unidad: ${datos['costo_por_unidad']:.2f}")
    c.drawString(100, 660, f"Precio de Venta por Unidad (con margen): ${datos['precio_venta_unidad']:.2f}")
    c.save()

# Función para imprimir documento
def imprimir_documento(documento):
    filename = tempfile.mktemp(".txt")
    with open(filename, "w") as f:
        f.write(documento)
    win32api.ShellExecute(
        0,
        "print",
        filename,
        '/d:"%s"' % win32print.GetDefaultPrinter(),
        ".",
        0
    )

# Función para mostrar tooltip
def crear_tooltip(widget, text):
    tooltip = ttk.Label(widget, text=text, relief=tk.SOLID, borderwidth=1, background="#FFFFE0")
    tooltip.pack_forget()

    def enter(event):
        tooltip.place(x=widget.winfo_x() + widget.winfo_width(), y=widget.winfo_y())

    def leave(event):
        tooltip.pack_forget()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

# Crear ventana principal con tema
root = ThemedTk(theme="breeze")
root.title("Calculadora Financiera")

# Crear Frame para organización
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Entradas de datos
ttk.Label(frame, text="Pallets:").grid(column=1, row=1, sticky=tk.W)
entry_pallets = ttk.Entry(frame)
entry_pallets.grid(column=2, row=1)

ttk.Label(frame, text="Unidades por Pallet:").grid(column=1, row=2, sticky=tk.W)
entry_unidades_pallet = ttk.Entry(frame)
entry_unidades_pallet.grid(column=2, row=2)

ttk.Label(frame, text="Costo por Pallet:").grid(column=1, row=3, sticky=tk.W)
entry_costo_pallet = ttk.Entry(frame)
entry_costo_pallet.grid(column=2, row=3)

ttk.Label(frame, text="Margen de Utilidad (%):").grid(column=1, row=4, sticky=tk.W)
entry_margen_utilidad = ttk.Entry(frame)
entry_margen_utilidad.grid(column=2, row=4)

ttk.Label(frame, text="Costos Fijos").grid(column=1, row=5, sticky=tk.W)
ttk.Label(frame, text="Renta:").grid(column=1, row=6, sticky=tk.W)
entry_renta = ttk.Entry(frame)
entry_renta.grid(column=2, row=6)
crear_tooltip(entry_renta, "Costo de renta mensual")

ttk.Label(frame, text="Nómina:").grid(column=1, row=7, sticky=tk.W)
entry_nomina = ttk.Entry(frame)
entry_nomina.grid(column=2, row=7)
crear_tooltip(entry_nomina, "Costo de nómina mensual")

ttk.Label(frame, text="Internet:").grid(column=1, row=8, sticky=tk.W)
entry_internet = ttk.Entry(frame)
entry_internet.grid(column=2, row=8)
crear_tooltip(entry_internet, "Costo de internet mensual")

ttk.Label(frame, text="Luz:").grid(column=1, row=9, sticky=tk.W)
entry_luz = ttk.Entry(frame)
entry_luz.grid(column=2, row=9)
crear_tooltip(entry_luz, "Costo de luz mensual")

ttk.Label(frame, text="Costos de Ventas").grid(column=1, row=10, sticky=tk.W)
ttk.Label(frame, text="Publicidad:").grid(column=1, row=11, sticky=tk.W)
entry_publicidad = ttk.Entry(frame)
entry_publicidad.grid(column=2, row=11)
crear_tooltip(entry_publicidad, "Costo de publicidad mensual")

ttk.Label(frame, text="Bolsas para Empaquetado:").grid(column=1, row=12, sticky=tk.W)
entry_bolsas = ttk.Entry(frame)
entry_bolsas.grid(column=2, row=12)
crear_tooltip(entry_bolsas, "Costo de bolsas para empaquetado por unidad")

# Botón para calcular
btn_calcular = ttk.Button(frame, text="Calcular", command=actualizar_resultados)
btn_calcular.grid(column=2, row=13, pady=10)

# Resultados
lbl_ingresos_semanales = ttk.Label(frame, text="Ingresos Semanales:")
lbl_ingresos_semanales.grid(column=1, row=14, columnspan=2, sticky=tk.W)

lbl_total_ingresos = ttk.Label(frame, text="Ingreso Total del Mes:")
lbl_total_ingresos.grid(column=1, row=15, columnspan=2, sticky=tk.W)

lbl_costos_totales = ttk.Label(frame, text="Costos Totales Mensuales:")
lbl_costos_totales.grid(column=1, row=16, columnspan=2, sticky=tk.W)

lbl_beneficio = ttk.Label(frame, text="Beneficio Mensual:")
lbl_beneficio.grid(column=1, row=17, columnspan=2, sticky=tk.W)

lbl_punto_equilibrio = ttk.Label(frame, text="Punto de Equilibrio (unidades):")
lbl_punto_equilibrio.grid(column=1, row=18, columnspan=2, sticky=tk.W)

lbl_costo_por_unidad = ttk.Label(frame, text="Costo de Venta por Unidad:")
lbl_costo_por_unidad.grid(column=1, row=19, columnspan=2, sticky=tk.W)

lbl_precio_venta_unidad = ttk.Label(frame, text="Precio de Venta por Unidad (con margen):")
lbl_precio_venta_unidad.grid(column=1, row=20, columnspan=2, sticky=tk.W)

# Botones para exportar
btn_exportar_excel = ttk.Button(frame, text="Exportar a Excel", command=lambda: exportar_a_excel(resultados, "resultados"))
btn_exportar_excel.grid(column=1, row=21, pady=10, sticky=tk.W)

btn_exportar_pdf = ttk.Button(frame, text="Exportar a PDF", command=lambda: exportar_a_pdf(resultados, "resultados"))
btn_exportar_pdf.grid(column=2, row=21, pady=10, sticky=tk.W)

# Botón para imprimir
btn_imprimir = ttk.Button(frame, text="Imprimir", command=lambda: imprimir_documento(str(resultados)))
btn_imprimir.grid(column=1, row=22, pady=10, sticky=tk.W)

# Configuración de la cuadrícula
for child in frame.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Iniciar el hilo de Flask
flask_thread = threading.Thread(target=start_flask)
flask_thread.daemon = True
flask_thread.start()

# Iniciar la aplicación Tkinter
root.mainloop()
