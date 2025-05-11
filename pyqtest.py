from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets, uic
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


class MainWindow(QtWidgets.QMainWindow):
    net: Network


    def __init__(self, net: Network) -> None:
        super().__init__()
        self.net = net

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(1200, 700)
        canvas.fill(Qt.GlobalColor.white)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        #self.draw_something()

    def draw_something(self) -> None:          #test
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.drawLine(70, 45, 100, 45)
        painter.drawEllipse(20, 20, 50, 50)
        painter.end()
        self.label.setPixmap(canvas)


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


    def draw_network(self) -> None:
        canvas = self.label.pixmap()
        canvas.fill(Qt.GlobalColor.white)
        painter = QtGui.QPainter(canvas)
        info = self.get_net_info()
        

        for node in self.net.nodes:
            painter.drawEllipse(node.depth*50, 100, 50, 50)
        
        painter.end()
        self.label.setPixmap(canvas)




if __name__ == "__main__":
    app = QApplication([])
    network = Network(2, 2)
    network.process_network([1, 1])
    window = MainWindow(network)
    window.setGeometry(400, 150, 1200, 700)

    window.draw_network()
    window.show()
    app.exec()