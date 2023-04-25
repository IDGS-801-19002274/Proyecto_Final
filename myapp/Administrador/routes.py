from flask import Blueprint, render_template, request, current_app as app, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from my_decorator import role_required
from models import db, Proveedor, Pedido, Ingrediente, User, ComentariosCancelados, Log
import os
from Productos.converter import convert_Pedido
from datetime import datetime

Administrador = Blueprint('Administrador', __name__)

#----------------------RUTAS-------------------------------------------------------------------------------------------------------------------------------------#

@Administrador.route('/Admin/perfil', methods=['GET'])
@login_required
@role_required('admin', 'visor')
def get_profile_data():
    logs = Log.query.filter_by(usuario_id=current_user.id).order_by(Log.id.desc()).all()
    return render_template('admin-profile.html', name = 'Perfil', type = 'lateral', logs = logs)

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
        
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha agregado al proveedor ' + prov.nombre + ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)
        db.session.add(prov)
        db.session.commit()

        return redirect(url_for('Administrador.get_providers'))

    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al agregar el proveedor. Verifique que haya ingresado todos los campos correctamente.')
        return redirect(url_for('Administrador.get_providers'))


#Vista para editar al proveedor
@Administrador.route('/EditProveedor/<int:id>', methods=['GET'])
@login_required
@role_required('admin')
def showEditProveedor(id):
    proveedor = Proveedor.query.get(id)
    return render_template('edit_proveedor.html', name = proveedor.nombre, type = 'lateral', proveedor = proveedor, delete_route = ('/DeleteProveedor/'+str(id)))

#Edita al proveedor
@Administrador.route('/EditProveedor/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def EditProveedor(id):
    try:
        proveedor = Proveedor.query.get(id)
        proveedor.nombre = request.form.get('nombre')
        proveedor.descripcion = request.form.get('descripcion')
        proveedor.direccion = request.form.get('direccion')
        proveedor.telefono = request.form.get('telefono')
        proveedor.jefe = request.form.get('dueno')
        
        if request.files.get('imagen'):
            file = request.files['imagen']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            proveedor.url_photo = ('../static/img/upload/' + filename)
        
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' editó al proveedor ' + proveedor.nombre + ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)
        
        db.session.commit()
        flash('Se han guardado con exito los cambios')
    except:
        flash('Ha ocurrido un error')
    return redirect(url_for('Administrador.get_providers'))

#Elimina al proveedor
@Administrador.route('/DeleteProveedor/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def DeleteProveedor(id):
    prov = Proveedor.query.get(id)
    
    ahora = datetime.now()
    fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
    log = Log(
        log = (current_user.name + ' ha eliminado al proveedor ' + prov.nombre + ' - ' + fecha_hora),
        usuario_id = current_user.id
    )

    db.session.add(log)
    
    db.session.delete(prov)
    db.session.commit()
    flash('Proveedor eliminado con exito')
    
    return redirect(url_for('Administrador.get_providers'))
    

#PEDIDOS----------------------------------------------------------------------------
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
    cancelled = False
    ped = Pedido.query.get(id)
    cliente = User.query.get(ped.cliente_id)
    productos = convert_Pedido(ped.productos)
    true_Productos = []
    
    for producto in productos['productos']:
        if producto['erroa'] == 'ERROR':
            flash('El siguiente pedido contiene productos eliminados que se han retirado de la lista')
            cancelled = True
        else:
            true_Productos.append(producto)
    
    if not cliente:
        flash('El Cliente que ha solicitado el pedido, ya no existe')
        cancelled = True
    
    comentarios = ComentariosCancelados.query.filter_by(id_pedido=id).order_by(ComentariosCancelados.id.desc()).all()
    
    return render_template('order.html', name = 'Pedidos', type = 'lateral', pedido = ped, cliente = cliente, productos = true_Productos, total = productos['total'], cancelled = cancelled, comentarios = comentarios)

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
            
            ahora = datetime.now()
            fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
            log = Log(
                log = (current_user.name + ' ha actualizado el pedido ' + str(pedido.id) + ', se le ha dado el estado de' + pedido.status + ' - ' + fecha_hora),
                usuario_id = current_user.id
            )

            db.session.add(log)
            
            db.session.commit()
            flash('Se ha actualizado el pedido')
    except:
        flash('Algo salió mal')
    return redirect(url_for('Administrador.get_orders'))

#Agrega un comentario a un pedido
@Administrador.route('/add_comentario/<int:id>', methods=['POST'])
@login_required
@role_required('admin', 'visor')
def add_comentario(id):
    coemnt = request.form.get('comentario')
    
    if coemnt == '':
        flash ('No se pueden agregar comentarios vacíos')
    else:
        comentario = ComentariosCancelados(id_pedido = id, comentario = coemnt)
        pedido = Pedido.query.get(id)
        comentario.pedido = pedido
        
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha agregado el comentario: ' + comentario.comentario + ' en el producto #' + str(pedido.id) + ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)
        
        db.session.add(comentario)
        db.session.commit()
    
    return redirect(url_for('Administrador.get_orders'))


#LOG
@Administrador.route('/Admin/log', methods=['GET'])
@login_required
@role_required('admin')
def get_logs():
    logs = Log.query.order_by(Log.id.desc()).all()
    return render_template('logs.html', name = 'Log', type = 'lateral', logs = logs)