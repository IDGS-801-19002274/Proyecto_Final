from flask import Blueprint, render_template, request, current_app as app, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from my_decorator import role_required
from models import db, Proveedor, Pedido, Ingrediente, User
import os
from Productos.converter import convert_Pedido

Administrador = Blueprint('Administrador', __name__)

#----------------------RUTAS-------------------------------------------------------------------------------------------------------------------------------------#

@Administrador.route('/Admin/perfil', methods=['GET'])
@login_required
@role_required('admin', 'visor')
def get_profile_data():
    return render_template('admin-profile.html', name = 'Perfil', type = 'lateral')

#PROVEEDORES-----------------------------------------------------------------------
#Obtiene todos los proveedores
@Administrador.route('/Admin/proveedores', methods=['GET'])
@login_required
@role_required('admin')
def get_providers():
    providers = Proveedor.query.all()
    return render_template('providers.html', name = 'Proveedores', type = 'lateral', providers = providers)

#Obtiene y muestra un solo proveedor
@Administrador.route('/Proveedor/<int:id>', methods=['GET'])
@login_required
@role_required('admin')
def get_provider(id):
    provider = Proveedor.query.filter_by(id=id).first()
    ingredients = Ingrediente.query.filter_by(proveedor_id=provider.id)
    return render_template('provider_data.html', name = 'Proveedor', type = 'lateral', provider = provider, ingredients = ingredients)

#Muestra la vista de agregar un proveedor
@Administrador.route('/Admin/add_proveedor', methods=['GET'])
@login_required
@role_required('admin')
def show_add_provider():
    return render_template('new_proveedor.html', name = 'Agregar Proveedor', type = 'lateral')

#Agrega al proveedor
@Administrador.route('/Admin/add_proveedor', methods=['POST'])
@login_required
@role_required('admin')
def add_provider():
    try:
        nombre = request.form.get('nombre')
        des = request.form.get('descripcion')
        dire = request.form.get('direccion')
        tel = request.form.get('telefono')
        jefe = request.form.get('jefe')
        file = request.files['file']

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        prov = Proveedor(
            nombre = nombre,
            url_photo = ('../static/img/upload/' + filename),
            descripcion = des,
            direccion = dire,
            telefono = tel,
            jefe = jefe
        )

        db.session.add(prov)
        db.session.commit()

        return redirect(url_for('Administrador.get_providers'))

    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al agregar el proveedor. Verifique que haya ingresado todos los campos correctamente.')
        return redirect(url_for('Administrador.get_providers'))

#PEDIDOS
#Muestra todos los pedidos
@Administrador.route('/Admin/pedidos', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'visor')
def get_orders():
    status = ''
    if request.method == 'POST':
        status = request.form.get('status')
    
    if status != '':
        ped = Pedido.query.filter_by(status = status).all()
    else:
        ped =Pedido.query.order_by(
            (Pedido.status == 'pendiente').desc(),
            (Pedido.status == 'enviado').desc(),
            (Pedido.status == 'entregado').desc(),
            (Pedido.status == 'cancelado').desc(),
            Pedido.id.desc()
        ).all()
    
    pedidos = []
    
    for p in ped:
        pedidos.append({
            'pedido' : p,
            'cliente' : User.query.get(p.cliente_id)
        })
    return render_template('orders.html', name = 'Pedidos', type = 'lateral', pedidos = pedidos)

#Muestra un pedido en especifico
@Administrador.route('/Pedido/<int:id>', methods=['GET'])
@login_required
@role_required('admin', 'visor')
def get_order(id):
    ped = Pedido.query.get(id)
    cliente = User.query.get(ped.cliente_id)
    productos = convert_Pedido(ped.productos)
    return render_template('order.html', name = 'Pedidos', type = 'lateral', pedido = ped, cliente = cliente, productos = productos['productos'], total = productos['total'])

#Cambia el status de un pedido
@Administrador.route('/Pedido/editar', methods=['POST'])
@login_required
@role_required('admin', 'visor')
def cambiar_status_pedido():
    try:
        pedido = Pedido.query.get(int(request.form.get('id')))
        if pedido.status == request.form.get('status'):
            flash('No se realizaron cambios')
        else:
            new_status = request.form.get('status')
            pedido.status = new_status
            
            if new_status == 'entregado':
                objeto = convert_Pedido(pedido.productos)
                
                for producto in objeto['productos']:
                    prod = producto['producto']
                    if (prod.inventario[0].stock - int(producto['cantidad']))< 0:
                        flash('No hay suficiente stock para este pedido')
                        return redirect(url_for('Administrador.get_orders'))
                    else:
                        prod.inventario[0].stock -= int(producto['cantidad'])
            db.session.commit()
            flash('Se ha actualizado el pedido')
    except:
        flash('Algo salió mal')
    return redirect(url_for('Administrador.get_orders'))

#LOG
@Administrador.route('/Admin/log', methods=['GET'])
@login_required
@role_required('admin')
def get_logs():
    return render_template('logs.html', name = 'Log', type = 'lateral')