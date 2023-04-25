from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import User, Role, user_roles, db, Log
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from my_decorator import logout_required

Usuario = Blueprint('Usuario', __name__)

#----------------------RUTAS-------------------------------------------------------------------------------------------------------------------------------------#

#LOGIN
@Usuario.route('/Usuario/login', methods=['GET'])
@logout_required
def show_login():
    return render_template('login.html', name = 'Login', type = 'no-header')

@Usuario.route('/Usuario/login', methods=['POST'])
@logout_required
def login():
    email = request.form.get('email')
    passw = request.form.get('password')
    remember = True if request.form.get('remember_me') else False
    
    #Consultamos si existe un usuario ya registrado con el email.
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, passw):
        flash('El usuario y/o el password son incorrectos')
        return redirect(url_for('Usuario.show_login'))
    
    #Si llegamos aqui, el usuario tiene datos correctos 
    #creamos una session y logueamos al usuario.
    login_user(user, remember=remember)
    ahora = datetime.now()
    fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
    log = Log(
        log = (current_user.name + ' ha iniciado sesión ' + ' - ' + fecha_hora),
        usuario_id = current_user.id
    )

    db.session.add(log)
    db.session.commit()
    return redirect(url_for('Tienda.index'))


#REGISTER
@Usuario.route('/Usuario/register', methods=['GET'])
@logout_required
def show_register():
    return render_template('register.html', name = 'Login', type = 'no-header')

@Usuario.route('/Usuario/register', methods=['POST'])
@logout_required
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    passw = request.form.get('password')
    tel = request.form.get('telefono')
    dire = request.form.get('direccion')
    cp = request.form.get('cp')
    
    try:
        #Consultamos si existe un usuario ya registrado con ese email
        user = User.query.filter_by(email=email).first()

        if user: #Si se encontro un usuario, redireccionamos de regreso a la pagina de registro
            flash('Ese correo electronico ya existe')
            return redirect(url_for('Usuario.show_register'))

        #Si no existe, creamos un nuevo usuario con sus datos.
        #Hacemos un hash a la contraseña para protegerla.
        new_user = User(
            name = name,
            email = email,
            password = generate_password_hash(passw, method='sha256'),
            direccion = dire,
            telefono = tel,
            cp = cp)

        client_role = Role.query.filter_by(name='cliente').first()
        new_user.roles.append(client_role)

        db.session.add(new_user)
        
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (new_user.name + ' se ha registrado ' + ' - ' + fecha_hora),
            usuario_id = -1
        )
        
        db.session.add(log)
        
        db.session.commit()
        
        return redirect(url_for('Usuario.show_login'))
    
    except:
        flash('Hubo un error al crear el usuario. Inténtalo de nuevo más tarde.')
        return redirect(url_for('Usuario.show_register'))

#LOGOUT
@Usuario.route('/Usuario/logout', methods=['GET'])
@login_required
def logout():
    ahora = datetime.now()
    fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
    log = Log(
        log = (current_user.name + ' ha cerrado sesión ' + ' - ' + fecha_hora),
        usuario_id = current_user.id
    )
    db.session.add(log)
    logout_user()
    db.session.commit()
    return redirect(url_for('Usuario.show_login'))

#ADMIN_VIEW-------------------------------------------------------------------
#Obtiene todos los usuarios
@Usuario.route('/Admin/usuarios', methods=['GET'])
@login_required
def show_usuarios():
    users = User.query.all()
    roles = Role.query.all()
    return render_template('usuarios.html', name = 'Usuarios', type = 'lateral', users = users, roles = roles, delete_route = '/DeleteUser/')

#Modifica el rango de un usuario
@Usuario.route('/Admin/usuarios_update', methods=['POST'])
@login_required
def range_usuarios():
    user = User.query.get(int(request.form.get('usuario_id')))
    role = int(request.form.get('rango'))
    new_role = Role.query.get(role)
    
    #Comprueba que no sea el mismo rol, sino, lo modifica
    if new_role != user.roles[0]:
        user.roles.remove(user.roles[0])
        user.roles.append(new_role)
        
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha modificado el rango de: ' + user.name + ', ahora es ' + new_role.name + ' - ' + fecha_hora),
            usuario_id = current_user.id
        )
        
        db.session.add(log)
        
        db.session.commit()
    else:
        flash('No se han realizado cambios')
    
    return redirect(url_for('Usuario.show_usuarios'))

#Elimina usuarios
@Usuario.route('/DeleteUser/<int:id>', methods=['POST'])
@login_required
def deleteuser(id):
    user = User.query.get(id)
    ahora = datetime.now()
    fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
    log = Log(
        log = (current_user.name + ' ha eliminado a ' + user.name + ' - ' + fecha_hora),
        usuario_id = current_user.id
    )
    db.session.delete(user)
    db.session.add(log)
    
    db.session.commit()
    flash('El usuario ha sido eliminado correctamente')
    return redirect(url_for('Usuario.show_usuarios'))
    

    
    
