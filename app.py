# Importamos las bibliotecas necesarias
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import random  # Para la selección aleatoria de plataformas en los combos
import pandas as pd  # Para manejar archivos Excel
import os  # Para manejar rutas de archivos en el sistema

# Inicializamos la aplicación Flask
app = Flask(__name__)
app.secret_key = 'supersecreto'  # Clave secreta para manejar sesiones en Flask

# ----------------------------- FUNCION PARA GENERAR COMBOS -----------------------------

def generar_combos(cantidad, plataformas_seleccionadas, nombre_base, plataforma_inicio, plataforma_fin, costos=None):
    """
    Función que genera combos de plataformas de streaming de manera aleatoria.

    Parámetros:
    - cantidad: Número total de combos a generar.
    - plataformas_seleccionadas: Lista de plataformas seleccionadas por el usuario.
    - nombre_base: Nombre base que se usará para los combos.
    - plataforma_inicio: Plataforma inicial obligatoria (si se seleccionó una).
    - plataforma_fin: Plataforma final obligatoria (si se seleccionó una).
    - costos: Diccionario con los precios de cada plataforma.

    Retorna:
    - Lista de combos generados, donde cada combo es una tupla (nombre, descripción, costo total).
    """

    # Si no se proporciona el diccionario de costos, se inicializa vacío
    if costos is None:
        costos = {}

    # Lista donde se almacenarán los combos generados
    combos = []

    # Intentamos extraer el número de plataformas desde el nombre del combo
    try:
        num_plataformas = int(''.join(filter(str.isdigit, nombre_base)))  # Extrae solo los números del nombre
    except ValueError:
        num_plataformas = 3  # Si no hay números en el nombre, por defecto toma 3 plataformas

    # Asegurar que el número de plataformas sea válido y no exceda la cantidad seleccionada
    num_plataformas = max(1, min(num_plataformas, len(plataformas_seleccionadas) - 1))

    # Generamos los combos según la cantidad solicitada
    for i in range(1, cantidad + 1):
        combo = []  # Lista donde se almacenará el combo actual
        
        # Si se seleccionó una plataforma inicial, la agregamos al combo
        if plataforma_inicio and plataforma_inicio in plataformas_seleccionadas:
            combo.append(plataforma_inicio)

        # Seleccionar aleatoriamente plataformas adicionales sin repetir la plataforma inicial ni la final
        seleccionables = [p for p in plataformas_seleccionadas if p not in combo and p != plataforma_fin]
        seleccionadas = random.sample(seleccionables, k=min(len(seleccionables), num_plataformas - len(combo)))
        combo.extend(seleccionadas)

        # Si aún faltan plataformas, se agregan aleatoriamente
        while len(combo) < num_plataformas:
            faltantes = [p for p in seleccionables if p not in combo]
            if not faltantes:
                break  # Si no quedan más plataformas disponibles, terminamos
            combo.append(random.choice(faltantes))  # Agregar una plataforma aleatoria faltante

        # Si hay una plataforma final seleccionada, se agrega al combo
        if plataforma_fin in plataformas_seleccionadas:
            combo.append(plataforma_fin)

        # Calcular el costo total sumando los valores de las plataformas en el combo
        try:
            costo_total = sum(costos[p] for p in combo if p in costos)
        except KeyError as e:
            print(f"Error: La plataforma {e} no tiene un costo definido.")
            costo_total = 0

        # Redondear el costo total
        costo_total = round(costo_total)

        # Formatear el nombre y descripción del combo
        nombre_combo = f"{nombre_base} #{i}"
        descripcion = " + ".join(combo)

        # Agregar el combo generado a la lista
        combos.append((nombre_combo, descripcion, costo_total))

    return combos

# ----------------------------- DICCIONARIO DE PLATAFORMAS -----------------------------

# Diccionario con las plataformas disponibles y sus costos
plataformas_disponibles = {
    "Netflix": 8000, "Prime Video": 1000, "Max": 1600, "Disney Basico": 1143, "Disney Promocion": 1286, "Disney Premium": 6200,
    "Vix Plus": 500, "CrunchyRoll": 500, "Paramount Plus": 250, "TvMia": 750, "YouTube Premium": 2500, "Canva Pro": 1000,
    "Universal Plus": 600, "Mubi Plus": 400, "Spotify Premium": 4500, "Tidal Plus": 1500, "Calm Plus": 1000, "Viky Rakuten": 300,
    "Microsoft 365": 1600, "Apple TV": 3333, "Apple Music": 6000, "Atres Players": 667, "Iptv Premium": 500, "Next Movie": 500,
    "XXX": 500, "Duolingo Plus": 450, "Obsequios": 1000, "Obsequio Netflix": 8000, "Obsequio YouTube": 2500, "Obsequio Spotify": 4500
}

# ----------------------------- RUTAS DE LA APLICACIÓN -----------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Ruta principal que maneja la generación de combos.

    - Si la solicitud es POST, se generan nuevos combos basados en la selección del usuario.
    - Si la solicitud es GET, simplemente se renderiza la página con una lista vacía de combos.
    """
    combos = None
    if request.method == 'POST':
        # Obtener los datos del formulario
        total_combos = int(request.form['total_combos'])
        nombre_base = request.form['nombre_base']
        plataforma_inicio = request.form.get('plataforma_inicio', '')
        plataforma_fin = request.form['plataforma_fin']
        plataformas_seleccionadas = request.form.getlist('plataformas')

        # Generar los combos
        combos_generados = generar_combos(total_combos, plataformas_seleccionadas, nombre_base, plataforma_inicio, plataforma_fin, costos=plataformas_disponibles)

        # Guardar los combos generados en la sesión
        session['combos'] = combos_generados

        return render_template('index.html', plataformas=plataformas_disponibles.keys(), combos=combos_generados)
    
    if combos is None:
        combos = []

    # Si es una solicitud GET, limpiar la sesión para borrar los combos anteriores
    session.pop('combos', None)

    return render_template('index.html', plataformas=plataformas_disponibles.keys(), combos=combos)

@app.route('/export_to_excel', methods=['POST'])
def export_to_excel():
    """
    Ruta para exportar los combos generados a un archivo Excel.
    """
    data = request.get_json()
    combos = data['combos']  # Obtener los combos desde la solicitud

    # Crear un DataFrame con los combos
    df = pd.DataFrame(combos, columns=['Nombre del Combo', 'Descripción', 'Costo'])
    
    # Guardar el archivo en la ruta actual
    file_path = os.path.join(os.getcwd(), 'combos.xlsx')
    df.to_excel(file_path, index=False)

    # Enviar el archivo al usuario para su descarga
    return send_file(file_path, as_attachment=True)

@app.route('/reset', methods=['POST'])
def reset():
    """
    Ruta que borra los combos almacenados en la sesión y redirige a la página principal.
    """
    session.pop('combos', None)  # Eliminar los combos de la sesión
    return redirect(url_for('index'))  # Redirigir a la página principal

# ----------------------------- EJECUCIÓN DE LA APLICACIÓN -----------------------------

if __name__ == '__main__':
    app.run(debug=True)
