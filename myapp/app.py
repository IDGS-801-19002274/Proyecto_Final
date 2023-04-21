from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

from config import config
from models import db, User

import os, random

from Administrador.routes import Administrador
from Productos.routes import Productos
from Tienda.routes import Tienda
from Usuario.routes import Usuario

app = Flask(__name__)
login_manager = LoginManager(app)
app.config.from_object(config['development'])
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/img/upload')

#----------------------RUTAS-------------------------------------------------------------------------------------------------------------------------------------#

@app.route('/', methods=['GET'])
def home():
    return  redirect(url_for('Tienda.index'))

@app.errorhandler(404)
def page_not_found(error):
    flash("Lo siento, el sitio solicitado no existe. [404]")
    return redirect('/')

@app.context_processor
def my_variables():
    img_logo = '../static/img/Logo.png'
    img_logo2 = '../static/img/logo_recortado.png'
    img_logo3 = '../static/img/logo_recortado2.png'
    def_img = '../static/img/default_image.jpg'
    rand = random.randint(2, 7)
    return dict(logo_white = img_logo, logo = img_logo2, logo2 = img_logo3, def_img = def_img, rand = rand)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(Administrador)
app.register_blueprint(Productos)
app.register_blueprint(Tienda)
app.register_blueprint(Usuario)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

if __name__ =='__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    login_manager.login_view = 'Usuario.show_login'
    login_manager.login_message = "Por favor inicie sesión para acceder a esta página"
    app.run()