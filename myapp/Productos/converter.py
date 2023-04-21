from models import Ingrediente
import json

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