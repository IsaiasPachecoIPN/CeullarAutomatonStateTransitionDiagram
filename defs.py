import threading
import time
import numpy as np
from graphviz import Digraph

total_nodos = []


class Circular(list):

    def __init__(self, sequence=[]):
        super(Circular, self).__init__(sequence)
        self.position = 0

    def current(self):
        return self[self.position]

    def next(self, n=1):
        self.position = (self.position + n) % len(self)
        return self[self.position]

    def prev(self, n=1):
        return self.next(-n)


def buscarEnTabla(celula, tabla):
    for regla in tabla:
        aux = regla[0:3]
        x = np.equal(regla[0:3], celula)
        if x.all():
            return regla[3]


def procesamiento(arregloCircular, tabla, estadoInicial):
    salida = []
    for elem in estadoInicial:
        aux = [arregloCircular.prev(), arregloCircular.next(),
               arregloCircular.next()]
        salida.append(buscarEnTabla(aux, tabla))
    return salida


def ProcesarEntrada(tabla, estadoInicial, numGeneraciones):
    puntos = []
    puntos.append(Circular(estadoInicial))
    for x in range(numGeneraciones):
        res = procesamiento(Circular(puntos[x]), tabla, estadoInicial)
        puntos.append(res)
    return puntos

# Se crea el diagrama


def getFSM(r_num, n, colorNodos, colorLineas, ly, grosorln, figura):

    g = Digraph('Diagrama', filename='res.gv', format='svg')
    # Convierte la regla en formato decimal a binario
    numEntrada = format(r_num, '#010b')
    # Separa el binario de la regla en un arreglo
    regla = [int(x) for x in numEntrada[2:]]
    # Se obtiene la tabla par la regla especificada
    tabla = np.array(([1, 1, 1, regla[0]], [1, 1, 0, regla[1]], [1, 0, 1, regla[2]], [1, 0, 0, regla[3]], [
                     0, 1, 1, regla[4]], [0, 1, 0, regla[5]], [0, 0, 1, regla[6]], [0, 0, 0, regla[7]]))

    # Se establecen los atributos
    g.attr('graph', layout=ly, packmode='graph')
    g.attr('node', shape=figura, style='filled',
           color=colorNodos, fontcolor="#ffffff")
    g.attr('edge', arrowhead='none', dir='none', color=colorLineas)
    #print( "source fron fn: " , g.source)
    # Aux es el tam de las cadenas o nodos
    aux = 2**n

    num_hilos = 4

    # Se divide en rangos para y utilizar 4 hilos
    rangos = []
    rangos.append(aux)
    for i in range(4):
        rangos.append(aux//2)
        aux //= 2
    rangos.extend([0])
    rangos.reverse()

    # print(rangos)
    # Se crean n hilos
    hilos = []
    for i in range(num_hilos+1):
        hilo = threading.Thread(name="hilo%s" % i, target=h_obtenerNodos, args=(i, g,), kwargs={
                                'regla_tabla': tabla, 'tam_cad': n, 'linf': rangos[i], 'lsup': rangos[i+1]})
        hilos.append(hilo)
        hilo.start()

    # Se espera por los n hilos
    for i in range(num_hilos+1):
        hilos[i].join()

    return g


def nodos_a_cadNodos(lista_nodos, n):
    nodos = []
    for i in range(0, len(lista_nodos), n):
        a = ""
        for x in range(n):
            a += str(lista_nodos[i+x])
        nodos.append(a)
        pass
    return nodos


def transicion(arreglo_cad, n):
    arreglo_cad = np.array(arreglo_cad)
    aux_ta = sum(arreglo_cad[:, :n].tolist(), [])

    return nodos_a_cadNodos(aux_ta, n)


def h_obtenerNodos(num_hilo, g,  **datos):
    tam_cad = datos['tam_cad']
    limite_inf = datos['linf']
    limite_sup = datos['lsup']
    tablaRegla = datos['regla_tabla']

    for limite_inf in range(limite_inf, limite_sup, 1):
        transicionA = format(limite_inf, "0"+str(tam_cad)+"b")
        transicionB = ProcesarEntrada(
            tablaRegla, list(map(int, transicionA)), 1)
        transicionesAB = transicion(transicionB, tam_cad)
        g.node(transicionA, label=transicionA)
        g.edge(transicionesAB[0], transicionesAB[1])
