import numpy as np
from defs import *
from graphviz import Digraph
from graphviz import Source

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
import sys
from os import remove
from os import path
import pygraphviz as pgv


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elemental Cellular Automaton")

        self.initUI()

    def initUI(self):
        layoutPrincipal = QVBoxLayout()
        self.setLayout(layoutPrincipal)

        # Colores
        self.colorUno = QColor(0, 0, 0)
        self.rellenoUno = True

        self.colorDos = QColor(0, 0, 0)
        self.rellenoDos = False

        # Munu
        menu = QMenuBar()
        colores = menu.addMenu("Colors")
        menu.addMenu(colores)

        # Elemenetos menu Colores
        self.cambiarColorUno = QAction("Change node color", menu)
        self.cambiarColorCero = QAction("Change line color", menu)

        colores.addAction(self.cambiarColorUno)
        colores.addSeparator()
        colores.addAction(self.cambiarColorCero)
        colores.addSeparator()

        # Agregar Icono al color
        auxColor1 = QPixmap(100, 100)
        auxColor1.fill(self.colorUno)
        iconoColor1 = QIcon(auxColor1)

        auxColor2 = QPixmap(100, 100)
        auxColor2.fill(self.colorDos)
        iconoColor2 = QIcon(auxColor2)

        self.cambiarColorUno.setIcon(iconoColor1)
        self.cambiarColorCero.setIcon(iconoColor2)

        # Señales para conectar los eventos
        self.cambiarColorUno.triggered.connect(self.abrirColorPickerUno)
        self.cambiarColorCero.triggered.connect(self.abrirColorPickerDos)

        # Layout para la regla
        layoutRegla = QHBoxLayout()
        # Layout para el tamaño
        layoutTam = QHBoxLayout()
        # Layout para las opciones del diagrama
        layoutOps = QHBoxLayout()

        # Elementos para la regla
        lblRegla = QLabel("Rule: ")
        self.sliderRegla = QSlider(Qt.Horizontal)
        self.sliderRegla.setRange(0, 255)
        self.sliderRegla.setFocusPolicy(Qt.NoFocus)
        self.sliderRegla.setPageStep(1)
        self.lblRegla2 = QLabel("0")
        self.lblRegla2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lblRegla2.setMinimumWidth(80)

        self.sliderRegla.valueChanged.connect(self.updateLabelRegla)
        self.sliderRegla.sliderReleased.connect(self.sliderReleasedAction)

        fuente = lblRegla.font()
        fuente.setPointSize(12)
        self.setFont(fuente)

        # Elementos para el tamaño
        lblTam = QLabel("Size n: ")
        self.sliderTam = QSlider(Qt.Horizontal)
        self.sliderTam.setRange(1, 31)
        self.sliderTam.setFocusPolicy(Qt.NoFocus)
        self.sliderTam.setPageStep(1)
        self.sliderTam.setValue(1)
        self.lblTam2 = QLabel("1")
        self.lblTam2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lblTam2.setMinimumWidth(80)

        self.sliderTam.valueChanged.connect(self.updateLabelTam)
        self.sliderTam.sliderReleased.connect(self.sliderReleasedAction)

        # Opciones pequeñas
        self.layoutsDiagrama = QComboBox()
        self.layoutsDiagrama.addItems(
            ["circo", "twopi", "neato", "dot", "fdp", "osage", "patchwork", "sfdp"])
        self.layoutsDiagrama.currentIndexChanged.connect(self.modificarFSMD)

        self.tamLinea = QSpinBox()
        self.tamLinea.setMaximum(500)
        self.tamLinea.setMinimum(2)
        self.tamLinea.setSingleStep(2)
        # self.tamLinea.valueChanged.connect(self.sliderReleasedAction)
        self.tamLinea.valueChanged.connect(self.modificarFSMD)

        self.tamNodo = QSpinBox()
        self.tamNodo.setMaximum(500)
        self.tamNodo.setMinimum(1)
        self.tamNodo.setSingleStep(2)
        self.tamNodo.valueChanged.connect(self.modificarFSMD)

        self.figuraDiagrama = QComboBox()
        self.figuraDiagrama.addItems(
            ["circle", "point", "egg", "diamond", "oval"])
        self.figuraDiagrama.currentIndexChanged.connect(
            self.sliderReleasedAction)

        layoutOps.addWidget(QLabel("Layouts: "))
        layoutOps.addWidget(self.layoutsDiagrama)
        layoutOps.addWidget(QLabel("Line width: "))
        layoutOps.addWidget(self.tamLinea)
        layoutOps.addWidget(QLabel("Shape: "))
        layoutOps.addWidget(self.figuraDiagrama)
        layoutOps.addWidget(QLabel("Node size: "))
        layoutOps.addWidget(self.tamNodo)

        layoutRegla.addWidget(lblRegla)
        layoutRegla.addWidget(self.sliderRegla)
        layoutRegla.addWidget(self.lblRegla2)

        layoutTam.addWidget(lblTam)
        layoutTam.addWidget(self.sliderTam)
        layoutTam.addWidget(self.lblTam2)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setScene(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        hboxDibujo = QHBoxLayout()
        hboxDibujo.addWidget(self.view)

        layoutPrincipal.addWidget(menu)
        layoutPrincipal.addSpacerItem(
            QSpacerItem(150, 20, QSizePolicy.Expanding))
        layoutPrincipal.addLayout(layoutRegla)
        layoutPrincipal.addLayout(layoutTam)
        layoutPrincipal.addSpacerItem(
            QSpacerItem(150, 40, QSizePolicy.Expanding))
        layoutPrincipal.addLayout(layoutOps)
        layoutPrincipal.addLayout(hboxDibujo)

    def abrirColorPickerUno(self):
        self.colorUno = QColorDialog().getColor()
        auxColor1 = QPixmap(100, 100)
        auxColor1.fill(self.colorUno)
        iconoColor1 = QIcon(auxColor1)
        self.cambiarColorUno.setIcon(iconoColor1)
        self.sliderReleasedAction()
        pass

    def abrirColorPickerDos(self):
        self.colorDos = QColorDialog().getColor()
        auxColor2 = QPixmap(100, 100)
        auxColor2.fill(self.colorDos)
        iconoColor2 = QIcon(auxColor2)
        self.cambiarColorCero.setIcon(iconoColor2)
        self.sliderReleasedAction()
        pass

    def repintar(self, archivo):
        self.scene.clear()
        self.scene = QGraphicsScene()
        self.svgItem = QGraphicsSvgItem(archivo)
        self.scene.addItem(self.svgItem)
        self.view.setScene(self.scene)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.show()

    def modificarFSMD(self):
        g = pgv.AGraph()
        g.read('./res.gv')

        # Modificar ancho de linea
        g.edge_attr['penwidth'] = str(self.tamLinea.value())
        # Modificar layout
        g.graph_attr['layout'] = self.layoutsDiagrama.currentText()
        # modificar Tam de nodo
        g.node_attr['width'] = str(self.tamNodo.value())
        g.node_attr['height'] = str(self.tamNodo.value())

        g.write('res2.gv')
        g = Source.from_file('./res2.gv')
        # print(g.source)
        g.format = 'svg'
        g.render('res2.gv', view=False)
        self.repintar('./res2.gv.svg')

    def sliderReleasedAction(self):
        regla = self.sliderRegla.value()
        n = self.sliderTam.value()
        # Se genero el svg
        fsm = getFSM(regla, n, self.colorUno.name(), self.colorDos.name(), self.layoutsDiagrama.currentText(
        ), str(self.tamLinea.value()), self.figuraDiagrama.currentText())
        fsm.render('res.gv', view=False)
        self.scene.clear()
        self.scene = QGraphicsScene()
        self.svgItem = QGraphicsSvgItem('./res.gv.svg')
        self.scene.addItem(self.svgItem)
        self.view.setScene(self.scene)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.show()

    def updateLabelTam(self, value):
        self.lblTam2.setText(str(value))

    def updateLabelRegla(self, value):
        self.lblRegla2.setText(str(value))

    def wheelEvent(self, event):
        """
        Zoom in or out of the view.
        """
        zoomInFactor = 2.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.view.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.view.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.view.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.view.translate(delta.x(), delta.y())


if __name__ == "__main__":

    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(800, 800)
    widget.show()

    sys.exit(app.exec_())
