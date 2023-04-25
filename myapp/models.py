from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User account model."""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(100), nullable=False)
    cp = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean)
    roles = db.relationship('Role', secondary=user_roles, backref='user')
    create_date = db.Column(db.DateTime, default = datetime.datetime.now)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion_corta = db.Column(db.String(200), nullable=False)
    descripcion_larga = db.Column(db.Text, nullable=False)
    precio_menudeo = db.Column(db.Double, nullable=False)
    precio_mayoreo = db.Column(db.Double, nullable=False)
    url_photo = db.Column(db.String(255), nullable=False)
    receta = db.Column(db.Text, nullable=False)
    create_date = db.Column(db.DateTime, default = datetime.datetime.now)

class Ingrediente(db.Model):
    __tablename__ = 'ingredientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    proveedor_id = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Double, nullable=False)
    gramaje_id = db.Column(db.Integer, db.ForeignKey('gramaje.id'))
    gramaje = relationship('Gramaje', backref='ingredientes')
    create_date = db.Column(db.DateTime, default = datetime.datetime.now)

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    url_photo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(100), nullable=False)
    jefe = db.Column(db.String(100), nullable=False)
    create_date = db.Column(db.DateTime, default = datetime.datetime.now)

class Role(db.Model):
  __tablename__ = 'roles'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
    
class Pedido(db.Model):
  __tablename__ = 'pedidos'
  id = db.Column(db.Integer, primary_key=True)
  productos = db.Column(db.Text, nullable=False)    
  cliente_id = db.Column(db.Integer, nullable=False)
  status = db.Column(db.String(50), nullable=False)

class Facturas(db.Model):
  __tablename__ = 'facturas'
  id = db.Column(db.Integer, primary_key=True)
  pedido_id = db.Column(db.Integer, nullable=False)
  
class Log(db.Model):
  __tablename__ = 'log'
  id = db.Column(db.Integer, primary_key=True)  
  log = db.Column(db.Text, nullable=False)    
  usuario_id = db.Column(db.Integer, nullable=False)

class Gramaje(db.Model):
  __tablename__ = 'gramaje'
  id = db.Column(db.Integer, primary_key=True)  
  uni_mini = db.Column(db.String(100), nullable=False)
  uni_larga = db.Column(db.String(100), nullable=False)
  
class InventarioIngredientes(db.Model):
    __tablename__ = 'inventario_ingredientes'
    ingrediente_id = db.Column(db.Integer, ForeignKey('ingredientes.id'), primary_key=True)
    stock = db.Column(db.Double)
    ingrediente = relationship('Ingrediente', uselist=False, backref='inventario')

class InventarioProductos(db.Model):
    __tablename__ = 'inventario_productos'
    producto_id = db.Column(db.Integer, ForeignKey('productos.id'), primary_key=True)
    stock = db.Column(db.Double)
    producto = relationship('Producto', uselist=False, backref='inventario')

class ComentariosCancelados(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=False)