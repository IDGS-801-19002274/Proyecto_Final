from flask import Blueprint, render_template, request, current_app as app, redirect, url_for
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from my_decorator import role_required
from models import db, Proveedor, Pedido, Ingrediente
import os

Administrador = Blueprint('Administrador', __name__)

#----------------------RUTAS-------------------------------------------------------------------------------------------------------------------------------------#

@Administrador.route('/Admin/perfil', methods=['GET'])
@login_required
@role_required('admin', 'mod')
def get_profile_data():
    return render_template('admin-profile.html', name = 'Perfil', type = 'lateral')

#PROVEEDORES-----------------------------------------------------------------------


#PEDIDOS
@Administrador.route('/Admin/pedidos', methods=['GET'])
@login_required
def get_orders():
    return render_template('orders.html', name = 'Pedidos', type = 'lateral')

#LOG
@Administrador.route('/Admin/log', methods=['GET'])
@login_required
@role_required('admin')
def get_logs():
    return render_template('logs.html', name = 'Log', type = 'lateral')