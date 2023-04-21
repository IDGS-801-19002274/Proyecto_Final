from flask import Blueprint, render_template

Tienda = Blueprint('Tienda', __name__)

#-------------------------------------------------RUTAS---------------------------------------------------------#

@Tienda.route('/Tienda/index', methods=['GET'])
def index():
    return render_template('index.html', name = 'Inicio', type = 'header')

@Tienda.route('/Tienda/nosotros', methods=['GET'])
def nosotros():
    return render_template('nosotros.html', name = 'Nosotros', type = 'header')

@Tienda.route('/Tienda/contacto', methods=['GET'])
def contacto():
    return render_template('contacto.html', name = 'Contacto', type = 'header')

@Tienda.route('/Tienda/productos', methods=['GET'])
def products():
    products = Producto.query.all()
    return render_template('productos.html', name = 'Productos', type = 'header', products = products)

@Tienda.route('/TiendaProducto/<int:id>', methods=['GET'])
def product(id):
    products = Producto.query.get(id)
    suggest = productos_aleatorios = random.sample(Producto.query.all(), 4)
    return render_template('producto.html', name = 'Productos', type = 'header', product = products, suggest = suggest)
