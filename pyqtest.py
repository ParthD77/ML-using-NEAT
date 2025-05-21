from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPoint
from network import Network
from typing import Tuple, List, Dict

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
    somehow have a main file (maybe this one?) that has x agents and computes everything and such,
        while  only displaying x network, adjustable values?

    grading agents (BUG: networks currently spam nodes cause nothing stops it, maybe clean up or grade large networks harshly)
    
    Different mutation than just random (gradient descent OR breeding OR other)

    Data clean up? (del temp variables once finished using)

"""

class NetworkWidget(QWidget):
    net: Network


    def __init__(self, net: Network, width: int, height: int) -> None:
        super().__init__()
        self.net = net
        self.setFixedSize(width, height) # Set canvas size



    def get_net_info(self) -> Tuple[int, Dict[int, List[int]]]:
        """
        layers = largest node depth (0 inclusive)
        height = largest count of nodes in any given layer
        """
        self.net.sort_nodes_depth()
        # Total # of layers (max depth)
        layers = 0
        # number of nodes per depth [0, count]
        # first value is to be used when drawing to track which have been drawn
        heights = {}

        # for each node compare against max of node or stored layer
        # for each depth set to [0, 0] and increment second value [0, node per layer]
        for node in self.net.nodes:
            # ensure useless nodes dont bloat drawing
            if node.depth == -1:
                continue
            layers = max(layers, node.depth)
            heights.setdefault(node.depth, [0, 0])
            heights[node.depth][1] += 1

        return (layers, heights)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1E1E1E"))  # background

        # box around network
        pen_border = QPen(QColor("black"))
        pen_border.setWidth(3)
        painter.setPen(pen_border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect())



        layers, heights = self.get_net_info()


        max_height = max(height[1] for height in heights.values())

        # (total space - padding) // (max_nodes) = max_node size
        node_size_x = (self.width() - 200) // (layers + 1)
        node_size_y = (self.height() - 100) // (max_height + 1)
        node_size = min(node_size_x, node_size_y, 100)
        
        max_x = self.width()-node_size
        max_y = self.height()-node_size

        # lowkey this somehow seems to work and idk how so ima leave it
        # plan is to fix the nodes witihn the box

        # store each nodes position
        positions = {}
        for node in self.net.nodes:
            # dont display disjoint nodes
            if node.depth == -1:
                continue
            # x = total space // total depth*node_depth
            x = max_x//(layers)*node.depth
            # total space // (layer height+1) * (already displayed nodes + 1(offset to center))
            y = max_y//(heights[node.depth][1]+1)*(heights[node.depth][0]+1)
            heights[node.depth][0] += 1
            # works cause splitting area into count + 1 gives enough slots in middle
            positions[node] = (x, y)
            painter.setBrush(QColor("#2196F3"))
            painter.drawEllipse(x, y, node_size, node_size)
    

        # set nerves position with offset for node
        for nerve in self.net.nerves:
            # check if node that this nerve connects to wasnt drawn
            if nerve.start not in positions or nerve.end not in positions:
                continue

            start_x = positions[nerve.start][0] + node_size
            start_y = positions[nerve.start][1] + (node_size // 2)
            end_x = positions[nerve.end][0]
            end_y = positions[nerve.end][1] + (node_size // 2)
            

            # pos weight = green, neg weight = red
            # |weight| determisn thickness
            if nerve.weight > 0:
                painter.setPen(QPen(QColor("#00C853"), 1+abs(nerve.weight * 2)))
            elif nerve.weight == 0:
                painter.setPen(QPen(QColor("#B0BEC5"), 1+abs(nerve.weight * 2)))
            else:
                painter.setPen(QPen(QColor("#D50000"), 1+abs(nerve.weight * 2)))
            
            painter.drawLine(start_x, start_y, end_x, end_y)

            if node_size >= 50:
                # dispaly the weights only if enough space
                painter.setPen(QColor("#FFFFFF"))  
                font = painter.font()
                font.setPointSize(10)
                painter.setFont(font)

                weight_x = (end_x+start_x) // 2
                weight_y = (end_y+start_y) // 2
                weight_point = QPoint(weight_x, weight_y)
                painter.drawText(weight_point, f"{nerve.weight:.2f}")

        # draw node values
        if node_size >= 50:
            for node in self.net.nodes:
                # if node wasnt drawn skip it
                if node.depth == -1:
                    continue
                # Center the text on the node
                # Calculate text position (centered)
                text_x = positions[node][0] + node_size // 2
                text_y = positions[node][1] + node_size // 2
                
                # Draw the value (formatted to 2 decimal places)
                painter.drawText(QPoint(text_x, text_y), f"{node.value:.2f}")


        painter.end()



class MainWindow(QMainWindow):


    def __init__(self, net: Network, x: int, y: int, width: int, height: int) -> None:
        super().__init__()
        self.setGeometry(x, y, width, height)
        self.setWindowTitle("NEAT Network")

        container = QtWidgets.QWidget()
        self.setCentralWidget(container)


        net_width = width//2
        net_height = height//2
        layout = QGridLayout()  
        canvas = NetworkWidget(net, net_width, net_height)
        layout.addWidget(canvas, 0, 0)  # widget, row, column
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # TODO: maybe remove later?
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setLayout(layout)


    # Set main frame to background black
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#2E2E2E"))
        painter.end()

        #self.draw_something()


    def draw_something(self) -> None:          #test
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.drawLine(70, 45, 100, 45)
        painter.drawEllipse(20, 20, 50, 50)
        painter.end()
        self.label.setPixmap(canvas)


# public to display any network
def display_network(net: Network, width: int = 1200, height: int = 700, x: int = 400, y: int = 150) -> None:
    app = QApplication([])
    window = MainWindow(net, x, y, width, height)
    window.show()
    app.exec()



if __name__ == "__main__":
    app = QApplication([])
    network = Network(2, 1)
    for i in range(100):
        network.mutate_network()
    network.process_network([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    window = MainWindow(network, 400, 150, 1200, 700)
    print(len(network.nodes))
    print(len(network.nerves))
   # window.draw_network()
    window.show()
    app.exec()