from models import Ingrediente, Producto
import json
import openai

def convert_Inputs(req):
    x = ''
    for n in range(int(req.get('indexes'))):
        ing = ('ingredient_' + str(n))
        cin = ('can_ing_' + str(n))
        x += (req.get(ing)+','+req.get(cin)+'|')
    
    return x

def convert_Objects(jeison):
    devolve = []
    for element in jeison[:-1].split('|'):
        ele2 = element.split(',')
        ingr = Ingrediente.query.filter_by(id=int(ele2[0])).first()
        devolve.append({
            "id" : ingr.id,
            "ingrediente" : ingr.nombre,
            "cantidad" : int(ele2[1]),
            "disponible" : ingr.inventario[0].stock,
            "gramaje_m" : ingr.gramaje.uni_mini,
            "gramaje_l" : ingr.gramaje.uni_larga
        })
    
    return devolve

def convert_carrito_Inputs(req):
    x = ''
    for n in range(int(req.get('elements'))):
        prod = 'prod_id_' + str(n)
        quan = 'quan_' + str(n)
        x += (req.get(prod) + ',' + req.get(quan) + '|')
        
    return x

def convert_Pedido(jeison):
    devolve = []
    total = 0.0
    
    for element in jeison[:-1].split('|'):
        elem = element.split(',')
        product = Producto.query.get(int(elem[0]))
        devolve.append({
            'producto' : product,
            'cantidad' : int(elem[1])
        })
        total += (product.precio_menudeo * int(elem[1]))
    
    return {
        'productos' : devolve,
        'total' : total
    }

def generate_notification_by_IA(prompt):
    # Generar una entrada para la IA utilizando OpenAI
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        n=1,
        temperature=0.7,
    )
    return completions.choices[0].text.strip()
