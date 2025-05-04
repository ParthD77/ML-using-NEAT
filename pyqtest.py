from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import Qt
from network import Network

"""
To use git:
    Pull:
    git pull
    OR OPTIONAL/FIRST-TIME LINK
    git pull link

    Push:
git add .
git commit -m "Edit message info"
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
        self.draw_something()

    def draw_something(self) -> None:          #test
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.drawLine(70, 45, 100, 45)
        painter.drawEllipse(20, 20, 50, 50)
        painter.end()
        self.label.setPixmap(canvas)

    def draw_network(self) -> None:
        canvas = self.label.pixmap()
        canvas.fill(Qt.GlobalColor.white)
        painter = QtGui.QPainter(canvas)

        for node in self.net.nodes:
            painter.drawEllipse(node.depth, 100, 50, 50)



if __name__ == "__main__":
    app = QApplication([])
    net = Network(2, 2)
    net.process_network([1, 1])
    window = MainWindow(net)
    window.setGeometry(400, 150, 1200, 700)
    window.show()
    app.exec()