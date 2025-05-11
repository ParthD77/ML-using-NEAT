from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt
from network import Network
from typing import Tuple

"""
To use git:
git diff origin/main
git status
git fetch
git log HEAD..origin/main   # remote has - local doesnt
git log origin/main..HEAD   # local has - remote dosent


    Pull:
    git pull
    OR OPTIONAL/FIRST-TIME LINK
    git pull link

    Push:
git add .
git commit -m "Edit message info"
OR
git commit -a -m "Edit message info"
git push

    Branch:
git checkout -b new-feature-name

git add .
git commit -m "added new feature info"

git push -u origin new-feature-name

    Merge Branch to main:
git checkout main
git pull
git merge new-feature-name
git push
"""

"""
TODO:
    Find a  way to dispaly the network:
        how to know the height of each node?
    Different mutation than just random (gradient descent OR breeding OR other)

"""

class NetworkWidget(QWidget):
    net: Network


    def __init__(self, net: Network, width: int, height: int) -> None:
        super().__init__()
        self.net = net
        self.setFixedSize(width, height) # Set canvas size



    def get_net_info(self) -> Tuple[int, int]:
        """
        layers = largest node depth (0 inclusive)
        height = largest count of nodes in any given layer
        """
        layers = 0

        depths = {}
        for node in self.net.nodes:
            layers = max(layers, node.depth)
            depths.setdefault(node.depth, 0)
            depths[node.depth] += 1

        height = max(depths.values())

        return (layers, height)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1E1E1E"))  # background

        # box aroudn network
        pen_border = QPen(QColor("black"))
        pen_border.setWidth(5)
        painter.setPen(pen_border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect())


        layers, height = self.get_net_info()

        # Example: Draw nodes based on their depth (simple horizontal spacing)
        for node in self.net.nodes:
            x = node.depth * 150 + 50
            y = 100 + (1 * 70)  # You might want to improve this positioning
            painter.setBrush(QColor("blue"))
            painter.drawEllipse(x, y, 50, 50)

        painter.end()



class MainWindow(QMainWindow):


    def __init__(self, net: Network, x: int, y: int, width: int, height: int) -> None:
        super().__init__()
        self.setGeometry(x, y, width, height)
        self.setWindowTitle("NEAT Network")

        container = QtWidgets.QWidget()
        self.setCentralWidget(container)


        net_widht = width//2
        net_height = height//2
        layout = QGridLayout()                                                  
        canvas = NetworkWidget(net, net_widht, net_height)
        layout.addWidget(canvas, 0, 0)  # widget, row, column
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        container.setLayout(layout)


    # Set main frame to background black
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1E1E1E"))
        painter.end()

        #self.draw_something()


    def draw_something(self) -> None:          #test
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.drawLine(70, 45, 100, 45)
        painter.drawEllipse(20, 20, 50, 50)
        painter.end()
        self.label.setPixmap(canvas)




if __name__ == "__main__":
    app = QApplication([])
    network = Network(2, 2)
    network.process_network([1, 1])
    window = MainWindow(network, 400, 150, 1200, 700)

   # window.draw_network()
    window.show()
    app.exec()