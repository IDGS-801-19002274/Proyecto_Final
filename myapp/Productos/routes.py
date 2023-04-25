from flask import Blueprint, render_template, request, current_app as app, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from Productos.converter import convert_Inputs, convert_Objects
import os, json
from models import db, Producto, Proveedor, Ingrediente, InventarioIngredientes, InventarioProductos, Gramaje, Log
from datetime import datetime
from my_decorator import role_required

Productos = Blueprint('Productos', __name__)

#----------------------RUTAS-------------------------------------------------------------------------------------------------------------------------------------#

#PRODUCTOS-------------------------------------------------------
#Obtiene y muestra los productos
@Productos.route('/Admin/productos', methods=['GET'])
@login_required
@role_required('admin', 'visor')
def get_Productos():
    producst = Producto.query.all()
    return render_template('products.html', name = 'Productos', type = 'lateral', products = producst)

#Obtiene y muestra un solo producto
@Productos.route('/Producto/<int:id>', methods=['GET'])
@login_required
@role_required('admin', 'visor')
def get_Producto(id):
    error = False
    product = Producto.query.filter_by(id=id).first()
    receta = convert_Objects(product.receta)
    jreceta = json.dumps(receta)
    ingredientes = Ingrediente.query.all()
    
    for r in receta:
        if r['id'] == 'ERROR':
            error = True
    
    if error:
        flash('Algunos ingredientes han sido eliminados, se recomienda revisar la receta y corregir')
    return render_template('product_data.html', name = 'Producto', type = 'lateral', product = product, receta = receta, jreceta = jreceta, ingredientes = ingredientes, ing = len(receta), delete_route = ('/DeleteProducto/' + str(product.id)))

