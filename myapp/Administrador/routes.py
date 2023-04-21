from flask import Blueprint, render_template, request, current_app as app, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from my_decorator import role_required
from models import db, Proveedor, Pedido, Ingrediente
import os

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
@Administrador.route('/Admin/pedidos', methods=['GET'])
@login_required
@role_required('admin', 'visor')
def get_orders():
    return render_template('orders.html', name = 'Pedidos', type = 'lateral')

#Muestra un pedido en especifico
@Administrador.route('/Pedido/<int:id>', methods=['GET'])
@login_required
@role_required('admin', 'visor')
def get_order(id):
    
    return render_template('order.html', name = 'Pedidos', type = 'lateral')

#LOG
@Administrador.route('/Admin/log', methods=['GET'])
@login_required
@role_required('admin')
def get_logs():
    return render_template('logs.html', name = 'Log', type = 'lateral')