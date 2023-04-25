from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import db, Producto, Pedido, ComentariosCancelados, Log
import random, json
from my_decorator import role_required
from flask_login import login_required, current_user
from Productos.converter import convert_carrito_Inputs
from datetime import datetime
from Productos.converter import convert_Pedido

Tienda = Blueprint('Tienda', __name__)

#-------------------------------------------------RUTAS---------------------------------------------------------#

#muestra el index
@Tienda.route('/Tienda/index', methods=['GET'])
def index():
    return render_template('index.html', name = 'Inicio', type = 'header')

#Muestra la pagina de nosotros
@Tienda.route('/Tienda/nosotros', methods=['GET'])
def nosotros():
    return render_template('nosotros.html', name = 'Nosotros', type = 'header')

#Muestra la pagina de contacto
@Tienda.route('/Tienda/contacto', methods=['GET'])
@login_required
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

#Muestra el carrito de compra
@Tienda.route('/Tienda/carrito', methods=['GET'])
@login_required
def carrito():
    items = json.loads(request.args.get('cartItems', '{}'))
    cartItems = []
    total = 0
    
    if items:
        for item in items:
            prod = Producto.query.get(item['product_id'])
            cartItems.append({
                'product' : prod,
                'quantity' : item['quantity']
            })
            
            total += prod.precio_menudeo * item['quantity']
    
    return render_template('carrito.html', name='Carrito', type='header', cartItems = cartItems, total = total)

#Realiza el pago y guarda el pedido
@Tienda.route('/pago', methods=['POST'])
@login_required
def pago():
    try:
        new_pedido = Pedido(
        productos = convert_carrito_Inputs(request.form),
        cliente_id = current_user.id,
        status = 'pendiente'
        )
    
        db.session.add(new_pedido)
        
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha dado de alta un pedido' + ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)
        
        db.session.commit()
        
        return redirect(url_for('Tienda.borrarLS'))
    except:
        flash('Ha ocurrido un error al realizar el pedido')
    return redirect(url_for('Tienda.index'))

@Tienda.route('/pago/deleteLS', methods=['GET'])
@login_required
def borrarLS():
    return render_template('deletels.html',)

@Tienda.route('/agregar_carrito', methods=['GET'])
@login_required
def add_carrito():
    flash ('Se ha agregado correctamente el producto a su carrito :)')
    return redirect(url_for('Tienda.products'))

@Tienda.route('/mis_pedidos', methods=['GET'])
@login_required
def show_mispedidos():
    ped = Pedido.query.filter(Pedido.cliente_id == current_user.id).order_by(
            (Pedido.status == 'pendiente').desc(),
            (Pedido.status == 'enviado').desc(),
            (Pedido.status == 'entregado').desc(),
            (Pedido.status == 'cancelado').desc(),
            Pedido.id.desc()
        ).all()
    return render_template('mispedidos.html', name='Mis pedidos', type='header', pedidos = ped)

@Tienda.route('/mi_pedido/<int:id>', methods=['GET'])
@login_required
def show_mipedido(id):
    ped = Pedido.query.get(id)
    productos = convert_Pedido(ped.productos)
    true_Productos = []
    
    for producto in productos['productos']:
        if producto['erroa'] == 'ERROR':
            flash('El siguiente pedido contiene productos eliminados que se han retirado de la lista')
        else:
            true_Productos.append(producto)
    
    comentarios = ComentariosCancelados.query.filter_by(id_pedido=id).order_by(ComentariosCancelados.id.desc()).all()
    
    return render_template('mipedido.html', name='Mis pedidos', type='header', pedido = ped, productos = true_Productos, total = productos['total'], comentarios = comentarios)