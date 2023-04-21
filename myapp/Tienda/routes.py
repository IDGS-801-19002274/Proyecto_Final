from flask import Blueprint, render_template

Tienda = Blueprint('Tienda', __name__)

#----------------------RUTAS-------------------------------------------------------------------------------------------------------------------------------------#

@Tienda.route('/Tienda/index', methods=['GET'])
def index():
    return render_template('index.html', name = 'Inicio', type = 'header')
