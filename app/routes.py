from flask import Blueprint, render_template, request, session, redirect, url_for
from .controllers import generar_combos, export_to_excel
from .models import plataformas_disponibles

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    combos = []
    if request.method == 'POST':
        try:
            total_combos = int(request.form['total_combos'])
            nombre_base = request.form['nombre_base']
            plataforma_inicio = request.form.get('plataforma_inicio', '')
            plataforma_fin = request.form['plataforma_fin']
            plataformas_seleccionadas = request.form.getlist('plataformas')

            combos = generar_combos(
                total_combos, plataformas_seleccionadas, nombre_base, plataforma_inicio, plataforma_fin, costos=plataformas_disponibles
            )
            session['combos'] = combos
        except Exception as e:
            print(f"Error al procesar el formulario: {e}")

    session.pop('combos', None)
    return render_template('index.html', plataformas=plataformas_disponibles.keys(), combos=combos)

@main_blueprint.route('/export_to_excel', methods=['POST'])
def export_to_excel_route():
    return export_to_excel()

@main_blueprint.route('/reset', methods=['POST'])
def reset():
    session.pop('combos', None)
    return redirect(url_for('main.index'))