#Vista que permite agregar productos
@Productos.route('/Admin/add_productos', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def show_new_Producto():
    ingredientes = 0
    ingredients = []
    if request.method == 'POST':
        ingredientes = int(request.form.get('ingre'))
        ingredients = Ingrediente.query.all()
    return render_template('new_product.html', name = 'Agregar Producto', type = 'lateral', ing = ingredientes, ingredients = ingredients)

#Agrega productos
@Productos.route('/Admin/add_producto', methods=['POST'])
@login_required
@role_required('admin')
def add_producto():
    try:
        nombre = request.form.get('name')
        descripcion_corta = request.form.get('descripcion_corta')
        descripcion_larga = request.form.get('descripcion_larga')
        precio_menudeo = request.form.get('precio_menudeo')
        precio_mayoreo = request.form.get('precio_mayoreo')
        file = request.files['file']
        receta = convert_Inputs(request.form)

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        prod = Producto(
            nombre=nombre,
            descripcion_corta=descripcion_corta,
            descripcion_larga=descripcion_larga,
            precio_menudeo=precio_menudeo,
            precio_mayoreo=precio_mayoreo,
            url_photo=('../static/img/upload/' + filename),
            receta=receta
        )

        inventario = InventarioProductos(stock=0.0, producto=prod)
        prod.inventario = [inventario]

        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha agregado el producto: ' + prod.nombre +  ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)

        db.session.add(prod)
        db.session.commit()

        return redirect(url_for('Productos.get_Productos'))
    except Exception as e:
        db.session.rollback()
        flash('Hubo un error al agregar el producto: verifique que los datos que ingresó son correctos o que no dejó ningún campo vacío')
        return redirect(url_for('Productos.get_Productos'))
   
#Edita info general de productos
@Productos.route('/Editproduct/<int:id>', methods=['POST'])
@login_required
@role_required('admin', 'visor')
def edit_product(id):
    try:
        producto = Producto.query.get(id)
    
        producto.descripcion_corta = request.form.get('descripcion_corta')
        producto.descripcion_larga = request.form.get('descripcion_larga')
        producto.nombre = request.form.get('name')
        producto.precio_menudeo = request.form.get('precio_menudeo')
        
        if request.files['file'].filename:
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            producto.url_photo = ('../static/img/upload/' + filename)
        
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha editado la información del producto: ' + producto.nombre +  ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)
        
        db.session.commit()
        flash('Se han guardado con éxito los cambios!')
        
    except TypeError:
        flash('Se ha producido un error')
    return redirect(url_for('Productos.get_Productos'))
    
#Edita la receta
@Productos.route('/Editrecipe/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_recipe(id):
    producto = Producto.query.get(id)
    new_receta = convert_Inputs(request.form)
    if producto.receta == new_receta:
        flash ('No se han ralizado cambios en la receta')
    else:
        try:
            producto.receta = new_receta
            
            ahora = datetime.now()
            fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
            log = Log(
                log = (current_user.name + ' ha editado la receta del producto: ' + producto.nombre +  ' - ' + fecha_hora),
                usuario_id = current_user.id
            )

            db.session.add(log)
            
            db.session.commit()
            flash ('La receta ha sido cambiada con exito')
        except:
            flash('Ha ocurrido un error')
        
    return redirect(url_for('Productos.get_Productos'))

#Elimina productos
@Productos.route('/DeleteProducto/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def deleteProducto(id):
    try:
        producto = Producto.query.get(id)

        # Eliminar primero de la tabla inventario_ingredientes
        inventario = InventarioProductos.query.filter_by(producto_id=id).first()
        if inventario:
            db.session.delete(inventario)

        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha eliminado: ' + producto.nombre +  ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)
        
        db.session.delete(producto)
        db.session.commit()

        flash('Se ha eliminado el elemento, asegurese de cancelar los pedidos que puedan contener este elemento')
    except:
        flash('Ha ocurrido un error')

    return redirect(url_for('Productos.get_Productos'))
    
#INGREDIENTES-------------------------------------------------------
#Muestra todos los ingredientes
@Productos.route('/Admin/ingredientes', methods=['GET'])
@login_required
@role_required('admin', 'visor')
def get_Ingredientes():
    ingredients = Ingrediente.query.all()
    error = False
    r_i = []
    for ingredient in ingredients:
        inventario = ingredient.inventario[0]
        prov = Proveedor.query.filter_by(id=ingredient.proveedor_id).first()
        if not prov:
            error = True
        r_i.append({
            "id" : ingredient.id,
            "nombre" : ingredient.nombre,
            "stock" : inventario.stock,
            "proveedor" : prov,
            "precio" : ingredient.precio,
            "gramaje" : ingredient.gramaje.uni_larga,
        })
    
    if error:
        flash('Hay elementos con valores erroneos, favor de corregirlos')
        
    return render_template('ingredients.html', name = 'Ingredientes', type = 'lateral', ingredients = r_i)

#Muestra la vista de agregar ingredientes
@Productos.route('/Admin/add_ingrediente', methods=['GET'])
@login_required
@role_required('admin')
def get_show_new_ingrediente():
    providers = Proveedor.query.all()
    gramaje = Gramaje.query.all()
    return render_template('new_ingrediente.html', name = 'Agregar Ingrediente', type = 'lateral', providers = providers, gramaje = gramaje)

#Agrega ingredientes
@Productos.route('/Admin/add_ingrediente', methods=['POST'])
@login_required
@role_required('admin')
def add_ingrediente():
    nombre = request.form.get('nombre')
    prov = request.form.get('provider')
    precio = request.form.get('precio')
    gramaje = request.form.get('gramaje')
    
    ingr = Ingrediente(
        nombre = nombre,
        proveedor_id = prov,
        precio = precio,
        gramaje_id = gramaje
        )
    
    inventario = InventarioIngredientes(stock=0.0, ingrediente=ingr)
    ingr.inventario = [inventario]

    try:
        db.session.add(ingr)
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha agregado el ingrediente: ' + ingr.nombre +  ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)
        
        db.session.commit()
    except:
        flash('Error al insertar en la base de datos. Por favor, revise que los datos sean correctos y vuelva a intentar.')
        return redirect(url_for('Productos.get_Ingredientes'))

    return redirect(url_for('Productos.get_Ingredientes'))
    
#Agrega al stock ingredientes
@Productos.route('/Admin/add_ingrediente_stock', methods=['POST'])
@login_required
@role_required('admin', 'visor')
def add_ingrediente_stock():
    ingr = Ingrediente.query.get(int(request.form.get('id')))
    stock = request.form.get('ammount')
    
    ingr.inventario[0].stock += (float(stock) * 1000)
    
    ahora = datetime.now()
    fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
    log = Log(
        log = (current_user.name + ' ha agregado stock al ingrediente: ' + ingr.nombre + ' una cantidad de ' + str(float(stock) * 1000) +  ' - ' + fecha_hora),
        usuario_id = current_user.id
    )

    db.session.add(log)
    
    db.session.commit()
    return redirect(url_for('Productos.get_Ingredientes'))

#Muestra la vista de editar ingredientes
@Productos.route('/Ingrediente/<id>', methods=['GET'])
@login_required
@role_required('admin')
def get_show_ingrediente(id):
    ingrediente = Ingrediente.query.get(id)
    providers = Proveedor.query.all()
    return render_template('edit_ingredient.html', name = 'Editar Ingrediente', type = 'lateral', providers = providers, ingrediente = ingrediente, delete_route = ('/DeleteIngrediente/' + str(ingrediente.id)))

#Edita ingredientes
@Productos.route('/Ingrediente/<id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_ingrediente(id):
    ingrediente = Ingrediente.query.get(id)
    if not ingrediente:
        flash('No se encontró el ingrediente especificado')
        return redirect(url_for('Productos.get_Ingredientes'))
    
    nombre = request.form.get('nombre')
    prov = request.form.get('provider')
    precio = request.form.get('precio')
    
    # Validar que los campos no estén vacíos
    if not nombre or not prov or not precio:
        flash('Todos los campos son requeridos')
        return redirect(url_for('Productos.get_Ingredientes'))
    
    # Convertir los tipos de datos necesarios
    prov = int(prov)
    precio = float(precio)
    
    # Actualizar los datos del ingrediente
    ingrediente.nombre = nombre
    ingrediente.proveedor_id = prov
    ingrediente.precio = precio
    
    ahora = datetime.now()
    fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
    log = Log(
        log = (current_user.name + ' ha agregado actualizado el ingrediente: ' + ingrediente.nombre + ' - ' + fecha_hora),
        usuario_id = current_user.id
    )

    db.session.add(log)
    
    db.session.commit()
    
    return redirect(url_for('Productos.get_Ingredientes'))

# Elimina los ingredientes
@Productos.route('/DeleteIngrediente/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_ingrediente(id):
    try:
        ingrediente = Ingrediente.query.get(id)

        # Eliminar primero de la tabla inventario_ingredientes
        inventario = InventarioIngredientes.query.filter_by(ingrediente_id=id).first()
        if inventario:
            db.session.delete(inventario)

        db.session.delete(ingrediente)
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha eliminado al ingrediente: ' + ingrediente.nombre + ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)
        
        db.session.commit()

        flash('Se ha eliminado el elemento, asegurese de editar las recetas que puedan contener este elemento')
    except:
        flash('Ha ocurrido un error')

    return redirect(url_for('Productos.get_Ingredientes'))



#GRAMAJE---------------------------------------------------------------
@Productos.route('/Admin/gramaje', methods=['GET'])
@login_required
@role_required('admin')
def gramaje():
    gramajes = Gramaje.query.all()
    return render_template('gramaje.html', name = 'Gramaje', type = 'lateral', gramajes = gramajes)

@Productos.route('/Admin/addgramaje', methods=['POST'])
@login_required
@role_required('admin')
def gramaje_add():
    umi = request.form.get('uni_mini')
    ula = request.form.get('uni_larga')
    
    if not umi or not ula:
        flash('Por favor ingrese los campos requeridos')
        return redirect(url_for('Productos.gramaje'))
    
    gramaje = Gramaje(
        uni_mini = umi,
        uni_larga = ula
    )
    
    ahora = datetime.now()
    fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
    log = Log(
        log = (current_user.name + ' ha agregado el gramaje: ' + gramaje.uni_larga + ' - ' + fecha_hora),
        usuario_id = current_user.id
    )

    db.session.add(log)
    
    db.session.add(gramaje)
    db.session.commit()
    
    return redirect(url_for('Productos.gramaje'))

#INVENTARIO----------------------------------------------------------------
#Agrega productos, descuenta del inventario (Esta funcion sera larga, ya no quiero martha)
@Productos.route('/Producto_stock/<int:id>', methods=['POST'])
@login_required
@role_required('admin', 'visor')
def add_producto_stock(id):
    try:
        prod = Producto.query.get(id)
        stock = float(request.form.get('added'))
        rec = request.form.get('receta')
        receta = json.loads(rec)
        
        for ingrediente in receta:
            total_add = ingrediente['cantidad'] * stock
            if (ingrediente['disponible'] - total_add) < 0:
                flash('Demasiado stock, poco inventario, intenta de nuevo')
                return redirect('/Producto/'+str(id))
            ingr = Ingrediente.query.get(ingrediente['id'])
            ingr.inventario[0].stock -= total_add
        
        prod.inventario[0].stock += stock
        
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')
        log = Log(
            log = (current_user.name + ' ha agregado stock al producto: ' + prod.nombre + ' una cantidad de: ' + str(stock) + ' - ' + fecha_hora),
            usuario_id = current_user.id
        )

        db.session.add(log)
        
        db.session.commit()
    except:
        flash('Ha ocurrido un error, verifica la receta que no contenga elementos eliminados')
    return redirect(url_for('Productos.get_Productos'))