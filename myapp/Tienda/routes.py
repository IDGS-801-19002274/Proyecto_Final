from flask import Blueprint, render_template
from models import db, Producto
import random
from my_decorator import role_required
from flask_login import login_required

Tienda = Blueprint('Tienda', __name__)

#-------------------------------------------------RUTAS---------------------------------------------------------#

@Tienda.route('/Tienda/index', methods=['GET'])
def index():
    return render_template('index.html', name = 'Inicio', type = 'header')

@Tienda.route('/Tienda/nosotros', methods=['GET'])
def nosotros():
    return render_template('nosotros.html', name = 'Nosotros', type = 'header')

@Tienda.route('/Tienda/carrito', methods=['GET'])
def carrito():
    return render_template('carrito.html', name = 'Carrito', type = 'header')

@Tienda.route('/Tienda/contacto', methods=['GET'])
@login_required
@role_required('admin', 'visor')
def contacto():
    return render_template('contacto.html', name = 'Contacto', type = 'header')

@Tienda.route('/Tienda/productos', methods=['GET'])
def products():
    products = Producto.query.all()
    return render_template('productos.html', name = 'Productos', type = 'header', products = products)

@Tienda.route('/TiendaProducto/<int:id>', methods=['GET'])
def product(id):
    products = Producto.query.get(id)
    suggest = random.sample(Producto.query.all(), 4)
    return render_template('producto.html', name = 'Productos', type = 'header', product = products, suggest = suggest)
