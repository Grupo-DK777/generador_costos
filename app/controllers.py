import random
import pandas as pd
import os
import json
from flask import request, jsonify, send_file
from .models import plataformas_disponibles

# Archivo para persistir las combinaciones generadas
COMBOS_FILE = 'combos.json'

# Cargar combinaciones existentes desde el archivo
def load_combos():
    if os.path.exists(COMBOS_FILE):
        with open(COMBOS_FILE, 'r') as file:
            return set(json.load(file))
    return set()

# Guardar combinaciones en el archivo
def save_combos(combos):
    with open(COMBOS_FILE, 'w') as file:
        json.dump(list(combos), file)

# Conjunto para almacenar combinaciones únicas
unique_combos = load_combos()

def generar_combos(cantidad, plataformas_seleccionadas, nombre_base, plataforma_inicio, plataforma_fin, costos=None):
    if costos is None:
        costos = {}

    combos = []
    try:
        num_plataformas = int(''.join(filter(str.isdigit, nombre_base)))
    except ValueError:
        num_plataformas = 3

    num_plataformas = max(1, min(num_plataformas, len(plataformas_seleccionadas) - 1))

    for i in range(1, cantidad + 1):
        combo = []
        if plataforma_inicio and plataforma_inicio in plataformas_seleccionadas:
            combo.append(plataforma_inicio)

        seleccionables = [p for p in plataformas_seleccionadas if p not in combo and p != plataforma_fin]
        seleccionadas = random.sample(seleccionables, k=min(len(seleccionables), num_plataformas - len(combo)))
        combo.extend(seleccionadas)

        while len(combo) < num_plataformas:
            faltantes = [p for p in seleccionables if p not in combo]
            if not faltantes:
                break
            combo.append(random.choice(faltantes))

        if plataforma_fin in plataformas_seleccionadas:
            combo.append(plataforma_fin)

        try:
            costo_total = sum(costos[p] for p in combo if p in costos)
        except KeyError as e:
            print(f"Error: La plataforma {e} no tiene un costo definido.")
            costo_total = 0

        costo_total = round(costo_total)
        nombre_combo = f"{nombre_base} #{i}"
        descripcion = " + ".join(combo)

        # Asegurar que la combinación sea única
        combo_tuple = (nombre_combo, descripcion, costo_total)
        if combo_tuple not in unique_combos:
            unique_combos.add(combo_tuple)
            combos.append(combo_tuple)

    # Guardar las combinaciones únicas en el archivo
    save_combos(unique_combos)

    return combos

def export_to_excel():
    data = request.get_json()
    combos = data['combos']

    df = pd.DataFrame(combos, columns=['Nombre del Combo', 'Descripción', 'Costo'])
    file_path = os.path.join(os.getcwd(), 'combos.xlsx')
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)
