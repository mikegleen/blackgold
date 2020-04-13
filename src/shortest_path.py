"""
https://www.bogotobogo.com/python/python_Dijkstras_Shortest_Path_Algorithm.php
"""
import heapq  # move from middle of file
import sys


class Vertex:
    def __init__(self, node_id):  # "node_id" is more descriptive
        self.id = node_id
        self.adjacent = {}
        # Set distance to infinity for all nodes
        self.distance = sys.maxsize  # 2to3
        # Mark all nodes unvisited
        self.visited = False
        # Predecessor
        self.previous = None

    def add_neighbor(self, neighbor, weight):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return list(self.adjacent.keys())  # 2to3

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]
    
    # Remove getters and setters as your use of them was inconsistent and they are not very Pythonic.

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

    # Python 3 issue, see:
    # https://stackoverflow.com/questions/43477958/typeerror-not-supported-between-instances-python
    def __lt__(self, other):
        return self.distance < other.distance


class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices += 1  # just because
        new_vertex = Vertex(node)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        return self.vert_dict.get(n, None)  # use the built-in function

    def add_edge(self, frm, to, cost=0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        return list(self.vert_dict.keys())  # 2to3


def shortest(v, path):
    """ make shortest path from v.previous"""
    if v.previous:
        path.append(v.previous.id)
        shortest(v.previous, path)
    return


def dijkstra(a_graph, start):   # change aGraph to a_graph because PyCharm was whining about it
    print('''Dijkstra's shortest path''')
    # Set the distance for the start node to zero
    start.distance = 0

    # Put tuple pair into the priority queue
    # This is now a list of vertices because, having added __lt__(), they are now comparable.
    unvisited_queue = [v for v in a_graph]
    heapq.heapify(unvisited_queue)

    while len(unvisited_queue):
        # Pops a vertex with the smallest distance
        current = heapq.heappop(unvisited_queue)
        current.visited = True

        # for next in v.adjacent:
        for nextv in current.adjacent:  # "next" was shadowing a built-in.
            # if visited, skip
            if nextv.visited:
                continue
            new_dist = current.distance + current.get_weight(nextv)
            nextv_dist = nextv.distance
            if new_dist < nextv_dist:
                nextv.distance = new_dist
                nextv.previous = current
                updated = 'updated'
            else:
                updated = 'not updated'
            print('%s : current = %s next = %s new_dist = %s'
                  % (updated, current.id, nextv.id, nextv_dist))

        # Rebuild heap
        # Removed redundant code.
        # Put all vertices not visited into the queue
        unvisited_queue = [v for v in a_graph if not v.visited]
        heapq.heapify(unvisited_queue)


def main():

    g = Graph()

    g.add_vertex('a')
    g.add_vertex('b')
    g.add_vertex('c')
    g.add_vertex('d')
    g.add_vertex('e')
    g.add_vertex('f')

    g.add_edge('a', 'b', 7)
    g.add_edge('a', 'c', 9)
    g.add_edge('a', 'f', 14)
    g.add_edge('b', 'c', 10)
    g.add_edge('b', 'd', 15)
    g.add_edge('c', 'd', 11)
    g.add_edge('c', 'f', 2)
    g.add_edge('d', 'e', 6)
    g.add_edge('e', 'f', 9)

    print('Graph data:')
    for v in g:
        for w in v.get_connections():
            print('( %s , %s, %3d)' % (v.id, w.id, v.get_weight(w)))

    dijkstra(g, g.get_vertex('a'))

    target = g.get_vertex('e')
    path = [target.id]
    shortest(target, path)
    print('The shortest path : %s' % (path[::-1]))


if __name__ == '__main__':
    main()  # moved code to main function to avoid "shadowing in outer scope" warnings.
    
