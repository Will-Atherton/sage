# -*- coding: utf-8 -*-
r"""
Modular Decomposition

This module implements the function for computing the modular decomposition
of undirected graphs.
"""
# ****************************************************************************
#       Copyright (C) 2017 Lokesh Jain <lokeshj1703@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
# ****************************************************************************

from enum import Enum

from sage.misc.random_testing import random_testing


class NodeType(Enum):
    """
    NodeType is an enumeration class used to define the various types of nodes
    in modular decomposition tree.

    The various node types defined are

    - ``PARALLEL`` -- indicates the node is a parallel module

    - ``SERIES`` -- indicates the node is a series module

    - ``PRIME`` -- indicates the node is a prime module

    - ``FOREST`` -- indicates a forest containing trees

    - ``NORMAL`` -- indicates the node is normal containing a vertex
    """
    PRIME = 0
    SERIES = 1
    PARALLEL = 2
    NORMAL = 3
    FOREST = -1

    def is_degenerate(self):
        return self is NodeType.PARALLEL or self is NodeType.SERIES

    def __repr__(self):
        r"""
        String representation of this node type.

        EXAMPLES::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import NodeType
            sage: repr(NodeType.PARALLEL)
            'PARALLEL'
        """
        return self.name

    def __str__(self):
        """
        String representation of this node type.

        EXAMPLES::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import NodeType
            sage: str(NodeType.PARALLEL)
            'PARALLEL'
        """
        return repr(self)


class NodeSplit(Enum):
    """
    Enumeration class used to specify the split that has occurred at the node or
    at any of its descendants.

    ``NodeSplit`` is defined for every node in modular decomposition tree and is
    required during the refinement and promotion phase of modular decomposition
    tree computation. Various node splits defined are

    - ``LEFT_SPLIT`` -- indicates a left split has occurred

    - ``RIGHT_SPLIT`` -- indicates a right split has occurred

    - ``BOTH_SPLIT`` -- indicates both left and right split have occurred

    - ``NO_SPLIT`` -- indicates no split has occurred
    """
    LEFT_SPLIT = 1
    RIGHT_SPLIT = 2
    BOTH_SPLIT = 3
    NO_SPLIT = 0


class VertexPosition(Enum):
    """
    Enumeration class used to define position of a vertex w.r.t source in
    modular decomposition.

    For computing modular decomposition of connected graphs a source vertex is
    chosen. The position of vertex is w.r.t this source vertex. The various
    positions defined are

    - ``LEFT_OF_SOURCE`` -- indicates vertex is to left of source and is a
      neighbour of source vertex

    - ``RIGHT_OF_SOURCE`` -- indicates vertex is to right of source and is
      connected to but not a neighbour of source vertex

    - ``SOURCE`` -- indicates vertex is source vertex
    """
    LEFT_OF_SOURCE = -1
    RIGHT_OF_SOURCE = 1
    SOURCE = 0


class Node:
    """
    Node class stores information about the node type, node split and index of
    the node in the parent tree.

    Node type can be ``PRIME``, ``SERIES``, ``PARALLEL``, ``NORMAL`` or
    ``FOREST``. Node split can be ``NO_SPLIT``, ``LEFT_SPLIT``, ``RIGHT_SPLIT``
    or ``BOTH_SPLIT``. A node is split in the refinement phase and the split
    used is propagated to the ancestors.

    - ``node_type`` -- is of type NodeType and specifies the type of node

    - ``node_split`` -- is of type NodeSplit and specifies the type of splits
      which have occurred in the node and its descendants

    - ``index_in_root`` -- specifies the index of the node in the forest
      obtained after promotion phase

    - ``comp_num`` -- specifies the number given to nodes in a (co)component
      before refinement

    - ``is_separated`` -- specifies whether a split has occurred with the node
      as the root
    """
    def __init__(self, node_type):
        r"""
        Create a node with the given node type.

        EXAMPLES::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import *
            sage: n = Node(NodeType.SERIES); n.node_type
            SERIES
            sage: n.children
            []
        """
        self.node_type = node_type
        self.node_split = NodeSplit.NO_SPLIT
        self.index_in_root = -1
        self.comp_num = -1
        self.is_separated = False
        self.children = []

    def set_node_split(self, node_split):
        """
        Add node_split to the node split of self.

        ``LEFT_SPLIT`` and ``RIGHT_SPLIT`` can exist together in ``self`` as
        ``BOTH_SPLIT``.

        INPUT:

        - ``node_split`` -- node_split to be added to self

        EXAMPLES::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import *
            sage: node = Node(NodeType.PRIME)
            sage: node.set_node_split(NodeSplit.LEFT_SPLIT)
            sage: node.node_split == NodeSplit.LEFT_SPLIT
            True
            sage: node.set_node_split(NodeSplit.RIGHT_SPLIT)
            sage: node.node_split == NodeSplit.BOTH_SPLIT
            True
            sage: node = Node(NodeType.PRIME)
            sage: node.set_node_split(NodeSplit.BOTH_SPLIT)
            sage: node.node_split == NodeSplit.BOTH_SPLIT
            True
        """
        if self.node_split == NodeSplit.NO_SPLIT:
            self.node_split = node_split
        elif ((self.node_split == NodeSplit.LEFT_SPLIT and
               node_split == NodeSplit.RIGHT_SPLIT) or
              (self.node_split == NodeSplit.RIGHT_SPLIT and
               node_split == NodeSplit.LEFT_SPLIT)):
            self.node_split = NodeSplit.BOTH_SPLIT

    def has_left_split(self):
        """
        Check whether ``self`` has ``LEFT_SPLIT``.

        EXAMPLES::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import *
            sage: node = Node(NodeType.PRIME)
            sage: node.set_node_split(NodeSplit.LEFT_SPLIT)
            sage: node.has_left_split()
            True
            sage: node = Node(NodeType.PRIME)
            sage: node.set_node_split(NodeSplit.BOTH_SPLIT)
            sage: node.has_left_split()
            True
        """
        return (self.node_split == NodeSplit.LEFT_SPLIT or
                self.node_split == NodeSplit.BOTH_SPLIT)

    def has_right_split(self):
        """
        Check whether ``self`` has ``RIGHT_SPLIT``.

        EXAMPLES::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import *
            sage: node = Node(NodeType.PRIME)
            sage: node.set_node_split(NodeSplit.RIGHT_SPLIT)
            sage: node.has_right_split()
            True
            sage: node = Node(NodeType.PRIME)
            sage: node.set_node_split(NodeSplit.BOTH_SPLIT)
            sage: node.has_right_split()
            True
        """
        return (self.node_split == NodeSplit.RIGHT_SPLIT or
                self.node_split == NodeSplit.BOTH_SPLIT)

    def __repr__(self):
        r"""
        Return a string representation of the node.

        EXAMPLES::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import *
            sage: n = Node(NodeType.PRIME)
            sage: n.children.append(create_normal_node(1))
            sage: n.children.append(create_normal_node(2))
            sage: str(n)
            'PRIME [NORMAL [1], NORMAL [2]]'
        """
        if self.node_type == NodeType.SERIES:
            s = "SERIES "
        elif self.node_type == NodeType.PARALLEL:
            s = "PARALLEL "
        elif self.node_type == NodeType.PRIME:
            s = "PRIME "
        elif self.node_type == NodeType.FOREST:
            s = "FOREST "
        else:
            s = "NORMAL "

        s += str(self.children)
        return s

    def __eq__(self, other):
        r"""
        Compare two nodes for equality.

        EXAMPLES::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import *
            sage: n1 = Node(NodeType.PRIME)
            sage: n2 = Node(NodeType.PRIME)
            sage: n3 = Node(NodeType.SERIES)
            sage: n1 == n2
            True
            sage: n1 == n3
            False
        """
        return (self.node_type == other.node_type and
                self.node_split == other.node_split and
                self.index_in_root == other.index_in_root and
                self.comp_num == other.comp_num and
                self.is_separated == other.is_separated and
                self.children == other.children)


def create_prime_node():
    """
    Return a prime node with no children

    OUTPUT:

    A node object with node_type set as NodeType.PRIME

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import create_prime_node
        sage: node = create_prime_node()
        sage: node
        PRIME []
    """
    return Node(NodeType.PRIME)


def create_parallel_node():
    """
    Return a parallel node with no children

    OUTPUT:

    A node object with node_type set as NodeType.PARALLEL

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import create_parallel_node
        sage: node = create_parallel_node()
        sage: node
        PARALLEL []
    """
    return Node(NodeType.PARALLEL)


def create_series_node():
    """
    Return a series node with no children

    OUTPUT:

    A node object with node_type set as NodeType.SERIES

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import create_series_node
        sage: node = create_series_node()
        sage: node
        SERIES []
    """
    return Node(NodeType.SERIES)


def create_normal_node(vertex):
    """
    Return a normal node with no children

    INPUT:

    - ``vertex`` -- vertex number

    OUTPUT:

    A node object representing the vertex with node_type set as NodeType.NORMAL

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import create_normal_node
        sage: node = create_normal_node(2)
        sage: node
        NORMAL [2]
    """
    node = Node(NodeType.NORMAL)
    node.children.append(vertex)
    return node


def print_md_tree(root):
    """
    Print the modular decomposition tree

    INPUT:

    - ``root`` -- root of the modular decomposition tree

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(modular_decomposition(graphs.IcosahedralGraph()))
        PRIME
         1
         5
         7
         8
         11
         0
         2
         6
         3
         9
         4
         10
    """

    def recursive_print_md_tree(root, level):
        """
        Print the modular decomposition tree at root

        INPUT:

        - ``root`` -- root of the modular decomposition tree

        - ``level`` -- indicates the depth of root in the original modular
          decomposition tree
        """
        if root.node_type != NodeType.NORMAL:
            print("{}{}".format(level, str(root.node_type)))
            for tree in root.children:
                recursive_print_md_tree(tree, level + " ")
        else:
            print("{}{}".format(level, str(root.children[0])))

    recursive_print_md_tree(root, "")


# =============================================================================
# Habib Maurer algorithm
# =============================================================================

def gamma_classes(graph):
    """
    Partition the edges of the graph into Gamma classes.

    Two distinct edges are Gamma related if they share a vertex but are not
    part of a triangle.  A Gamma class of edges is a collection of edges such
    that any edge in the class can be reached from any other by a chain of
    Gamma related edges (that are also in the class).

    The two important properties of the Gamma class

    * The vertex set corresponding to a Gamma class is a module
    * If the graph is not fragile (neither it or its complement is
      disconnected) then there is exactly one class that visits all the
      vertices of the graph, and this class consists of just the edges that
      connect the maximal strong modules of that graph.

    EXAMPLES:

    The gamma_classes of the octahedral graph are the three 4-cycles
    corresponding to the slices through the center of the octahedron::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import gamma_classes
        sage: g = graphs.OctahedralGraph()
        sage: sorted(gamma_classes(g), key=str)
        [frozenset({0, 1, 4, 5}), frozenset({0, 2, 3, 5}), frozenset({1, 2, 3, 4})]

    TESTS:

    Ensure that the returned vertex sets from some random graphs are modules::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import test_gamma_modules
        sage: test_gamma_modules(2, 10, 0.5)
    """
    from itertools import chain

    from sage.sets.disjoint_set import DisjointSet

    pieces = DisjointSet(frozenset(e) for e in graph.edge_iterator(labels=False))
    for v in graph:
        neighborhood = graph.subgraph(vertices=graph.neighbors(v))
        for component in neighborhood.complement().connected_components():
            v1 = component[0]
            e = frozenset([v1, v])
            for vi in component[1:]:
                ei = frozenset([vi, v])
                pieces.union(e, ei)
    return {frozenset(chain.from_iterable(loe)): loe for loe in pieces}


def habib_maurer_algorithm(graph, g_classes=None):
    """
    Compute the modular decomposition by the algorithm of Habib and Maurer

    Compute the modular decomposition of the given graph by the algorithm of
    Habib and Maurer [HM1979]_ . If the graph is disconnected or its complement
    is disconnected return a tree with a ``PARALLEL`` or ``SERIES`` node at the
    root and children being the modular decomposition of the subgraphs induced
    by the components. Otherwise, the root is ``PRIME`` and the modules are
    identified by having identical neighborhoods in the gamma class that spans
    the vertices of the subgraph (exactly one is guaranteed to exist). The gamma
    classes only need to be computed once, as the algorithm computes the the
    classes for the current root and each of the submodules. See also [BM1983]_
    for an equivalent algorithm described in greater detail.

    INPUT:

    - ``graph`` -- the graph for which modular decomposition tree needs to be
      computed

    - ``g_classes`` -- dictionary (default: ``None``); a dictionary whose values
      are the gamma classes of the graph, and whose keys are a frozenset of the
      vertices corresponding to the class. Used internally.

    OUTPUT:

    The modular decomposition tree of the graph.

    EXAMPLES:

    The Icosahedral graph is Prime::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(habib_maurer_algorithm(graphs.IcosahedralGraph()))
        PRIME
         1
         5
         7
         8
         11
         0
         2
         6
         3
         9
         4
         10

    The Octahedral graph is not Prime::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(habib_maurer_algorithm(graphs.OctahedralGraph()))
        SERIES
         PARALLEL
          0
          5
         PARALLEL
          1
          4
         PARALLEL
          2
          3

    Tetrahedral Graph is Series::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(habib_maurer_algorithm(graphs.TetrahedralGraph()))
        SERIES
         0
         1
         2
         3

    Modular Decomposition tree containing both parallel and series modules::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d = {2:[4,3,5], 1:[4,3,5], 5:[3,2,1,4], 3:[1,2,5], 4:[1,2,5]}
        sage: g = Graph(d)
        sage: print_md_tree(habib_maurer_algorithm(g))
        SERIES
         PARALLEL
          1
          2
         PARALLEL
          3
          4
         5

    Graph from Marc Tedder implementation of modular decomposition::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d = {1:[5,4,3,24,6,7,8,9,2,10,11,12,13,14,16,17], 2:[1],
        ....:       3:[24,9,1], 4:[5,24,9,1], 5:[4,24,9,1], 6:[7,8,9,1],
        ....:       7:[6,8,9,1], 8:[6,7,9,1], 9:[6,7,8,5,4,3,1], 10:[1],
        ....:       11:[12,1], 12:[11,1], 13:[14,16,17,1], 14:[13,17,1],
        ....:       16:[13,17,1], 17:[13,14,16,18,1], 18:[17], 24:[5,4,3,1]}
        sage: g = Graph(d)
        sage: test_modular_decomposition(habib_maurer_algorithm(g), g)
        True

    Graph from the :wikipedia:`Modular_decomposition`::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d2 = {1:[2,3,4], 2:[1,4,5,6,7], 3:[1,4,5,6,7], 4:[1,2,3,5,6,7],
        ....:       5:[2,3,4,6,7], 6:[2,3,4,5,8,9,10,11],
        ....:       7:[2,3,4,5,8,9,10,11], 8:[6,7,9,10,11], 9:[6,7,8,10,11],
        ....:       10:[6,7,8,9], 11:[6,7,8,9]}
        sage: g = Graph(d2)
        sage: test_modular_decomposition(habib_maurer_algorithm(g), g)
        True

    TESTS:

    Bad Input::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = DiGraph()
        sage: habib_maurer_algorithm(g)
        Traceback (most recent call last):
        ...
        ValueError: Graph must be undirected

    Empty Graph is Prime::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = Graph()
        sage: habib_maurer_algorithm(g)
        PRIME []


    Ensure that a random graph and an isomorphic graph have identical modular
    decompositions. ::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: permute_decomposition(2, habib_maurer_algorithm, 20, 0.5)
    """
    if graph.is_directed():
        raise ValueError("Graph must be undirected")

    if not graph.order():
        return create_prime_node()

    if graph.order() == 1:
        root = create_normal_node(next(graph.vertex_iterator()))
        return root

    elif not graph.is_connected():
        root = create_parallel_node()
        root.children = [habib_maurer_algorithm(graph.subgraph(vertices=sg), g_classes)
                         for sg in graph.connected_components()]
        return root

    g_comp = graph.complement()
    if g_comp.is_connected():
        from collections import defaultdict
        root = create_prime_node()
        if g_classes is None:
            g_classes = gamma_classes(graph)
        vertex_set = frozenset(graph)
        edges = [tuple(e) for e in g_classes[vertex_set]]
        sub = graph.subgraph(edges=edges)
        d = defaultdict(list)
        for v in sub:
            for v1 in sub.neighbor_iterator(v):
                d[v1].append(v)
        d1 = defaultdict(list)
        for k, v in d.items():
            d1[frozenset(v)].append(k)
        root.children = [habib_maurer_algorithm(graph.subgraph(vertices=sg), g_classes)
                         for sg in d1.values()]
        return root

    root = create_series_node()
    root.children = [habib_maurer_algorithm(graph.subgraph(vertices=sg), g_classes)
                     for sg in g_comp.connected_components()]
    return root

# ==============================================================================
# Tedder Algorithm
# ==============================================================================
class _TedderTreeNode():
    """
    The main tree node class for the Tedder algorithm, used as a base for which
    the other node classes inherit from.
    Implements the children of a node as a doubly linked list. Each node stores 
    the leftmost of its children, the number of children it has, and the left 
    and right siblings of the node.
    Nodes are added as the leftmost child (the first in the linked list)
    """

    def __init__(self):
        self.parent = None
        # - ``parent`` -- _TedderTreeNode, the parent of this node in the tree
        self.first_child = None
        # - ``first_child`` -- _TedderTreeNode, the leftmost child of this node
        self.left_sibling = None
        # - ``left_sibling`` -- _TedderTreeNode, the left sibling of this node
        self.right_sibling = None
        # - ``right_sibling`` -- _TedderTreeNode, the right sibling of this node
        self.num_children = 0
        # - ``num_children`` -- Integer, the number of children this node has
    
    def add_child(self, child):
        """
        Adds a child node (``child``) as the leftmost child of this node, after
        removing it from where it currently is.

        INPUT:
        
        - ``child`` -- _TedderTreeNode

        EXAMPLES:

        Series of adding children (Using _TedderMDLeafNode to show order)::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode, _TedderMDLeafNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderTreeNode()
            sage: n3 = _TedderMDLeafNode(1)
            sage: n2.add_child(n3)
            sage: n2
            {1}
            sage: n1.add_child(n2)
            sage: n1
            {{1}}
            sage: n4 = _TedderMDLeafNode(2)
            sage: n1.add_child(n4)
            sage: n5 = _TedderMDLeafNode(3)
            sage: n1.add_child(n5)
            sage: n1
            {3, 2, {1}}

        Adding a child removes it from where it is currently::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n1
            {{}}
            sage: n3 = _TedderTreeNode()
            sage: n3.add_child(n2)
            sage: n1
            {}
            sage: n3
            {{}}
        """
        # Remove ``child`` from where it is currently
        child.remove()

        # Add child as the first child, and fix the pointers
        if self.first_child is not None:
            self.first_child.left_sibling = child
            child.right_sibling = self.first_child
        self.first_child = child
        child.parent = self

        # This node now has one more child.
        self.num_children += 1
    
    def has_no_children(self):
        """
        Returns True if this node has no children, and False otherwise

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode
            sage: n1 = _TedderTreeNode()
            sage: n1.has_no_children()
            True
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n1.has_no_children()
            False
        """
        return self.num_children == 0
    
    def has_only_one_child(self):
        """
        Returns True if this node has exactly one child, and False otherwise

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode
            sage: n1 = _TedderTreeNode()
            sage: n1.has_only_one_child()
            False
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n1.has_only_one_child()
            True
            sage: n3 = _TedderTreeNode()
            sage: n1.add_child(n3)
            sage: n1.has_only_one_child()
            False
        """
        return self.num_children == 1
    
    def replace_with(self, replacement):
        """
        Replaces the subtree rooted at this node with another subtree rooted at 
        the supplied node (``replacement``), after removing it from where it is 
        currently

        INPUT:
        
        - ``replacement`` -- _TedderTreeNode

        EXAMPLES:
        
        Using _TedderMDLeafNode to distinguish between nodes::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode, _TedderMDLeafNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderMDLeafNode(1)
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDLeafNode(2)
            sage: n1.add_child(n3)
            sage: n1
            {2, 1}
            sage: n4 = _TedderMDLeafNode(3)
            sage: n2.replace_with(n4)
            sage: n1
            {2, 3}
        """
        # Remove ``replacement`` from where it is currently
        replacement.remove()

        # Change the sibling/parent pointers appropriately
        replacement.left_sibling = self.left_sibling
        replacement.right_sibling = self.right_sibling
        if self.left_sibling is not None:
            self.left_sibling.right_sibling = replacement
        if self.right_sibling is not None:
            self.right_sibling.left_sibling = replacement
        replacement.parent = self.parent
        if self.parent is not None and self.parent.first_child == self:
            # This node is the first child, so ``replacement`` becomes the first 
            # child
            self.parent.first_child = replacement

        # Reset this node's sibling/parent pointers to None, as it is no longer 
        # connected to them.
        self.parent = None
        self.left_sibling = None
        self.right_sibling = None
    
    def remove(self):
        """
        Removes the subtree rooted at this node

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderTreeNode()
            sage: n1.add_child(n3)
            sage: n4 = _TedderTreeNode()
            sage: n3.add_child(n4)
            sage: n5 = _TedderTreeNode()
            sage: n1.add_child(n5)
            sage: n1
            {{}, {{}}, {}}
            sage: n3.remove()
            sage: n1
            {{}, {}}
            sage: n3
            {{}}
        """
        if self.parent is not None:
            # The parent has one less child
            self.parent.num_children -= 1

        # Fix the pointers of the siblings/parent of this node
        if self.left_sibling is not None:
            self.left_sibling.right_sibling = self.right_sibling
        if self.right_sibling is not None:
            self.right_sibling.left_sibling = self.left_sibling
        if self.parent is not None and self.parent.first_child == self:
            self.parent.first_child = self.right_sibling

        # Reset this node's sibling/parent pointers to None, as it is no longer 
        # connected to them
        self.parent = None
        self.left_sibling = None
        self.right_sibling = None

    def insert_before(self, just_before):
        """
        Insert the subtree rooted at this node as the left sibling of the 
        supplied node (``just_before``), after removing it from where it is 
        currently
        
        INPUT:
        
        - ``just_before`` -- _TedderTreeNode

        EXAMPLES:

        Using _TedderMDLeafNodes to distinguish between nodes::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode, _TedderMDLeafNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderMDLeafNode(1)
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDLeafNode(2)
            sage: n1.add_child(n3)
            sage: n1
            {2, 1}
            sage: n4 = _TedderMDLeafNode(3)
            sage: n4.insert_before(n2)
            sage: n1
            {2, 3, 1}
        """
        # Remove this node from where it is
        self.remove()

        # Fix the sibling pointers
        self.left_sibling = just_before.left_sibling
        if just_before.left_sibling is not None:
            just_before.left_sibling.right_sibling = self
        self.right_sibling = just_before
        just_before.left_sibling = self

        # Fix the parent pointers
        self.parent = just_before.parent
        if just_before.parent is not None:
            # The parent now has one more child, and this node is now the 
            # leftmost child if ``just_before`` was the leftmost child.
            just_before.parent.num_children += 1
            if just_before.parent.first_child == just_before:
                self.parent.first_child = self

    def insert_after(self, just_after):
        """
        Insert the subtree rooted at this node as the right sibling of 
        the supplied node (``just_after``)
        
        INPUT:
        
        - ``just_after`` -- _TedderTreeNode

        EXAMPLES:

        Using _TedderMDLeafNodes to distinguish between nodes::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode, _TedderMDLeafNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderMDLeafNode(1)
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDLeafNode(2)
            sage: n1.add_child(n3)
            sage: n4 = _TedderMDLeafNode(3)
            sage: n4.insert_after(n3)
            sage: n1
            {2, 3, 1}
        """
        # Remove this node from where it is
        self.remove()

        # Fix the sibling pointers
        self.right_sibling = just_after.right_sibling
        if just_after.right_sibling is not None:
            just_after.right_sibling.left_sibling = self
        self.left_sibling = just_after
        just_after.right_sibling = self

        # Fix the parent pointers
        self.parent = just_after.parent
        if just_after.parent is not None:
            # The parent now has one more child
            just_after.parent.num_children += 1
    
    def make_first_child(self):
        """
        Moves the subrree rooted at this node to be the first child of it's 
        parent

        EXAMPLES:

        Using _TedderMDLeafNodes to distinguish between nodes::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode, _TedderMDLeafNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderMDLeafNode(1)
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDLeafNode(2)
            sage: n1.add_child(n3)
            sage: n1
            {2, 1}
            sage: n2.make_first_child()
            sage: n1
            {1, 2}
        """
        if self.parent is not None and self.parent.first_child != self:
            new_right_sibling = self.parent.first_child
            # Remove this node from where it is
            self.remove()

            # Insert it to the left of the current first child, to make 
            # it the new first child.
            self.insert_before(new_right_sibling)
    
    def get_leaves(self):
        """
        Returns a list of the leaves of the subtree rooted at this node. The 
        leaves in this case refers to the _TedderMDLeafNode's present in the 
        tree.

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode, _TedderMDLeafNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDLeafNode(1)
            sage: n2.add_child(n3)
            sage: n4 = _TedderMDLeafNode(2)
            sage: n1.add_child(n4)
            sage: n5 = _TedderMDLeafNode(3)
            sage: n1.add_child(n5)
            sage: n1
            {3, 2, {1}}
            sage: n1.get_leaves()
            [3, 2, 1]
        """
        if isinstance(self, _TedderMDLeafNode):
            """
            If this is a _TedderMDLeafNode, the list of leaves is just the 
            singleton list of this node, as _TedderMDLeafNodes shouldn't have 
            any children
            """
            leaves = [self]
        else:
            """
            This node isn't a _TedderMDLeafNode, so the list of leaves is 
            just the union of the list of leaves of this node's children's 
            subtree.
            """
            leaves = []
            current_child = self.first_child
            while current_child is not None:
                leaves += current_child.get_leaves()
                current_child = current_child.right_sibling

        return leaves
    
    def add_children_from(self, parent):
        """
        Adds the children of the supplied node (``parent``) as children to this 
        node
        
        INPUT:
        
        - ``parent`` -- _TedderTreeNode

        EXAMPLES:
        
            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderTreeNode()
            sage: n1.add_child(n3)
            sage: n1
            {{}, {}}
            sage: n4 = _TedderTreeNode()
            sage: n5 = _TedderTreeNode()
            sage: n4.add_child(n5)
            sage: n4
            {{}}
            sage: n4.add_children_from(n1)
            sage: n1
            {}
            sage: n4
            {{}, {}, {}}
        """
        current_child = parent.first_child
        while current_child is not None:
            next_child = current_child.right_sibling
            self.add_child(current_child)
            current_child = next_child
    
    def replace_this_by_its_children(self):
        """
        Removes just this node of the tree, the children of this node become 
        children of this node's parent

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderTreeNode()
            sage: n2.add_child(n3)
            sage: n4 = _TedderTreeNode()
            sage: n2.add_child(n4)
            sage: n5 = _TedderTreeNode()
            sage: n1.add_child(n5)
            sage: n1
            {{}, {{}, {}}}
            sage: n2.replace_this_by_its_children()
            sage: n1
            {{}, {}, {}}
        """
        current_child = self.first_child
        while current_child is not None:
            next_child = current_child.right_sibling
            current_child.insert_before(self)
            current_child = next_child
        self.remove()
    
    def replace_children_with(self, replacement):
        """
        Replaces the children of this node with the node supplied 
        (``replacement``)
        
        INPUT:
        
        - ``replacement`` -- _TedderTreeNode

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderTreeNode()
            sage: n1.add_child(n3)
            sage: n1
            {{}, {}}
            sage: n4 = _TedderTreeNode()
            sage: n5 = _TedderTreeNode()
            sage: n4.add_child(n5)
            sage: n4
            {{}}
            sage: n1.replace_children_with(n4)
            sage: n1
            {{{}}}
        """
        current_child = self.first_child
        while current_child is not None:
            next_child = current_child.right_sibling
            # Remove each of this node's children from where they are
            current_child.remove()
            current_child = next_child

        # Add the new node as the only child of this node.
        self.add_child(replacement)
    
    def is_root(self):
        """
        Returns True if this node is the root
        For the general node, this means if it has no parent, but will be 
        overridden for subclasses

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode
            sage: n1 = _TedderTreeNode()
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n1.is_root()
            True
            sage: n2.is_root()
            False
        """
        return self.parent is None

    def __repr__(self):
        """
        Returns the string representation of this node.
        _TedderTreeNodes don't have any sort of 'value', so the string 
        representation is just a list of the representations of this 
        node's children, separated by commas, and surrounded by {}, to 
        distinguish it from its subclasses.
        This will be overridden by all of the subclasses, for more useful 
        representaitons.

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderTreeNode
            sage: n1 = _TedderTreeNode()
            sage: str(n1)
            '{}'
            sage: n2 = _TedderTreeNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderTreeNode()
            sage: n2.add_child(n3)
            sage: n4 = _TedderTreeNode()
            sage: n1.add_child(n4)
            sage: str(n1)
            '{{}, {{}}}'
        """
        result = "{"
        current_child = self.first_child
        if current_child is not None:
            result += str(current_child)
            current_child = current_child.right_sibling
        while current_child is not None:
            result += ", " + str(current_child)
            current_child = current_child.right_sibling
        return result + "}"

class _TedderMDNode(_TedderTreeNode):
    """
    The class of nodes in the MD tree for the Tedder algorithm.
    This class performs a similar function as the Node class for MD trees, and
    can be converted to the Node class using the function to_node.
    This class, however, inherits from _TedderTreeNode for the operations on 
    trees needed for the Tedder algorithm.
    These nodes, along with the Node Type and Split Type, store a comp_number 
    and tree_number, which are used in the Tedder algorithm
    The nodes also have a num_marks attribute, which is used to distinguish 
    between certain types of nodes at various points in the Tedder algorithm.
    The class _TedderMDLeafNode will inherit from this class, and represent 
    the leaf nodes of the MD trees.
    """

    def __init__(self, node_type = NodeType.PRIME):
        """
        INPUT:
        
        - ``node_type`` -- NodeType, default PRIME
        """
        # Initialise the node using the superclass _TedderTreeNode __init__ 
        # method
        _TedderTreeNode.__init__(self)
        self.type = node_type
        """
        - ``type`` -- NodeType, the type of the node, PRIME, PARALLEL, SERIAL, 
        or NORMAL, but should only be NORMAL if the node is a _TedderMDLeafNode
        """
        self.comp_number = -1
        # - ``comp_number`` -- Integer, this node's component or co-component 
        # number
        self.tree_number = -1
        # - ``tree_number`` -- Integer, the number of the tree this node is in, 
        # relative to the current subproblem being solved
        self.num_marks = 0
        # - ``num_marks`` -- Integer, the number of marks this node has
        self.split_type = NodeSplit.NO_SPLIT
        # - ``split_type`` -- NodeSplit, the type of split this node has, 
        # NO_SPLIT, LEFT_SPLIT, RIGHT_SPLIT or BOTH_SPLIT
    
    def copy(self, copy):
        """
        Receives the value of the supplied node's (``copy``) fields, but
        none of it's children

        INPUT:
        
        - ``copy`` -- _TedderMDNode, the node whose fields are being copied

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeType
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n1.comp_number = 1
            sage: n1
            (PRIME: (PRIME: ))
            sage: n3 = _TedderMDNode(NodeType.PARALLEL)
            sage: n3
            (PARALLEL: )
            sage: n3.comp_number
            -1
            sage: n3.copy(n1)
            sage: n3
            (PRIME: )
            sage: n3.comp_number
            1
        """
        self.type = copy.type
        self.comp_number = copy.comp_number
        self.tree_number = copy.tree_number
        self.num_marks = copy.num_marks
        self.split_type = copy.split_type

    def to_node(self):
        """
        Convert this node's subtree into Node class elements

        OUTPUT:

        the equivalent Node element for this node's subtree.

        EXAMPLES:

        Example with just _TedderMDNodes::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeType
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode(NodeType.PARALLEL)
            sage: n1.add_child(n2)
            sage: n1
            (PRIME: (PARALLEL: ))
            sage: n1.to_node()
            PRIME [PARALLEL []]

        Example with _TedderMDLeafNodes::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, _TedderMDLeafNode
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDLeafNode(1)
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDLeafNode(2)
            sage: n1.add_child(n3)
            sage: n1
            (PRIME: 2, 1)
            sage: n1.to_node()
            PRIME [NORMAL [2], NORMAL [1]]
        """
        if isinstance(self, _TedderMDLeafNode):
            node = create_normal_node(self.vertex)
        else:
            # It's not a leaf node, so it has children
            node = Node(self.type)
            current_child = self.first_child
            while current_child is not None:
                node.children.append(current_child.to_node())
                current_child = current_child.right_sibling
        return node

    def is_fully_marked(self):
        """
        Returns True if the number of marks this node has is equal to the 
        number of it's children, and False otherwise

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode
            sage: n1 = _TedderMDNode()
            sage: n1.is_fully_marked()
            True
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n1.is_fully_marked()
            False
            sage: n1.num_marks = 1
            sage: n1.is_fully_marked()
            True
        """
        return self.num_marks == self.num_children
    
    def clear_marks(self):
        """
        Resets the number of marks this node has to 0

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode
            sage: n1 = _TedderMDNode()
            sage: n1.num_marks = 1
            sage: n1.clear_marks()
            sage: n1.num_marks
            0
        """
        self.num_marks = 0
    
    def is_marked(self):
        """
        Returns True if this node has at least one mark, and False otherwise

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode
            sage: n1 = _TedderMDNode()
            sage: n1.is_marked()
            False
            sage: n1.num_marks = 1
            sage: n1.is_marked()
            True
        """
        return self.num_marks > 0

    def set_comp_number_for_subtree(self, comp_number):
        """
        Sets the comp_number of all nodes in this node's subtree to the 
        supplied value (``comp_number``)

        INPUT:
        
        - ``comp_number`` -- integer

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n2.add_child(n3)
            sage: n1
            (PRIME: (PRIME: (PRIME: )))
            sage: n1.set_comp_number_for_subtree(1)
            sage: n1.comp_number
            1
            sage: n2.comp_number
            1
            sage: n3.comp_number
            1
        """
        self.comp_number = comp_number
        current_child = self.first_child
        while current_child is not None:
            current_child.set_comp_number_for_subtree(comp_number)
            current_child = current_child.right_sibling
        
    def set_tree_number_for_subtree(self, tree_number):
        """
        Sets the tree_number of all nodes in this node's subtree to the 
        supplied value (``tree_number``)
        
        INPUT:
        
        - ``tree_number`` -- integer

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n2.add_child(n3)
            sage: n1
            (PRIME: (PRIME: (PRIME: )))
            sage: n1.set_tree_number_for_subtree(1)
            sage: n1.tree_number
            1
            sage: n2.tree_number
            1
            sage: n3.tree_number
            1
        """
        self.tree_number = tree_number
        current_child = self.first_child
        while current_child is not None:
            current_child.set_tree_number_for_subtree(tree_number)
            current_child = current_child.right_sibling

    def number_comps(self, comp_number, by_type):
        """
        Starting with the supplied number (comp_number), incrementally numbers
        the nodes in this subtree rooted at this node according to either the
        component or the co-component they reside in, storing the number in the 
        node's 'comp_number' field. 
        If the supplied type (by_type) is parallel, and this node is labelled 
        parallel,then the subtrees defined by its children are numbered 
        incrementally starting with the supplied number, with all nodes in each 
        subtree having their ``comp_number`` set to the number assigned to that 
        tree. If this node is not labelled series, then all nodes in this 
        node's subtree have their ``comp_number`` set to the supplied number.
        Symmetrically for when the supplied type is series

        INPUT:

        - ``comp_number`` -- integer
        
        - ``by_type`` -- NodeType

        OUTPUT:

        The number of components counted

        EXAMPLES:

        ``by-type`` same as type of node::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeType
            sage: n1 = _TedderMDNode(NodeType.SERIES)
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n2.add_child(n3)
            sage: n4 = _TedderMDNode()
            sage: n1.add_child(n4)
            sage: n1
            (SERIES: (PRIME: ), (PRIME: (PRIME: )))
            sage: n1.number_comps(2, NodeType.SERIES)
            2
            sage: n2.comp_number
            3
            sage: n3.comp_number
            3
            sage: n4.comp_number
            2
        
        ``by-type`` different from type of node::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeType
            sage: n1 = _TedderMDNode(NodeType.SERIES)
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n2.add_child(n3)
            sage: n4 = _TedderMDNode()
            sage: n1.add_child(n4)
            sage: n1
            (SERIES: (PRIME: ), (PRIME: (PRIME: )))
            sage: n1.number_comps(2, NodeType.PARALLEL)
            0
            sage: n2.comp_number
            2
            sage: n3.comp_number
            2
            sage: n4.comp_number
            2
        """

        # Store the original comp_number, to find the number of components 
        # counted
        orig_comp_number = comp_number
        if self.type == by_type:
            """
            Number the subtrees' comp_number incrementally starting with 
            ``comp_number``
            """
            current_child = self.first_child
            while current_child is not None:
                current_child.set_comp_number_for_subtree(comp_number)
                current_child = current_child.right_sibling
                comp_number += 1
        else:
            """
            Set the comp_number for all nodes in the subtree rooted at this 
            node to ``comp_number``
            """
            self.set_comp_number_for_subtree(comp_number)
        # Return the number of components counted
        return comp_number - orig_comp_number

    def mark_ancestors_by_split(self, split_type):
        """
        Adds the given split mark to all of this node's ancestors.
        If one of those ancestors is marked by the other split mark, instead 
        it is marked with BOTH_SPLIT.
        If one of those ancestors is prime, it's children are marked with the
        split mark.

        INPUT:
        
        - ``split_type`` -- NodeSplit, LEFT_SPLIT or RIGHT_SPLIT

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n1.add_child(n3)
            sage: n4 = _TedderMDNode()
            sage: n2.add_child(n4)
            sage: n1
            (PRIME: (PRIME: ), (PRIME: (PRIME: )))
            sage: n1.split_type = NodeSplit.LEFT_SPLIT
            sage: n2.split_type = NodeSplit.RIGHT_SPLIT
            sage: n4.mark_ancestors_by_split(NodeSplit.LEFT_SPLIT)
            sage: n1.split_type
            <NodeSplit.LEFT_SPLIT: 1>
            sage: n2.split_type
            <NodeSplit.BOTH_SPLIT: 3>
            sage: n3.split_type
            <NodeSplit.LEFT_SPLIT: 1>
        """
        if not self.is_root():
            """
            As this node is not a root, it has a parent, which is a 
            _TedderMDNode
            """
            assert(self.parent is not None)
            parent = self.parent
            parent.add_split_mark(split_type)
            parent.mark_ancestors_by_split(split_type)

    def mark_children_by_split(self, split_type):
        """
        Adds the given split mark to all of this node's children.
        If one of those children is already with the other split type, instead
        it is marked with BOTH_SPLIT.
        If one of the children is prime, they're children are recursively marked
        with the split.
        
        INPUT:
        
        - ``split_type`` -- NodeSplit, LEFT_SPLIT or RIGHT_SPLIT

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n1.add_child(n3)
            sage: n4 = _TedderMDNode()
            sage: n2.add_child(n4)
            sage: n1
            (PRIME: (PRIME: ), (PRIME: (PRIME: )))
            sage: n3.split_type = NodeSplit.LEFT_SPLIT
            sage: n2.split_type = NodeSplit.RIGHT_SPLIT
            sage: n1.mark_children_by_split(NodeSplit.LEFT_SPLIT)
            sage: n3.split_type
            <NodeSplit.LEFT_SPLIT: 1>
            sage: n2.split_type
            <NodeSplit.BOTH_SPLIT: 3>
            sage: n4.split_type
            <NodeSplit.LEFT_SPLIT: 1>
        """
        current_child = self.first_child
        while current_child is not None:
            current_child.add_split_mark(split_type)
            current_child = current_child.right_sibling

    def add_split_mark(self, split_type):
        """
        Adds the given mark (``split_type``) to this node. If this node has 
        already been marked by this type, then nothing happens. If the node 
        already has a different mark it is marked as BOTH_SPLIT. If the node is 
        prime, then the node's children are recursively marked by the supplied 
        type.
        
        INPUT:
        
        - ``split_type`` -- NodeSplit, LEFT_SPLIT or RIGHT_SPLIT

        EXAMPLES:

        Unmarked nodes marked with the split type::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n1.add_split_mark(NodeSplit.LEFT_SPLIT)
            sage: n1.split_type
            <NodeSplit.LEFT_SPLIT: 1>

        Nodes marked with the same split type are left unchanged::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n1.split_type = NodeSplit.LEFT_SPLIT
            sage: n1.add_split_mark(NodeSplit.LEFT_SPLIT)
            sage: n1.split_type
            <NodeSplit.LEFT_SPLIT: 1>

        Nodes marked with the other split type are marked with BOTH_SPLIT::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n1.split_type = NodeSplit.LEFT_SPLIT
            sage: n1.add_split_mark(NodeSplit.RIGHT_SPLIT)
            sage: n1.split_type
            <NodeSplit.BOTH_SPLIT: 3>

        If the node is prime, its children are recursively marked::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeSplit, NodeType
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n2.add_child(n3)
            sage: n4 = _TedderMDNode(NodeType.SERIES)
            sage: n1.add_child(n4)
            sage: n5 = _TedderMDNode()
            sage: n4.add_child(n5)
            sage: n1
            (PRIME: (SERIES: (PRIME: )), (PRIME: (PRIME: )))
            sage: n1.add_split_mark(NodeSplit.LEFT_SPLIT)
            sage: n3.split_type
            <NodeSplit.LEFT_SPLIT: 1>
            sage: n5.split_type
            <NodeSplit.NO_SPLIT: 0>
        """
        if self.split_type != split_type:
            """
            If self.split_type is NO_SPLIT, this node hasn't been marked, so it 
            can be marked with ``split_type`` as normal. If it is BOTH_SPLIT, 
            or the other split type (i.e. LEFT_SPLIT if ``split_type`` is 
            RIGHT_SPLIT), then it either has already been marked by both split 
            types, or is now marked by both split types, so should be marked as 
            BOTH_SPLIT
            """
            if self.split_type == NodeSplit.NO_SPLIT:
                self.split_type = split_type
            else:
                self.split_type = NodeSplit.BOTH_SPLIT
        """
        If self.split_type is equal to ``split_type``, no extra mark needs to 
        be added
        """
        if self.type == NodeType.PRIME:
            """
            If this node has a PRIME type, all this node's children also need 
            to be marked with ``split_type``
            """
            self.mark_children_by_split(split_type)
    
    def is_split_marked(self, split_type):
        """
        Returns True if this node has been marked by the supplied type 
        (``split_type``) of split, and False otherwise.
        This is the case if either self.split_type is equal to ``split_type``, 
        or is BOTH_SPLIT, as it has then been marked by both types of split.
        
        INPUT:
        
        - ``split_type`` -- NodeSplit, LEFT_SPLIT or RIGHT_SPLIT

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n1.add_split_mark(NodeSplit.LEFT_SPLIT)
            sage: n1.is_split_marked(NodeSplit.LEFT_SPLIT)
            True
            sage: n1.add_split_mark(NodeSplit.RIGHT_SPLIT)
            sage: n1.is_split_marked(NodeSplit.LEFT_SPLIT)
            True
        """
        return self.split_type == NodeSplit.BOTH_SPLIT or self.split_type == split_type

    def clear_split_marks_for_subtree(self):
        """
        Sets the split marks for all nodes in this node's subtree to NO_SPLIT

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n2.add_child(n3)
            sage: n1.split_type = NodeSplit.LEFT_SPLIT
            sage: n3.split_type = NodeSplit.BOTH_SPLIT
            sage: n1.clear_split_marks_for_subtree()
            sage: n1.split_type
            <NodeSplit.NO_SPLIT: 0>
            sage: n3.split_type
            <NodeSplit.NO_SPLIT: 0>
        """
        self.split_type = NodeSplit.NO_SPLIT
        current_child = self.first_child
        while (current_child is not None):
            current_child.clear_split_marks_for_subtree()
            current_child = current_child.right_sibling

    def promote(self, split_type):
        """
        Promotes to depth-0 (this node's level) all nodes in this node's subtree 
        labelled by the supplied type (split_type). 
        If the split type is LEFT_SPLIT, then nodes are promoted to the left of 
        their parent. If the split type is RIGHT_SPLIT, then nodes are promoted 
        to the right of their parent.
        If, after promoting these nodes, any non-leaf nodes are found to have 
        no children, or only a single child, then these nodes are deleted, and 
        in the latter case, replaced by their only child. 

        INPUT:
        
        - ``split_type`` -- NodeSplit, LEFT_SPLIT or RIGHT_SPLIT
        
        PRECONDITION:
        
        If node x is marked by split_type t, then all of x's ancestors are
        marked by t.

        EXAMPLES:

        Promoting with LEFT_SPLIT promotes nodes marked with LEFT_SPLIT to the
        left of their parents, recursively, until they are depth-0, and leaves
        nodes marked with RIGHT_SPLIT or NO_SPLIT alone::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, _TedderMDLeafNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDLeafNode(1)
            sage: n2.add_child(n3)
            sage: n4 = _TedderMDLeafNode(2)
            sage: n2.add_child(n4)
            sage: n5 = _TedderMDLeafNode(3)
            sage: n2.add_child(n5)
            sage: n1
            (PRIME: (PRIME: 3, 2, 1))
            sage: n3.split_type = NodeSplit.LEFT_SPLIT
            sage: n4.split_type = NodeSplit.RIGHT_SPLIT
            sage: n5.split_type = NodeSplit.NO_SPLIT
            sage: n2.split_type = NodeSplit.BOTH_SPLIT
            sage: n1.split_type = NodeSplit.BOTH_SPLIT
            sage: n2.promote(NodeSplit.LEFT_SPLIT)
            sage: n1
            (PRIME: 1, (PRIME: 3, 2))

        Symmetrically for RIGHT_SPLIT::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, _TedderMDLeafNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDLeafNode(1)
            sage: n2.add_child(n3)
            sage: n4 = _TedderMDLeafNode(2)
            sage: n2.add_child(n4)
            sage: n5 = _TedderMDLeafNode(3)
            sage: n2.add_child(n5)
            sage: n1
            (PRIME: (PRIME: 3, 2, 1))
            sage: n3.split_type = NodeSplit.LEFT_SPLIT
            sage: n4.split_type = NodeSplit.RIGHT_SPLIT
            sage: n5.split_type = NodeSplit.NO_SPLIT
            sage: n2.split_type = NodeSplit.BOTH_SPLIT
            sage: n1.split_type = NodeSplit.BOTH_SPLIT
            sage: n2.promote(NodeSplit.RIGHT_SPLIT)
            sage: n1
            (PRIME: (PRIME: 3, 1), 2)

        Nodes left with one child replaced by the child, and nodes without 
        children removed::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, _TedderMDLeafNode, NodeSplit
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n2.add_child(n3)
            sage: n4 = _TedderMDLeafNode(1)
            sage: n3.add_child(n4)
            sage: n5 = _TedderMDNode()
            sage: n2.add_child(n5)
            sage: n6 = _TedderMDLeafNode(2)
            sage: n7 = _TedderMDLeafNode(3)
            sage: n5.add_child(n6)
            sage: n5.add_child(n7)
            sage: n1
            (PRIME: (PRIME: (PRIME: 3, 2), (PRIME: 1)))
            sage: n4.split_type = NodeSplit.LEFT_SPLIT
            sage: n6.split_type = NodeSplit.LEFT_SPLIT
            sage: n3.split_type = NodeSplit.LEFT_SPLIT
            sage: n5.split_type = NodeSplit.LEFT_SPLIT
            sage: n2.split_type = NodeSplit.LEFT_SPLIT
            sage: n1.split_type = NodeSplit.LEFT_SPLIT
            sage: n2.promote(NodeSplit.LEFT_SPLIT)
            sage: n1
            (PRIME: 2, 3, 1)

        """
        to_promote = self.first_child
        # Promote each child marked by the given type
        while to_promote is not None:
            next_to_promote = to_promote.right_sibling
            if to_promote.is_split_marked(split_type):
                if split_type == NodeSplit.LEFT_SPLIT:
                    # Promote the node to just to the left of it's parent
                    to_promote.insert_before(to_promote.parent)
                else:
                    # Promote the node to just to the right of it's parent
                    to_promote.insert_after(to_promote.parent)
                """
                Recursively promote in the subtree rooted at the node just 
                promoted
                """
                to_promote.promote(split_type)
            to_promote = next_to_promote
        if self.has_no_children() and not isinstance(self, _TedderMDLeafNode):
            """
            This node has no children, and isn't a leaf, so is a useless node 
            that can be deleted.
            """
            self.remove()
        elif self.has_only_one_child():
            """
            This node has only one child, so can safely be replaced by that 
            child
            """
            self.replace_with(self.first_child)

    def remove_degenerate_duplicates_from_subtree(self):
        """
        Removes consecutive degenerate nodes of the same type from this node's 
        subtree Degenerate nodes are those with node type PARALLEL or SERIAL

        EXAMPLES:

        Consecutive degenerate nodes are merged::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeType
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode(NodeType.SERIES)
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode(NodeType.SERIES)
            sage: n2.add_child(n3)
            sage: n4 = _TedderMDNode(NodeType.PARALLEL)
            sage: n1.add_child(n4)
            sage: n5 = _TedderMDNode(NodeType.PARALLEL)
            sage: n4.add_child(n5)
            sage: n1
            (PRIME: (PARALLEL: (PARALLEL: )), (SERIES: (SERIES: )))
            sage: n1.remove_degenerate_duplicates_from_subtree()
            sage: n1
            (PRIME: (PARALLEL: ), (SERIES: ))

        Alternating degenerate nodes are not merged::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeType
            sage: n1 = _TedderMDNode(NodeType.SERIES)
            sage: n2 = _TedderMDNode(NodeType.PARALLEL)
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode(NodeType.SERIES)
            sage: n2.add_child(n3)
            sage: n1
            (SERIES: (PARALLEL: (SERIES: )))
            sage: n1.remove_degenerate_duplicates_from_subtree()
            sage: n1
            (SERIES: (PARALLEL: (SERIES: )))
        """
        current_child = self.first_child
        while current_child is not None:
            next_child = current_child.right_sibling
            # Recursively remove the degenerate duplicates from the subtree
            current_child.remove_degenerate_duplicates_from_subtree()
            if current_child.type == self.type and self.type.is_degenerate():
                # Remove this node, as it can be subsumed by its parent
                self.add_children_from(current_child)
                current_child.remove()
            current_child = next_child
    
    def clear_all(self):
        """
        Resets to their defaults all properties of all nodes in this node's 
        subtree, except their type, which remains the same.

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeType
            sage: n1 = _TedderMDNode(NodeType.SERIES)
            sage: n2 = _TedderMDNode(NodeType.PARALLEL)
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: n2.add_child(n3)
            sage: n1
            (SERIES: (PARALLEL: (PRIME: )))
            sage: n1.num_marks = 2
            sage: n2.comp_number = 1
            sage: n3.tree_number = 0
            sage: n1.clear_all()
            sage: n1
            (SERIES: (PARALLEL: (PRIME: )))
            sage: n1.num_marks
            0
            sage: n2.comp_number
            -1
            sage: n3.tree_number
            -1
        """
        self.comp_number = -1
        self.tree_number = -1
        self.num_marks = 0
        self.split_type = NodeSplit.NO_SPLIT
        current_child = self.first_child
        while current_child is not None:
            """
            Recursively clears the property of the nodes in the children's 
            subtrees
            """
            current_child.clear_all()
            current_child = current_child.right_sibling
        
    def is_root(self):
        """
        Overridden method from _TedderTreeNode
        Returns True if this node is a root of an MD tree
        For these nodes, this is True if the parent of this node is NOT a 
        _TedderMDNode

        EXAMPLES:


            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, _TedderTreeNode
            sage: n1 = _TedderMDNode()
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n1.is_root()
            True
            sage: n2.is_root()
            False
            sage: n3 = _TedderTreeNode()
            sage: n3.add_child(n1)
            sage: n1.is_root()
            True    
        """
        if self.parent is None or not isinstance(self.parent, _TedderMDNode):
            return True
        else:
            return False

    def __repr__(self):
        """
        Overridden method from _TedderTreeNode
        Returns the string represetation of this node.
        The 'value' of this node is the node type of the node, so the 
        representation is the type of the node, followed by a list of the 
        representations of this node's children, separated by commas, surrounded 
        by () in order to distinguish it from the other classes inheriting from 
        _TedderTreeNode.
        This method will be overridden by _TedderMDLeafNode, as they have no 
        children and a different definition of `value` of the node.

        EXAMPLES:
        
            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDNode, NodeType
            sage: n1 = _TedderMDNode()
            sage: str(n1)
            '(PRIME: )'
            sage: n2 = _TedderMDNode(NodeType.PARALLEL)
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode(NodeType.SERIES)
            sage: n1.add_child(n3)
            sage: str(n1)
            '(PRIME: (SERIES: ), (PARALLEL: ))'
        """
        result = "(" + str(self.type) + ": "
        current = self.first_child
        if current is not None:
            result += str(current)
            current = current.right_sibling
        while current is not None:
            result += ", " + str(current)
            current = current.right_sibling
        return result + ")"

class _TedderMDLeafNode(_TedderMDNode):
    """
    This is the class of leaf nodes in the MD trees used in the Tedder algorithm.
    These node's have no children, and each is related to a vertex in the graph 
    that the Tedder algorithm is computed the MD tree of.
    The node also stores the _TedderMDLeafNode related to the neighbours of this
    node's vertex in its graph, as well as a list of _TedderMDLeafNodes called 
    its alpha-list that is used throughout the Tedder algorithm.
    Finally these nodes store a visited field, which is set to True once this 
    node is used as pivot, and stays True throughout the algorithm
    """
    def __init__(self, vertex = None):
        """
        INPUT:
        
        - ``vertex`` -- the graph vertex that this node represents
        """
        # Initialise the node using the superclass _TedderMDNode __init__ method
        _TedderMDNode.__init__(self)
        self.type = NodeType.NORMAL
        # MD Leaf Nodes are the NORMAL nodes of the MD Tree.
        self.alpha = []
        """
        - ``alpha`` -- List of _TedderMDLeafNodes, the alpha-list of this 
        vertex
        """
        self.neighbors = [] 
        """
        - ``neighbors`` -- List of _TedderMDLeafNodes, the neighours of this 
        vertex in the graph
        """
        self.visited = False
        """
        - ``visited`` -- Boolean, True if this node has been the pivot in the 
        algorithm, and False otherwise
        """
        self.vertex = vertex
        """
        - ``vertex`` -- vertex, the vertex this node is related to in the 
        graph
        """

    def clear_alpha(self):
        """
        Resets alpha to []

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDLeafNode
            sage: n1 = _TedderMDLeafNode()
            sage: n1.alpha = [n1]
            sage: n1.clear_alpha()
            sage: n1.alpha
            []
        """
        self.alpha = []

    def replace_alpha(self, new_alpha):
        """
        Replaces this node's alpha list with the supplied list (``new_alpha``)
        
        INPUT:
        
        - ``new_alpha`` -- list of _TedderMDLeafNodes

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDLeafNode
            sage: n1 = _TedderMDLeafNode()
            sage: n1.alpha = [1]
            sage: n1.replace_alpha([2])
            sage: n1.alpha
            [2]
        """
        self.alpha = new_alpha

    def clear_all(self):
        """
        Overridden method from _TedderMDNode
        Resets to their defaults all properties of this node, except it's 
        'visited' field, which remains the same. The only property other than 
        the ones inherited from _TedderMDNode that needs to be reset is the 
        alpha-list of this node.

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDLeafNode, NodeSplit
            sage: n1 = _TedderMDLeafNode()
            sage: n1.split_type = NodeSplit.LEFT_SPLIT
            sage: n1.alpha = [1]
            sage: n1.clear_all()
            sage: n1.split_type
            <NodeSplit.NO_SPLIT: 0>
            sage: n1.alpha
            []
        """
        _TedderMDNode.clear_all(self)
        self.alpha = []
    
    def __repr__(self):
        """
        Overridden method from _TedderMDNode
        Returns the string representation of this node.
        The 'value' of this node is the representation of the vertex it is 
        related to.
        This node will have no children, so that is all that is needed for the
        representation of the node.

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderMDLeafNode, NodeSplit, NodeType
            sage: n1 = _TedderMDLeafNode(1)
            sage: n1.alpha = [1]
            sage: n1.split_type = NodeSplit.LEFT_SPLIT
            sage: n1.type = NodeType.SERIES
            sage: str(n1)
            '1'
        """
        return str(self.vertex)

class _TedderFactPermElement(_TedderTreeNode):
    """
    This is the class of factorising permutation elements used in the Tedder 
    Algorithm.
    The Tedder algorithm uses these to form factorising permutations where the 
    strong modules in the graph are stored consecutively.
    A factorising permutation will either have an index of -1, in which case it 
    is a trivial element that is used as a separator, or it will have an index 
    >= 0, in which case it is associated with an MD tree, the root of which will 
    be its first (and only) child.
    A factorising permutation element also has a mu-value. For details on what 
    the mu-value of a factorising permutation element is, see [TCHP2008]_
    A factorising permutation also can have one or more marks, which are used to 
    distinguish between certain elements in the algorithm, and flags for whether 
    or not they have certain connections to the left and right elements.
    Finally, an element stores the neighbours it has.
    If a vertex in this elements MD tree has an edge to a vertex in the MD tree 
    of another element, we say this element has an edge to that element.
    This element is a neighbour of another element if this element has an edge 
    to that element, and that element is on the other side of the pivot to this 
    element.
    """
    
    def __init__(self, index = -1):
        """
        INPUT:
        
        - ``index`` -- integer
        """
        # Initialise the element using the superclass _TedderTreeNode __init__
        _TedderTreeNode.__init__(self)
        self.index = index
        # - ``index`` -- Integer, the index of the element (see above).
        self.mu = None
        # - ``mu`` -- Integer, the mu value of the element (see [TCHP2008]_).
        self.has_right_comp_fragment = False
        """
        - ``has_right_comp_fragment`` -- Boolean. True if this element is part 
        of the same component as the element to its right, and False otherwise.
        """
        self.has_left_co_comp_fragment = False
        """
        - ``has_left_co_comp_fragment`` -- Boolean, True if this element is part 
        of the same co-component as the element to its left, and False otherwise.
        """
        self.has_right_layer_neighbor = False
        """
        - ``has_right_layer_neighbor`` -- Boolean, True if this element has an 
        edge to the element to its right, and False otherwise.
        """
        self.num_marks = 0
        # - ``num_marks`` -- Integer, the number of marks this element has.
        self.neighbors = []
        # - ``neighbors`` -- List of _TedderFactPermElements, the neighbours of 
        # this element (see above)

    def is_marked(self):
        """
        Returns True if the element has been marked

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderFactPermElement
            sage: n1 = _TedderFactPermElement()
            sage: n1.is_marked()
            False
            sage: n1.num_marks += 1
            sage: n1.is_marked()
            True
        """
        return self.num_marks > 0

    def clear_marks(self):
        """
        Resets the marks to their default value (0)
        
        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderFactPermElement
            sage: n1 = _TedderFactPermElement()
            sage: n1.num_marks = 2
            sage: n1.clear_marks()
            sage: n1.num_marks
            0
        """
        self.num_marks = 0

    def replace_neighbors(self, new_neighbors):
        """
        Replaces this element's neighbors with the supplied list 
        (``new_neighbors``)
        
        INPUT:
        
        - ``new_neighbors`` -- List of _TedderFactPermElements

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderFactPermElement
            sage: n1 = _TedderFactPermElement()
            sage: n1.neighbors = [1]
            sage: n1.replace_neighbors([2])
            sage: n1.neighbors
            [2]
        """
        self.neighbors = new_neighbors

    def __repr__(self):
        """
        Overridden from _TedderTreeNode
        Returns the string representation of this element. 
        The 'value' of this element is simply its index
        To make things clearer, if this element is trivial (its index is -1), we 
        don't show it, simply leaving it blank. 
        As the non-trivial elements of the factorising permutation will only have 
        one child, the root of its MD tree, and the MD tree doesn't really matter 
        to the operations surrounding factorising permutation elements, these are 
        not shown in the representation. To make things clear, the representation 
        of the element is preceded by |. This means if the element is trivial, 
        its representation will simply be |, if it isn't, its representation
        will be |Index=i, where i is the index of the node.

        EXAMPLES:

        If the element's index is not -1::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderFactPermElement
            sage: n1 = _TedderFactPermElement(1)
            sage: n1.neighbors = [1]
            sage: n1.num_marks = 2
            sage: str(n1)
            '|Index=1'

        If the element's index is -1, representation is just |::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderFactPermElement
            sage: n1 = _TedderFactPermElement()
            sage: n1.neighbors = [1]
            sage: n1.num_marks = 2
            sage: str(n1)
            '|'
        """
        result = "|"
        if self.index != -1:
            result += "Index=" + str(self.index)
        return result

class _TedderSubProblem(_TedderTreeNode):
    """
    This is the class of recursive subproblems used in the Tedder Algorithm.
    The children of these nodes will have a different class depending on the
    point in the algorithm. They could, at times, be _TedderMDNodes (or 
    _TedderMDLeafNodes), _TedderFactPermElements, or _TedderSubProblems.
    Comments have been added to ensure that it is clear what class the children
    are at any time.
    These nodes also store the pivot of the subproblem, which is an element 
    chosen arbitrarily from the subproblems graph. An element should only ever be 
    the pivot of a subproblem once.
    It also stores whether or not this subproblem is a currently active 
    subproblem, or a subproblem waiting to be solved, and whether or not the 
    vertices in this subproblem are connected to the pivot of its parent.
    A subproblem represents a graph, and 'solving' the subproblem returns the MD
    tree of the graph represented by the subproblem.
    The build_graph function converts this subproblem into the 'unsolved' 
    subproblem representing the graph, and the solve function then solves this 
    subproblem, returning a _TedderMDNode that is the root of the MD tree of the 
    graph.
    """

    def __init__(self, leaf = None):
        """
        INPUT:
        
        - ``leaf`` -- _TedderMDLeafNode, if this is not None, initialise the node 
        to start with this as a child.
        """
        # Initialise the element using the superclass _TedderTreeNode __init__
        _TedderTreeNode.__init__(self)
        self.connected = False
        """
        - ``connected`` -- Boolean, True if this nodes vertices are connected to 
        the pivot of this node's parent, and False otherwse.
        """
        self.active = False
        # - ``active`` -- Boolean, True if this node is currently being solved,
        # and False otherwse
        self.pivot = None
        # - ``pivot`` -- _TedderMDLeafNode, the pivot vertex of this problem
        if leaf is not None:
            # Subproblem initialised with one child, ``leaf``
            self.add_child(leaf)

    def copy(self, copy):
        """
        Copies the field values of the supplied problem (copy), but not any of 
        it's children
        
        INPUT:
        
        - ``copy`` -- _TedderSubProblem

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderSubProblem
            sage: p1 = _TedderSubProblem()
            sage: p1.connected = False
            sage: p1.active = True
            sage: p2 = _TedderSubProblem()
            sage: p3 = _TedderSubProblem()
            sage: p2.add_child(p3)
            sage: p2
            [[]]
            sage: p2.connected = True
            sage: p1.copy(p2)
            sage: p1.connected
            True
            sage: p1.active
            False
            sage: p1.first_child
        """
        self.connected = copy.connected
        self.active = copy.active
        self.pivot = copy.pivot

    def clear_attributes(self):
        """
        Resets the fields of this problem to their default values

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderSubProblem
            sage: p1 = _TedderSubProblem()
            sage: p1.active = True
            sage: p1.pivot = 1
            sage: p1.clear_attributes()
            sage: p1.active
            False
            sage: p1.pivot
        """
        self.connected = False
        self.active = False
        self.pivot = None

    def clear_all_but_visited(self):
        """
        For all nodes in this sub-problems's MD tree, clears all fields except 
        'visited'

        PRECONDITION:

        This node has exactly one child, and its a _TedderMDNode
        """
        assert(self.has_only_one_child())
        self.first_child.clear_all()

    def clear_split_marks(self):
        """
        Removes all split marks from the nodes in this node's subtree

        PRECONDITION:

        This node's children are _TedderMDNodes

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderSubProblem, _TedderMDNode, NodeSplit
            sage: p = _TedderSubProblem()
            sage: n1 = _TedderMDNode()
            sage: p.add_child(n1)
            sage: n2 = _TedderMDNode()
            sage: n1.add_child(n2)
            sage: n3 = _TedderMDNode()
            sage: p.add_child(n3)
            sage: n1.split_type = NodeSplit.LEFT_SPLIT
            sage: n2.split_type = NodeSplit.BOTH_SPLIT
            sage: n3.split_type = NodeSplit.RIGHT_SPLIT
            sage: p.clear_split_marks()
            sage: n1.split_type
            <NodeSplit.NO_SPLIT: 0>
            sage: n2.split_type
            <NodeSplit.NO_SPLIT: 0>
            sage: n3.split_type
            <NodeSplit.NO_SPLIT: 0>      
        """
        current = self.first_child
        while current is not None:
            assert(isinstance(current, _TedderMDNode))
            next_node = current.right_sibling
            current.clear_split_marks_for_subtree()
            current = next_node

    def remove_degenerate_duplicates(self):
        """
        Removes consecutively appearing degenerate nodes of the same type in 
        this sub-problem's MD tree. 
        A node is degenerate if its type is degenerate, that is, SERIAL or
        PARALLEL

        PRECONDITION:

        This node has exactly one child, and that child is a _TedderMDNode

        EXAMPLE:
        """
        assert(self.has_only_one_child() and isinstance(self.first_child, _TedderMDNode))
        self.first_child.remove_degenerate_duplicates_from_subtree()

    def is_pivot_layer(self):
        """
        Returns True if this is the pivot subproblem, that is, the subproblem
        just containing the pivot of this node's parent's pivot.

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderSubProblem, _TedderMDLeafNode
            sage: p1 = _TedderSubProblem()
            sage: p2 = _TedderSubProblem()
            sage: p1.add_child(p2)
            sage: n = _TedderMDLeafNode(1)
            sage: p2.add_child(n)
            sage: p1
            [[1]]
            sage: p2.is_pivot_layer()
            False
            sage: p1.pivot = n
            sage: p1
            [PIVOT=[1]]
            sage: p2.is_pivot_layer()
            True
        """
        return (self.parent.pivot == self.first_child)

    def build_graph(self, graph):
        """
        Builds the subproblem from the given graph (graph), and adds the vertices 
        as children to this node
        
        INPUT:
        
        - ``graph`` -- the graph from which the subproblem will be build

        PRECONDITION:
        
        ``graph`` is undirected, and has at least one node.
        This node has no children.

        EXAMPLES:

           sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderSubProblem
            sage: d = {0:[], 1:[2], 2:[1]}
            sage: g = Graph(d)
            sage: problem = _TedderSubProblem()
            sage: problem.build_graph(g)
            sage: problem
            [2, 1, 0]
            sage: problem.first_child
            2
            sage: problem.first_child.neighbors
            [1] 
        """
        # Create the _TedderLeafNode for each vertex
        vertex_list = graph.vertices(sort=False)
        vertex_dictionary = {}
        """
        A dictionary 'vertex --> node', where 
        - 'vertex' is a vertex of the graph ``graph``, and
        - 'node' is the _TedderMDLeafNode associated with 'vertex'
        """
        for vertex in vertex_list:
            vertex_dictionary[vertex] = _TedderMDLeafNode(vertex)
    
        # Populate the nodes with the neighbors of their vertices, and add them 
        # to the subproblem
        for vertex in vertex_list:
            node = vertex_dictionary[vertex]
            neighbor_list = graph.neighbors(vertex)
            for neighbor in neighbor_list:
                node.neighbors.append(vertex_dictionary[neighbor])
            # Add vertex as a child
            self.add_child(node)

    def solve(self):
        """
        Compute the MD tree for this subproblem. The root of the MD tree becomes 
        the sole child of this subproblem
        
        OUTPUT:
        
        The root of the constructed MD tree

        PRECONDITION:

        The children of this node should be _TedderMDLeafNodes
        """
        # We are currently solving this subproblem
        self.active = True
        
        if self.has_only_one_child():
            """
            Subproblem (and thus MD tree) only contains a single node, so 
            nothing to do except process the pivot to refine the sub-problems in 
            the rest of the recursion tree
            """
            self.pivot = self.first_child
            self.process_neighbors(self.pivot)
            self.pivot.visited = True
            return self.first_child
        
        # Pivot this sub-problem, and refine the sub-problems in the rest of the 
        # recursion tree.
        this_problem = self.pivot_problem()

        # At this point, the children of this_problem are _TedderSubProblems whose
        # children are _TedderMDLeafNodes

        # Solve the sub-problems defined by the layers
        current_sub_problem = this_problem.first_child
        while current_sub_problem is not None:
            if current_sub_problem.first_child != this_problem.pivot:
                solved_root = current_sub_problem.solve()
            else:
                # This problem is just the problem with the pivot, which has 
                # already been processed and 'solved'
                solved_root = current_sub_problem.first_child
            current_sub_problem = solved_root.parent.right_sibling
        
        """
        At this point, the children of this_problem are _TedderSubProblems whose
        children are _TedderMDNodes

        MD tree of all but the first connected component of this sub-problem's 
        graph has already been computed. Remove it for now, we merge the two MD 
        trees later
        """
        extra_components = this_problem.remove_extra_components()
        
        # Replace the layers by their solutions
        this_problem.remove_layers()
        # The children of this_problem are now _TedderMDNodes
        
        # Fix the attributes of the children
        this_problem.complete_alpha_lists()
        this_problem.number_by_comp()
        this_problem.number_by_tree()

        # Get the factorizing permutation
        this_problem.refinement()
        this_problem.promotion()

        # Use the factorizing permutation to build the tree
        this_problem.delineation()
        # The children of this_problem are now _TedderFactPermElements

        this_problem.assemble_tree()
        # The children of this_problem are now _TedderMDNodes

        this_problem.remove_degenerate_duplicates()

        # Incorporate extra components
        this_problem.merge_components(extra_components)

        """
        Must reset fields to have recursion continue to work
        Do not reset 'visited' field since we need to know which nodes have been 
        pivots for alpha-list calculations
        """
        this_problem.clear_all_but_visited()

        # Return the finished MD tree, which is this_problem's first child.
        return this_problem.first_child
    
    def process_neighbors(self, pivot):
        """
        Refines the subproblems of the recursion tree according to the 
        neighborhood of a pivot. If a neighbor has already been visited, adds 
        the pivot to that neighbor's alpha-list.
        
        INPUT:
        
        - ``pivot`` -- _TedderMDLeafNode
        
        OUTPUT:
        
        A subproblem consisting of the neighbors of 'pivot' in the same 
        subproblem as 'pivot'

        EXAMPLES:

        No neighbors to pull forward::

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderSubProblem
            sage: d = {0:[1], 1:[], 2:[3], 3:[]}
            sage: g = Graph(d)
            sage: problem = _TedderSubProblem()
            sage: problem.build_graph(g)
            sage: problem
            [3, 2, 1, 0]
            sage: problem.pivot_problem()
            [[2], PIVOT=[3], [1, 0]]
            sage: d = {0:[1,2], 1:[2], 2:[3], 3:[]}
            sage: g = Graph(d)
            sage: problem.build_graph(g)
            sage: problem
            [3, 2, 1, 0, 1, 0]

        Has neighbors in other subproblems that need to be pulled forwared (see
        pull_forward for more examples of nodes being pulled forward.)::


        """
        piv_neighs_list = pivot.neighbors
        neighbor_problem = _TedderSubProblem()
        for current_neighbor in piv_neighs_list:
            if current_neighbor.visited:
                current_neighbor.alpha.append(pivot)
            elif current_neighbor.parent == pivot.parent:
                neighbor_problem.add_child(current_neighbor)
            else:
                self.pull_forward(current_neighbor)
        return neighbor_problem
    
    def pull_forward(self, leaf):
        """
        Determines which of the following three cases applies:
        (1): The given vertex must be moved forward from its current subproblem 
        to the immediately preceding subproblem (i.e. it is found to occupy the 
        previous layer)
        (2): A new subproblem must be formed consisting of the given vertex and 
        placed immediately before its current subproblem (i.e. a new layer must 
        be formed initially consisting of only this vertex)
        (3): The recursion tree remains unchanged
        In the first two cases, it effects the necessary changes
        
        INPUT:
        
        - ``leaf`` -- _TedderMDLeafNode
        """
        current_layer = leaf.parent
        if current_layer is not None and current_layer.connected:
            return

        prev_layer = current_layer.left_sibling

        if prev_layer is not None and (prev_layer.active or prev_layer.is_pivot_layer()):
            """
            If the previous layer is the pivot, or is the layer currently being
            worked on, this is the first node in this stage to be pulled forward,
            so a new layer must be formed
            """
            prev_layer = _TedderSubProblem()
            prev_layer.insert_before(current_layer)

            # The new layer is connected to the first component in its 
            # subproblem through the pivot.
            prev_layer.connected = True
        
        if prev_layer is not None and prev_layer.connected:
            prev_layer.add_child(leaf)
        
        if current_layer.has_no_children():
            current_layer.remove()

    def pivot_problem(self):
        """
        Selects a pivot vertex from this recursive subproblem and partitions the 
        recursion tree according to its neighbors.
        Has the side effect that this recursive subproblem will no longer be the 
        current recursive subproblem, which is necessary to achieve linear time; 
        returns the new current recursive subproblem
        
        OUTPUT:
        
        The new current recursive subproblem
        """
        pivot = self.first_child # This should be a _TedderMDLeafNode
        assert(pivot is not None and isinstance(pivot, _TedderMDLeafNode))
        pivot.visited = True
        # Process the neighbours of the pivot, getting back the subproblem
        # containing the neighbours of the pivot.
        neighbor_problem = self.process_neighbors(pivot)
        # Create the subproblem for just the pivot
        pivot_problem = _TedderSubProblem(pivot)

        # Pivot forms part of the first connected component of the current 
        # subproblem's graph
        pivot_problem.connected = True

        """
        Replace the current subproblem with something new, but sharing the same 
        attributes. See comment below regarding reuse of current recursive 
        subproblem
        """
        replacement = _TedderSubProblem()
        replacement.copy(self)
        self.replace_with(replacement)
        replacement.pivot = pivot

        # Must reuse the current subproblem to act as non-neighbor partition of 
        # the current recursive subproblem in order to achieve linear-time
        if not self.has_no_children():
            self.clear_attributes()
            replacement.add_child(self)
        
        replacement.add_child(pivot_problem)
        
        if not neighbor_problem.has_no_children():
            # Neighbors connected to pivot and so also part of first connected 
            # component of current subproblem's graph
            neighbor_problem.connected = True
            replacement.add_child(neighbor_problem)
        """
        Replacement now has children (from left to right):
            1. neighbor_problem, first child if exists
            2. pivot_problem, first child if neighbor_problem doesn't exist
            3. non_neighbor_problem
        Where neighbor_problem is the subproblem for the elements that are 
        neighbors to the pivot (if none, this child doesn't exist)
        pivot_problem is the subproblem with just the pivot in
        non_neighbor_problem is the subproblem with all the elements that aren't
        neighbors of the pivot (if none, this child doesn't exist)
        """
        return replacement

    def remove_extra_components(self):
        """
        Determines if this subproblem's graph has more than one component and 
        removes them if it does.
        
        OUTPUT:
        
        If more than one component exists, returns the root of the recursively 
        computed MD tree for the graph consisting of all but the first 
        component. Returns None otherwise.
        """
        current_sub_problem = self.first_child
        while current_sub_problem is not None and current_sub_problem.connected:
            current_sub_problem = current_sub_problem.right_sibling
        
        if current_sub_problem is not None:
            current_sub_problem.remove()
            root = current_sub_problem.first_child
            root.remove()
            return root
        else:
            return None
        
    def remove_layers(self):
        """
        Replaces the subproblems of this subproblem with their recursively 
        computed solutions (i.e. replaces the children of this node by their 
        children.)
        
        PRECONDITION:

        Each child of this node is a _TedderSubProblem with exactly one child.
        """
        current_layer = self.first_child
        while current_layer is not None:
            next_layer = current_layer.right_sibling
            current_layer.replace_with(current_layer.first_child)
            current_layer = next_layer

    def complete_alpha_lists(self):
        """
        For each vertex x in this subproblem, looks at alpha(x), and if y in 
        alpha(x), adds x to alpha(y). 

        POSTCONDITION:
        
        no alpha-list contains duplicate entries
        """

        # Completes the list (possibly creating duplicate entries within them).
        leaves_list = self.get_leaves()
        for leaf in leaves_list:
            alpha_list = leaf.alpha
            for alpha_node in alpha_list:
                alpha_node.alpha.append(leaf)
        
        # Removes duplicate entries in the lists.
        for leaf in leaves_list:
            alpha_list = leaf.alpha
            i = 0
            while i < len(alpha_list):
                current_alpha_neighbor = alpha_list[i]
                if current_alpha_neighbor.is_marked():
                    alpha_list.pop(i)
                else:
                    current_alpha_neighbor.num_marks += 1
                    i += 1
            for alpha in alpha_list:
                alpha.clear_marks()

    def number_by_comp(self):
        """
        Numbers the nodes in the recursively computed MD trees for this 
        subproblem. Nodes in the tree to the left of x (the pivot) are numbered 
        by co-component and those in trees to the right of x are numbered by 
        component. The numbering starts at 0, and the tree to the left x is 
        considered first. All nodes in a particular (co-)component receive the 
        same number, which is one more than the previous (co-)component. The 
        roots of trees are therefore left unnumbered sometimes.
        """
        comp_number = 0
        after_pivot = False
        current_root = self.first_child
        while current_root is not None:
            if current_root == self.pivot:
                after_pivot = True
            if after_pivot:
                comp_number += current_root.number_comps(comp_number, NodeType.PARALLEL)
            else:
                comp_number += current_root.number_comps(comp_number, NodeType.SERIES)
            current_root = current_root.right_sibling

    def number_by_tree(self):
        """
        This subproblem's recursively computed MD trees are numbered one by one, 
        starting at 0 for the tree to the left of x; every node in the tree is 
        assigned that tree's number.
        """
        tree_number = 0
        current_root = self.first_child
        while current_root is not None:
            current_root.set_tree_number_for_subtree(tree_number)
            current_root = current_root.right_sibling
            tree_number += 1

    def refinement(self):
        # Every vertex in this subproblem uses its active edges to refine the 
        # recursively computed MD trees other than its own.
        leaf_list = self.get_leaves()
        for leaf in leaf_list:
            self.refine_with(leaf)
    
    def refine_with(self, refiner):
        """
        Effects the changes that result from a single vertex refining with it's 
        active edges
        
        INPUT:
        
        - ``refiner`` -- _TedderMDLeafNode
        """
        sub_tree_roots = self.get_max_subtrees(refiner.alpha)
        sibling_groups = self.group_sibling_nodes(sub_tree_roots)

        # Remove roots of trees.
        i = 0
        while i < len(sibling_groups):
            if sibling_groups[i].is_root():
                sibling_groups.pop(i)
            else:
                i += 1
        
        """
        Split trees when sibling groups are children of the root, and split 
        nodes when not. In the latter case, mark the two nodes resulting from 
        the split, plus all their ancestors as having been marked, also mark the 
        children of all prime ancestors.
        """
        for current in sibling_groups:
            # Determine the split type.
            pivot_tree_number = self.pivot.tree_number
            refiner_tree_number = refiner.tree_number
            current_tree_number = current.tree_number
            if current_tree_number < pivot_tree_number or refiner_tree_number < current_tree_number:
                split_type = NodeSplit.LEFT_SPLIT
            else:
                split_type = NodeSplit.RIGHT_SPLIT
            current_parent = current.parent
            if current_parent.is_root():
                # Parent is a root, must split the tree.
                if split_type == NodeSplit.LEFT_SPLIT:
                    current.insert_before(current_parent)
                else:
                    current.insert_after(current_parent)
                new_sibling = current_parent
                if current_parent.has_only_one_child():
                    current_parent.replace_this_by_its_children()
                if current_parent.has_no_children():
                    current_parent.remove()
            else:
                # Parent is not a root, must split the node.
                current.remove()
                if current_parent.has_only_one_child():
                    new_sibling = current_parent.first_child
                    current_parent.add_child(current)
                else:
                    """
                    To achieve linear time, must reuse the parent node to 
                    represent the non-neighbor partition. See the function 
                    'pivot' for another example of this trick.
                    """
                    replacement = _TedderMDNode()
                    replacement.copy(current_parent)
                    current_parent.replace_with(replacement)
                    replacement.add_child(current)
                    replacement.add_child(current_parent)
                    new_sibling = current_parent
            current.add_split_mark(split_type)
            new_sibling.add_split_mark(split_type)
            current.mark_ancestors_by_split(split_type)
            new_sibling.mark_ancestors_by_split(split_type)

    def get_max_subtrees(self, leaves):
        """
        Finds the set of maximal subtrees of this subproblem's recursively 
        computed forest of MD trees where the leaves of each subtree are members 
        of the supplied collection of vertices.
        
        INPUT:
        
        - ``leaves`` -- List of _TedderMDLeafNode
        
        OUTPUT:
        
        A list of the roots of each maximal subtree
        """
        active = leaves[::]
        discharged = []

        """
        Marking process: all nodes in maximal subtrees fully marked; the only 
        other marked nodes are parents of roots of maximal subtrees, and these 
        are partially marked.
        """
        i = 0
        while active != []:
            current = active[0]
            active.pop(0)
            if not current.is_root():
                current_parent = current.parent
                current_parent.num_marks += 1
                if current_parent.is_fully_marked():
                    active.append(current_parent)
            discharged.append(current)
        # Removes marks on all nodes; leaves discharged list so that it only 
        # holds roots of maximal subtrees
        i = 0
        while i < len(discharged):
            current = discharged[i]
            current.clear_marks()
            if not current.is_root():
                current_parent = current.parent
                if current_parent.is_fully_marked():
                    discharged.pop(i)
                else:
                    current_parent.clear_marks()
                    i += 1
            else:
                i += 1
        
        return discharged
    
    def group_sibling_nodes(self, nodes):
        """
        Takes the collection of the supplied nodes (nodes) and makes those that 
        are siblings in one of this subproblem's recursively computed MD trees 
        the children of a new node inserted in their place. New nodes inserted 
        have the same attributes as their parents. Nodes in the collection 
        without siblings are left unchanged.
        
        INPUT:
        
        - ``nodes`` -- List of _TedderMDNode
        
        OUTPUT:
        
        A list consisting of the supplied nodes without siblings and the new 
        nodes inserted in place of siblings
        """

        # Moves non-root nodes to front of parent's child list. Marks each node 
        # and marks their parents. Parents are marked once for each child node.
        parents = []
        for node in nodes:
            node.num_marks += 1
            if not node.is_root():
                node.make_first_child()
                current_parent = node.parent
                if not current_parent.is_marked():
                    parents.append(current_parent)
                current_parent.num_marks += 1
        
        # Collects the sibling groups formed.
        sibling_groups = []

        # First, trivial cases of nodes without siblings, meaning the roots of 
        # trees ...
        for node in nodes:
            if node.is_root():
                node.clear_marks()
                sibling_groups.append(node)
        # ... and the non-root nodes without siblings
        i = 0
        while i < len(parents):
            current = parents[i]
            if current.num_marks == 1:
                parents.pop(i)
                current.clear_marks()
                current.first_child.clear_marks()
                sibling_groups.append(current.first_child)
            else:
                i += 1
        
        # Next, group sibling nodes as children of a new node inserted in their 
        # place.
        for current_parent in parents:
            current_parent.clear_marks()
            grouped_children = _TedderMDNode()
            grouped_children.copy(current_parent)
            current_child = current_parent.first_child
            while current_child is not None and current_child.is_marked():
                next_child =  current_child.right_sibling
                current_child.clear_marks()
                grouped_children.add_child(current_child)
                current_child = next_child
            current_parent.add_child(grouped_children)
            sibling_groups.append(grouped_children)

        return sibling_groups
    
    def promotion(self):
        """
        All nodes labelled by one of the two split marks are promoted to depth-0 
        in this subproblem's forest. First the nodes marked by left splits are 
        promoted, then those marked by right splits. Nodes without children or 
        only a single child are deleted, and in the latter instance replaced by 
        their lone child.
        
        PRECONDITION: 
        
        If a node 'n' has a split mark of type 'x', then all its ancestors in 
        the forest also have a split mark of type 'x'.
        """
        self.promote_one_direction(NodeSplit.LEFT_SPLIT)
        self.promote_one_direction(NodeSplit.RIGHT_SPLIT)
        self.clear_split_marks()

    def promote_one_direction(self, split_type):
        """
        All nodes labelled by the supplied split mark (split_type) are promoted 
        to depth-0 in this subproblem's forest. Nodes without children or only 
        a single child are deleted, and in the latter instance replaced by their 
        lone child.

        INPUT:
        
        - ``split_type`` -- NodeSplit, LEFT_SPLIT or RIGHT_SPLIT

        PRECONDITION: 
        
        If a node is marked by the supplied type, then all its ancestors must 
        also be marked by this type.
        """
        current = self.first_child
        while current is not None:
            next_node = current.right_sibling
            current.promote(split_type)
            current = next_node

    def delineation(self):
        """
        Uses the factorizing permutation resulting from promotion, the active 
        edges between the vertices, and the (co-)components calculated 
        recursively to identify and delineate the strong modules containing x.
        """
        # Create the factorising permutation elements for each MD tree
        self.build_permutation()
        # Compute and fix the attributes of the elements
        self.determine_left_co_comp_fragments()
        self.determine_right_comp_fragments()
        self.determine_right_layer_neighbor()
        self.compute_fact_perm_edges()
        self.compute_mu()
        # Delineate the strong modules containing x
        self.delineate()

    def build_permutation(self):
        """
        Replaces each tree in this subproblem's forest with a 
        _TedderFactPermElement object, making the root of the tree the child of 
        the _TedderFactPermElement. The new _TedderFactPermElements are numbered 
        from left to right starting at 0, and these numbers are used as their 
        index.
        """
        current = self.first_child
        num_fact_perm_elements = 0
        while current is not None:
            next_node = current.right_sibling 
            new_element = _TedderFactPermElement(num_fact_perm_elements)
            new_element.insert_before(current)
            new_element.add_child(current)
            num_fact_perm_elements += 1
            current = next_node

    def determine_left_co_comp_fragments(self):
        """
        For each co-component of G[N(x)], determines if some portion of it 
        appears as part of a factorizing permutation element to its left.

        We take advantage of the fact that co-components of G[N(x)] appear 
        consecutively and all nodes within them are numbered according to their 
        membership in these co-components.
        """
        current = self.first_child
        last_comp_num = -1

        while current.first_child != self.pivot:
            current_comp_num = current.first_child.comp_number
            if last_comp_num != -1 and last_comp_num == current_comp_num:
                current.has_left_co_comp_fragment = True
            last_comp_num = current_comp_num
            current = current.right_sibling
    
    def determine_right_comp_fragments(self):
        """
        For the components of G[N_2] (the vertices distance 2 from x), 
        determines if some portion of it appears as part of a factorizing 
        permutation element to its right.

        We use an approach similar to that applied in the function
        'determine_left_co_comp_fragments'
        """
        current = self.pivot.parent.right_sibling
        last = None
        last_comp_num = -1
        while current is not None:
            current_comp_num = current.first_child.comp_number
            if last_comp_num != -1 and last_comp_num == current_comp_num:
                last.has_right_comp_fragment = True
            last = current
            last_comp_num = current_comp_num
            current = current.right_sibling

    def determine_right_layer_neighbor(self):
        """
        For the factorizing permutation elements of G[N_2] (vertices distance 2 
        from x), determines if each has an edge to N_3 (vertices distance 3 
        from x)
        """
        current = self.pivot.parent.right_sibling
        while current is not None:
            current_tree = current.first_child
            current_tree_num = current_tree.tree_number
            current_leaves_list = current_tree.get_leaves()
            for leaf in current_leaves_list:
                alpha_list = leaf.alpha
                for alpha in alpha_list:
                    if alpha.tree_number > current_tree_num:
                        current.has_right_layer_neighbor = True
            current = current.right_sibling
    
    def compute_fact_perm_edges(self):
        """
        Determines the edges between factorizing permutation elements on either 
        side of the pivot and explicitly add these edges as adjacencies of the 
        factorizing permutation elements in question. 
        Two factorizing permutation elements are considered adjacent if there is 
        a join between the leaves/vertices in the trees forming them.
        """
        # Change the comp_number of each vertex to the index of the factorizing 
        # permutation element to which it belongs
        current_element = self.first_child
        while current_element is not None:
            leaves_list = current_element.get_leaves()
            for leaf in leaves_list:
                leaf.comp_number = current_element.index
            current_element = current_element.right_sibling
        
        # Determine size of each factorizing permutation element.
        fact_perm_list = self.build_fact_perm_list()
        element_sizes = []
        for element in fact_perm_list:
            element_sizes.append(len(element.get_leaves()))

        # Add a neighbor every time there is an edge between factorizing 
        # permutation elements on either side of the pivot
        current_element = self.first_child
        while current_element is not None:
            leaves_list = current_element.get_leaves()
            for leaf in leaves_list:
                alpha_list = leaf.alpha
                for alpha_element in alpha_list:
                    current_element.neighbors.append(fact_perm_list[alpha_element.comp_number])
            current_element = current_element.right_sibling
        
        # Replace the edges added above with edges if a join exists
        current_element = self.first_child
        while current_element is not None:
            # Count the edges added above and remove duplicates
            neighbors_list = current_element.neighbors
            i = 0
            while i < len(neighbors_list):
                current_neighbor = neighbors_list[i]
                if current_neighbor.is_marked():
                    neighbors_list.pop(i)
                else:
                    i += 1
                current_neighbor.num_marks += 1
            current_element.neighbors = neighbors_list

            # Add the edge if a join is found to exist
            new_neighbors = []
            for neighbor in neighbors_list:
                my_size = element_sizes[current_element.index]
                neighbor_size = element_sizes[neighbor.index]
                if my_size * neighbor_size == neighbor.num_marks:
                    # There is a join
                    new_neighbors.append(neighbor)
                neighbor.clear_marks()
            current_element.replace_neighbors(new_neighbors)
            current_element = current_element.right_sibling

    def build_fact_perm_list(self):
        """
        Builds a list containing the factorizing permutation elements in order. 
        Thus, the index of each factorizing permutation element is their index 
        in the array
        
        OUTPUT:
        
        The array containing the factorizing permutation
        """
        fact_perm = []
        current_element = self.first_child
        while current_element is not None:
            fact_perm.append(current_element)
            current_element = current_element.right_sibling
        return fact_perm

    def compute_mu(self):
        # Computes the mu-value for each factorizing permutation element

        first_element = self.first_child # Should be a _TedderFactPermElement
        current = first_element
        pivot_element = self.pivot.parent

        # Initialize mu-values for those right of pivot; this is their default 
        # value
        while current is not None:
            current.mu = first_element
            current = current.right_sibling
        
        # mu-values determined only by looking at elements to the left of the 
        # pivot
        current = self.first_child
        while current != pivot_element:
            next_element = current.right_sibling
            neighbor_list = current.neighbors
            for neighbor in neighbor_list:
                """
                Neighbor to the left of pivot is universal to all up to current, 
                and also adjacent to current, so mu gets updated to next_element
                """
                if neighbor.mu.index == current.index:
                    neighbor.mu = next_element
                
                # Current has an edge past previous farthest edge, so must 
                # update mu.
                if neighbor.index > current.mu.index:
                    current.mu = neighbor
            current = next_element

    def delineate(self):
        """
        For each strong module containing x, inserts a pair of markers to 
        delineate the module; one marker is inserted immediately to the left of 
        the module's left boundary, and another immediately to the right of the 
        module's right boundary. Markers are _TedderFactPermElements whose index 
        is -1
        """
        pivot_element = self.pivot.parent
        # Find the last element in the permutation
        last_element = pivot_element
        while last_element.right_sibling is not None:
            last_element = last_element.right_sibling
        
        first_element = self.first_child

        # Current boundaries of module currently being formed.
        left = pivot_element.left_sibling
        right = pivot_element.right_sibling

        # The boundaries of the last module created
        left_last_in = pivot_element
        right_last_in = pivot_element
        # Delineates the module one at a time
        while left is not None or right is not None:
            series_module_formed = False

            # If a series module is possible, greedily adds the elements 
            # composing it
            while (left is not None and
                    left.mu.index <= right_last_in.index and
                    not left.has_left_co_comp_fragment):
                series_module_formed = True
                left_last_in = left
                left = left.left_sibling
            
            parallel_module_formed = False
            
            # If a parallel module is possible (and a series module has not 
            # already been formed), greedily adds the elements composing it
            while (not series_module_formed and right is not None and
                    right.mu.index >= left_last_in.index and
                    not right.has_right_comp_fragment and 
                    not right.has_right_layer_neighbor):
                parallel_module_formed = True
                right_last_in = right
                right = right.right_sibling
            
            left_queue = []
            if not series_module_formed and not parallel_module_formed:
                """
                Neither a series or parallel module could be formed, so must 
                form a prime module (neither left nor right will be None), 
                which must contain the first co-component to the left of the 
                pivot.
                """
                while True:
                    left_queue.append(left)
                    left_last_in = left
                    left = left.left_sibling
                    if not left_last_in.has_left_co_comp_fragment:
                        break
            
            right_queue = []
            has_right_edge = False

            # Add elements to the prime module one at a time using a forcing 
            # rule
            while len(left_queue) != 0 or len(right_queue) != 0:
                # Add elements from the left of the pivot
                while len(left_queue) != 0:
                    current_left = left_queue.pop(0)

                    # Must add all elements up to mu once current_left is 
                    # included in the module
                    while current_left.mu.index > right_last_in.index:
                        # Once part of a component is added, all of it must be 
                        # added
                        while True:
                            right_queue.append(right)
                            right_last_in = right
                            right = right.right_sibling
                            if right_last_in.has_right_layer_neighbor:
                                has_right_edge = True
                            if not right_last_in.has_right_comp_fragment:
                                break
                
                # Add elements to the right of the pivot
                while len(right_queue) != 0:
                    current_right = right_queue.pop(0)

                    # Must add all elements up to mu once current_right is 
                    # included in the module
                    while current_right.mu.index < left_last_in.index:
                        # Once part of a co-component is added, all of it must 
                        # be added
                        while True:
                            left_queue.append(left)
                            left_last_in = left
                            left = left.left_sibling
                            if not left_last_in.has_left_co_comp_fragment:
                                break
        
            """
            Added to the module an element to the right of x with an edge to a 
            layer to its right, so the module must be the entire graph in this 
            case
            """
            if has_right_edge:
                left_last_in = first_element
                right_last_in = last_element
                left = None
                right = None
            
            # Delineate the module just found
            left_boundary = _TedderFactPermElement(-1)
            right_boundary = _TedderFactPermElement(-1)
            left_boundary.insert_before(left_last_in)
            right_boundary.insert_after(right_last_in)

    def assemble_tree(self):
        """
        Takes the factorizing permutation with the strong modules containing x 
        properly delineated and assembles the MD tree. 
        Creates a spline of new modules for each strong module containing x, and 
        affixes to these the subtrees forming the permutation, based on the 
        position of each subtree relative to the nested strong modules 
        containing x.
        Replaces the factorizing permutation within the current subproblem with 
        the MD tree assembled. That is, the subproblem is made to have one child, 
        the root of the MD tree constructed.
        """
        left = self.pivot.parent.left_sibling
        right = self.pivot.parent.right_sibling

        # Smallest strong module containing x is x itself
        last_module = self.pivot

        while left is not None or right is not None:
            # Create the spine one module at a time
            new_module = _TedderMDNode()
            new_module.add_child(last_module)

            added_pivot_neighbors = False
            added_pivot_non_neighbors = False

            # Add the subtrees of the new module from N(x)
            while left.index != -1:
                new_module.add_children_from(left)
                old_left = left
                left = left.left_sibling
                old_left.remove()
                added_pivot_neighbors = True
            # Add the subtrees of the new module from /N(x)
            while right.index != -1:
                new_module.add_children_from(right)
                old_right = right
                right = right.right_sibling
                old_right.remove()
                added_pivot_non_neighbors = True
            
            if added_pivot_neighbors and added_pivot_non_neighbors:
                new_module.type = NodeType.PRIME
            elif added_pivot_neighbors:
                new_module.type = NodeType.SERIES
            else:
                new_module.type = NodeType.PARALLEL
            left = left.left_sibling
            right = right.right_sibling
            last_module = new_module
        self.replace_children_with(last_module)
    
    def merge_components(self, new_components):
        """
        Takes the MD tree for this sub-problem and merges it with the MD tree 
        rooted at the supplied node. If the roots of both trees are parallel, 
        then the former's children are made children of the latter. Otherwise, 
        a new root is created with its children being the roots of the two 
        trees in question. The tree resulting from this merge becomes the MD 
        tree of this subproblem.

        INPUT:
        
        - ``new_components`` -- _TedderMDNode
        """
        first_component = self.first_child
        if new_components is None:
            # No new components to merge, so can just end the function now
            return
        elif new_components.type is NodeType.PARALLEL:
            if first_component.type is NodeType.PARALLEL:
                new_components.add_children_from(first_component)
            else:
                new_components.add_child(first_component)
            self.add_child(new_components)
        else:
            new_root = _TedderMDNode(NodeType.PARALLEL)
            new_root.add_child(first_component)
            new_root.add_child(new_components)
            self.add_child(new_root)

    def __repr__(self):
        """
        Overridden from _TedderTreeNode
        Returns the string representation of this element. 
        _TedderSubProblems don't have any sort of 'value', so the 
        representation of this node is just a list of the 
        representations of this node's children, except the child
        containing the pivot of this node (is there is one) is marked
        with 'PIVOT='

        EXAMPLES:

            sage: from sage.graphs.graph_decompositions.modular_decomposition import _TedderSubProblem, _TedderMDLeafNode
            sage: p1 = _TedderSubProblem()
            sage: p2 = _TedderSubProblem()
            sage: p1.add_child(p2)
            sage: n = _TedderMDLeafNode(1)
            sage: p2.add_child(n)
            sage: p1.pivot = n
            sage: p3 = _TedderSubProblem()
            sage: p1.add_child(p3)
            sage: str(p1)
            '[[], PIVOT=[1]]'
        """
        result = "["
        current = self.first_child
        if current is not None:
            if current.first_child == self.pivot and self.pivot is not None:
                result += "PIVOT="
            result += str(current)
            current = current.right_sibling
        while current is not None:
            if current.first_child == self.pivot and self.pivot is not None:
                result += ", PIVOT=" + str(current)
            else:
                result += ", " + str(current)
            current = current.right_sibling
        return result + "]"

def tedder_algorithm(graph):
    """
    Compute the modular decomposition by the algorithm of Tedder

    Compute the modular decomposition of the given graph by the algorithm of
    Tedder [TCHP2008]_. The algorithm arbitrary selects a pivot vertex, say
    `x`, and recursively computes the MD tree for its neighbourhood, `N(x)`,
    and its non-neighbourhood, `\bar(N(x))`. It then constructs a factorizing
    premutation, which is an ordering of MD trees s.t. the strong modules
    containing `x` will be in order, and the strong modules not containing `x`
    will be separate. The algorithm then identifies the strong modules, and 
    assembles the tree. In order for the algorithm to work in linear time,
    a custom data structure is used instead of the MD node class Node, and
    post-processing then transforms the finalised data structure into the 
    equivalent Node objects.

    INPUT:

    - ``graph`` -- the graph for which modular decomposition tree needs to be
      computed

    OUTPUT:

    The modular decomposition tree of the graph.

    EXAMPLES:

    The Icosahedral graph is Prime::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(tedder_algorithm(graphs.IcosahedralGraph()))
        PRIME
         2
         3
         9
         6
         8
         1
         10
         7
         4
         0
         5
         11

    The Octahedral graph is not Prime::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(tedder_algorithm(graphs.OctahedralGraph()))
        SERIES
         PARALLEL
          1
          4
         PARALLEL
          2
          3
         PARALLEL
          0
          5

    Tetrahedral Graph is Series::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(tedder_algorithm(graphs.TetrahedralGraph()))
        SERIES
         2
         0
         1
         3

    Modular Decomposition tree containing both parallel and series modules::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d = {2:[4,3,5], 1:[4,3,5], 5:[3,2,1,4], 3:[1,2,5], 4:[1,2,5]}
        sage: g = Graph(d)
        sage: print_md_tree(tedder_algorithm(g))
        SERIES
         PARALLEL
          3
          4
         PARALLEL
          1
          2
         5

    Graph from Marc Tedder implementation of modular decomposition::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d = {1:[5,4,3,24,6,7,8,9,2,10,11,12,13,14,16,17], 2:[1],
        ....:       3:[24,9,1], 4:[5,24,9,1], 5:[4,24,9,1], 6:[7,8,9,1],
        ....:       7:[6,8,9,1], 8:[6,7,9,1], 9:[6,7,8,5,4,3,1], 10:[1],
        ....:       11:[12,1], 12:[11,1], 13:[14,16,17,1], 14:[13,17,1],
        ....:       16:[13,17,1], 17:[13,14,16,18,1], 18:[17], 24:[5,4,3,1]}
        sage: g = Graph(d)
        sage: test_modular_decomposition(tedder_algorithm(g), g)
        True

    Graph from the :wikipedia:`Modular_decomposition`::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d2 = {1:[2,3,4], 2:[1,4,5,6,7], 3:[1,4,5,6,7], 4:[1,2,3,5,6,7],
        ....:       5:[2,3,4,6,7], 6:[2,3,4,5,8,9,10,11],
        ....:       7:[2,3,4,5,8,9,10,11], 8:[6,7,9,10,11], 9:[6,7,8,10,11],
        ....:       10:[6,7,8,9], 11:[6,7,8,9]}
        sage: g = Graph(d2)
        sage: test_modular_decomposition(tedder_algorithm(g), g)
        True

    TESTS:

    Bad Input::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = DiGraph()
        sage: tedder_algorithm(g)
        Traceback (most recent call last):
        ...
        ValueError: Graph must be undirected

    Empty Graph is Prime::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = Graph()
        sage: tedder_algorithm(g)
        PRIME []


    Ensure that a random graph and an isomorphic graph have identical modular
    decompositions. ::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: permute_decomposition(2, tedder_algorithm, 20, 0.5)
    """
    # Some basic graph checks
    if graph.is_directed():
        raise ValueError("Graph must be undirected")

    if not graph.order():
        return create_prime_node()

    # Create the subproblem object
    main_problem = _TedderSubProblem()

    # Populate the subproblem with the vertices of ``graph``
    main_problem.build_graph(graph)
    
    # Recursively solve the subproblem
    tedder_root = main_problem.solve()

    # Post-processing -- turn the _TedderMDNodes and _TedderMDLeafNodes into 
    # Nodes using a recursive helper function
    return tedder_root.to_node()

# ============================================================================
# Overall Function
# ============================================================================

def modular_decomposition(graph, algorithm = "habib_maurer"):
    """
    Compute the modular decomposition of the graph

    INPUT:

    - ``graph`` -- the graph for which modular decomposition tree needs to be
      computed

    - ``algorithm`` -- string (default ``habib_maurer``). Either ``habib_maurer`` or
      ``tedder``. Decides with which algorithm to compute the modular decomposition

    OUTPUT:

    The modular decomposition tree of the graph.

    EXAMPLES:

    The Icosahedral graph is Prime::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(modular_decomposition(graphs.IcosahedralGraph()))
        PRIME
         1
         5
         7
         8
         11
         0
         2
         6
         3
         9
         4
         10

    The Octahedral graph is not Prime (using tedder algorithm)::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(modular_decomposition(graphs.OctahedralGraph(), "tedder"))
        SERIES
         PARALLEL
          1
          4
         PARALLEL
          2
          3
         PARALLEL
          0
          5

    Tetrahedral Graph is Series::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: print_md_tree(modular_decomposition(graphs.TetrahedralGraph(), "habib_maurer"))
        SERIES
         0
         1
         2
         3

    Modular Decomposition tree containing both parallel and series modules::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d = {2:[4,3,5], 1:[4,3,5], 5:[3,2,1,4], 3:[1,2,5], 4:[1,2,5]}
        sage: g = Graph(d)
        sage: print_md_tree(modular_decomposition(g))
        SERIES
         PARALLEL
          1
          2
         PARALLEL
          3
          4
         5

    Graph from Marc Tedder implementation of modular decomposition (using tedder algorithm)::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d = {1:[5,4,3,24,6,7,8,9,2,10,11,12,13,14,16,17], 2:[1],
        ....:       3:[24,9,1], 4:[5,24,9,1], 5:[4,24,9,1], 6:[7,8,9,1],
        ....:       7:[6,8,9,1], 8:[6,7,9,1], 9:[6,7,8,5,4,3,1], 10:[1],
        ....:       11:[12,1], 12:[11,1], 13:[14,16,17,1], 14:[13,17,1],
        ....:       16:[13,17,1], 17:[13,14,16,18,1], 18:[17], 24:[5,4,3,1]}
        sage: g = Graph(d)
        sage: test_modular_decomposition(modular_decomposition(g, "tedder"), g)
        True

    TESTS:

    Bad Input (digraph)::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = DiGraph()
        sage: modular_decomposition(g)
        Traceback (most recent call last):
        ...
        ValueError: Graph must be undirected

    Bad Input (bad algorithm field)::
        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = Graph()
        sage: modular_decomposition(g, "wrong")
        Traceback (most recent call last):
        ...
        ValueError: Algorithm must be "habib_maurer" or "tedder"

    Empty Graph is Prime (using tedder algorithm)::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = Graph()
        sage: modular_decomposition(g, "tedder")
        PRIME []

    Graph from the :wikipedia:`Modular_decomposition`::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d2 = {1:[2,3,4], 2:[1,4,5,6,7], 3:[1,4,5,6,7], 4:[1,2,3,5,6,7],
        ....:       5:[2,3,4,6,7], 6:[2,3,4,5,8,9,10,11],
        ....:       7:[2,3,4,5,8,9,10,11], 8:[6,7,9,10,11], 9:[6,7,8,10,11],
        ....:       10:[6,7,8,9], 11:[6,7,8,9]}
        sage: g = Graph(d2)
        sage: test_modular_decomposition(modular_decomposition(g, "habib_maurer"), g)
        True

    Graph from the :wikipedia:`Modular_decomposition` (using tedder algorithm)::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: d2 = {1:[2,3,4], 2:[1,4,5,6,7], 3:[1,4,5,6,7], 4:[1,2,3,5,6,7],
        ....:       5:[2,3,4,6,7], 6:[2,3,4,5,8,9,10,11],
        ....:       7:[2,3,4,5,8,9,10,11], 8:[6,7,9,10,11], 9:[6,7,8,10,11],
        ....:       10:[6,7,8,9], 11:[6,7,8,9]}
        sage: g = Graph(d2)
        sage: test_modular_decomposition(modular_decomposition(g, "tedder"), g)
        True


    Ensure that a random graph and an isomorphic graph have identical modular
    decompositions (with both algorithms). ::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: permute_decomposition(2, modular_decomposition, 20, 0.5)
    """
    if algorithm == "habib_maurer":
        # Use the Habib Maurer algorithm
        return habib_maurer_algorithm(graph)
    elif algorithm == "tedder":
        # Use the Tedder algorithm
        return tedder_algorithm(graph)
    else:
        raise ValueError('Algorithm must be "habib_maurer" or "tedder"')

# ============================================================================
# Below functions are implemented to test the modular decomposition tree
# ============================================================================

# Function implemented for testing
def test_modular_decomposition(tree_root, graph):
    """
    Test the input modular decomposition tree using recursion.

    INPUT:

    - ``tree_root`` -- root of the modular decomposition tree to be tested

    - ``graph`` -- graph whose modular decomposition tree needs to be tested

    OUTPUT:

    ``True`` if input tree is a modular decomposition else ``False``

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = graphs.HexahedralGraph()
        sage: test_modular_decomposition(modular_decomposition(g), g)
        True
    """
    if tree_root.node_type != NodeType.NORMAL:
        for module in tree_root.children:
            if not test_module(module, graph):
                # test whether modules pass the defining
                # characteristics of modules
                return False
            if not test_modular_decomposition(module,
                                              graph.subgraph(get_vertices(module))):
                # recursively test the modular decomposition subtrees
                return False

        if not test_maximal_modules(tree_root, graph):
            # test whether the mdoules are maximal in nature
            return False

    return True


# Function implemented for testing
def test_maximal_modules(tree_root, graph):
    r"""
    Test the maximal nature of modules in a modular decomposition tree.

    Suppose the module `M = [M_1, M_2, \cdots, n]` is the input modular
    decomposition tree. Algorithm forms pairs like `(M_1, M_2), (M_1, M_3),
    \cdots, (M_1, M_n)`; `(M_2, M_3), (M_2, M_4), \cdots, (M_2, M_n)`; `\cdots`
    and so on and tries to form a module using the pair. If the module formed
    has same type as `M` and is of type ``SERIES`` or ``PARALLEL`` then the
    formed module is not considered maximal. Otherwise it is considered maximal
    and `M` is not a modular decomposition tree.

    INPUT:

    - ``tree_root`` -- modular decomposition tree whose modules are tested for
      maximal nature

    - ``graph`` -- graph whose modular decomposition tree is tested

    OUTPUT:

    ``True`` if all modules at first level in the modular decomposition tree
    are maximal in nature

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = graphs.HexahedralGraph()
        sage: test_maximal_modules(modular_decomposition(g), g)
        True
    """
    if tree_root.node_type != NodeType.NORMAL:
        for index, module in enumerate(tree_root.children):
            for other_index in range(index + 1, len(tree_root.children)):

                # compute the module formed using modules at index and
                # other_index
                module_formed = form_module(index, other_index,
                                            tree_root, graph)

                if module_formed[0]:
                    # Module formed and the parent of the formed module
                    # should not both be of type SERIES or PARALLEL
                    mod_type = get_module_type(graph.subgraph(module_formed[1]))
                    if (mod_type == tree_root.node_type and
                            (tree_root.node_type == NodeType.PARALLEL or
                             tree_root.node_type == NodeType.SERIES)):
                        continue
                    return False
    return True


def get_vertices(component_root):
    """
    Compute the list of vertices in the (co)component

    INPUT:

    - ``component_root`` -- root of the (co)component whose vertices need to be
      returned as a list

    OUTPUT:

    list of vertices in the (co)component

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: forest = Node(NodeType.FOREST)
        sage: forest.children = [create_normal_node(2),
        ....:                    create_normal_node(3), create_normal_node(1)]
        sage: series_node = Node(NodeType.SERIES)
        sage: series_node.children = [create_normal_node(4),
        ....:                         create_normal_node(5)]
        sage: parallel_node = Node(NodeType.PARALLEL)
        sage: parallel_node.children = [create_normal_node(6),
        ....:                           create_normal_node(7)]
        sage: forest.children.insert(1, series_node)
        sage: forest.children.insert(3, parallel_node)
        sage: get_vertices(forest)
        [2, 4, 5, 3, 6, 7, 1]
    """
    vertices = []

    # inner recursive function to recurse over the elements in the
    # ``component``
    def recurse_component(node, vertices):
        if node.node_type == NodeType.NORMAL:
            vertices.append(node.children[0])
            return
        for child in node.children:
            recurse_component(child, vertices)

    recurse_component(component_root, vertices)
    return vertices


# Function implemented for testing
def get_module_type(graph):
    """
    Return the module type of the root of the modular decomposition tree of
    ``graph``.

    INPUT:

    - ``graph`` -- input sage graph

    OUTPUT:

    ``PRIME`` if graph is PRIME, ``PARALLEL`` if graph is PARALLEL and
    ``SERIES`` if graph is of type SERIES

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import get_module_type
        sage: g = graphs.HexahedralGraph()
        sage: get_module_type(g)
        PRIME
    """
    if not graph.is_connected():
        return NodeType.PARALLEL
    elif graph.complement().is_connected():
        return NodeType.PRIME
    return NodeType.SERIES


# Function implemented for testing
def form_module(index, other_index, tree_root, graph):
    r"""
    Forms a module out of the modules in the module pair.

    Let `M_1` and `M_2` be the input modules. Let `V` be the set of vertices in
    these modules. Suppose `x` is a neighbor of subset of the vertices in `V`
    but not all the vertices and `x` does not belong to `V`. Then the set of
    modules also include the module which contains `x`. This process is repeated
    until a module is formed and the formed module if subset of `V` is returned.

    INPUT:

    - ``index`` -- first module in the module pair

    - ``other_index`` -- second module in the module pair

    - ``tree_root`` -- modular decomposition tree which contains the modules
      in the module pair

    - ``graph`` -- graph whose modular decomposition tree is created

    OUTPUT:

    ``[module_formed, vertices]`` where ``module_formed`` is ``True`` if
    module is formed else ``False`` and ``vertices`` is a list of vertices
    included in the formed module

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = graphs.HexahedralGraph()
        sage: tree_root = modular_decomposition(g)
        sage: form_module(0, 2, tree_root, g)
        [False, {0, 1, 2, 3, 4, 5, 6, 7}]
    """
    vertices = set(get_vertices(tree_root.children[index]))
    vertices.update(get_vertices(tree_root.children[other_index]))

    # stores all neighbors which are common for all vertices in V
    common_neighbors = set()

    # stores all neighbors of vertices in V which are outside V
    all_neighbors = set()

    while True:
        # remove vertices from all_neighbors and common_neighbors
        all_neighbors.difference_update(vertices)
        common_neighbors.difference_update(vertices)

        for v in vertices:
            # stores the neighbors of v which are outside the set of vertices
            neighbor_list = set(graph.neighbors(v))
            neighbor_list.difference_update(vertices)

            # update all_neighbors and common_neighbors using the
            # neighbor_list
            all_neighbors.update(neighbor_list)
            common_neighbors.intersection_update(neighbor_list)

        if all_neighbors == common_neighbors:  # indicates a module is formed

            # module formed covers the entire graph
            if len(vertices) == graph.order():
                return [False, vertices]

            return [True, vertices]

        # add modules containing uncommon neighbors into the formed module
        for v in (all_neighbors - common_neighbors):
            for index in range(len(tree_root.children)):
                if v in get_vertices(tree_root.children[index]):
                    vertices.update(get_vertices(tree_root.children[index]))
                    break


# Function implemented for testing
def test_module(module, graph):
    """
    Test whether input module is actually a module

    INPUT:

    - ``module`` -- module which needs to be tested

    - ``graph`` -- input sage graph which contains the module

    OUTPUT:

    ``True`` if input module is a module by definition else ``False``

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = graphs.HexahedralGraph()
        sage: tree_root = modular_decomposition(g)
        sage: test_module(tree_root, g)
        True
        sage: test_module(tree_root.children[0], g)
        True
    """
    # A single vertex is a module
    if module.node_type == NodeType.NORMAL:
        return True

    # vertices contained in module
    vertices_in_module = get_vertices(module)

    # vertices outside module
    vertices_outside = list(set(graph.vertices(sort=False)) - set(vertices_in_module))

    # Nested module with only one child
    if module.node_type != NodeType.NORMAL and len(module.children) == 1:
        return False

    # If children of SERIES module are all SERIES modules
    if module.node_type == NodeType.SERIES:
        if children_node_type(module, NodeType.SERIES):
            return False

    # If children of PARALLEL module are all PARALLEL modules
    if module.node_type == NodeType.PARALLEL:
        if children_node_type(module, NodeType.PARALLEL):
            return False

    # check the module by definition. Vertices in a module should all either
    # be connected or disconnected to any vertex outside module
    for v in vertices_outside:
        if not either_connected_or_not_connected(v, vertices_in_module, graph):
            return False
    return True


# Function implemented for testing
def children_node_type(module, node_type):
    """
    Check whether the node type of the children of ``module`` is ``node_type``.

    INPUT:

    - ``module`` -- module which is tested

    - ``node_type`` -- input node_type

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = graphs.OctahedralGraph()
        sage: tree_root = modular_decomposition(g)
        sage: print_md_tree(modular_decomposition(g))
        SERIES
         PARALLEL
          0
          5
         PARALLEL
          1
          4
         PARALLEL
          2
          3
        sage: children_node_type(tree_root, NodeType.SERIES)
        False
        sage: children_node_type(tree_root, NodeType.PARALLEL)
        True
    """
    return all(node.node_type == node_type for node in module.children)


# Function implemented for testing
def either_connected_or_not_connected(v, vertices_in_module, graph):
    """
    Check whether ``v`` is connected or disconnected to all vertices in the
    module.

    INPUT:

    - ``v`` -- vertex tested

    - ``vertices_in_module`` -- list containing vertices in the module

    - ``graph`` -- graph to which the vertices belong

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = graphs.OctahedralGraph()
        sage: print_md_tree(modular_decomposition(g))
        SERIES
         PARALLEL
          0
          5
         PARALLEL
          1
          4
         PARALLEL
          2
          3
        sage: either_connected_or_not_connected(2, [1, 4], g)
        True
        sage: either_connected_or_not_connected(2, [3, 4], g)
        False
    """
    # marks whether vertex v is connected to first vertex in the module
    connected = graph.has_edge(vertices_in_module[0], v)

    # if connected is True then all vertices in module should be connected to
    # v else all should be disconnected
    return all(graph.has_edge(u, v) == connected for u in vertices_in_module)


def tree_to_nested_tuple(root):
    r"""
    Convert a modular decomposition tree to a nested tuple.

    INPUT:

    - ``root`` -- the root of the modular decomposition tree

    OUTPUT:

    A tuple whose first element is the type of the root of the tree and whose
    subsequent nodes are either vertex labels in the case of leaves or tuples
    representing the child subtrees.

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: g = graphs.OctahedralGraph()
        sage: tree_to_nested_tuple(modular_decomposition(g))
        (SERIES, [(PARALLEL, [0, 5]), (PARALLEL, [1, 4]), (PARALLEL, [2, 3])])
    """
    if root.node_type == NodeType.NORMAL:
        return root.children[0]
    else:
        return (root.node_type, [tree_to_nested_tuple(x) for x in root.children])


def nested_tuple_to_tree(nest):
    r"""
    Turn a tuple representing the modular decomposition into a tree.

    INPUT:

    - ``nest`` -- a nested tuple of the form returned by
      :meth:`tree_to_nested_tuple`

    OUTPUT:

    The root node of a modular decomposition tree.

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: tree = (NodeType.SERIES, 1, 2, (NodeType.PARALLEL, 3, 4))
        sage: print_md_tree(nested_tuple_to_tree(tree))
        SERIES
         1
         2
         PARALLEL
          3
          4
    """
    if not isinstance(nest, tuple):
        return create_normal_node(nest)

    root = Node(nest[0])
    root.children = [nested_tuple_to_tree(n) for n in nest[1:]]
    return root


def equivalent_trees(root1, root2):
    r"""
    Check that two modular decomposition trees are the same.

    Verify that the structure of the trees is the same. Two leaves are
    equivalent if they represent the same vertex, two internal nodes are
    equivalent if they have the same nodes type and the same number of children
    and there is a matching between the children such that each pair of
    children is a pair of equivalent subtrees.

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: t1 = nested_tuple_to_tree((NodeType.SERIES, 1, 2,
        ....:             (NodeType.PARALLEL, 3, 4)))
        sage: t2 = nested_tuple_to_tree((NodeType.SERIES,
        ....:             (NodeType.PARALLEL, 4, 3), 2, 1))
        sage: equivalent_trees(t1, t2)
        True
    """
    # internal definition
    def node_id(root):
        return (root.node_type, frozenset(get_vertices(root)))

    if root1.node_type != root2.node_type:
        return False

    if len(root1.children) != len(root2.children):
        return False

    if root1.node_type == NodeType.NORMAL:
        return root1.children[0] == root2.children[0]

    child_map = {}
    for node in root2.children:
        child_map[node_id(node)] = node

    for node in root1.children:
        id = node_id(node)
        if id not in child_map:
            return False
        if not equivalent_trees(node, child_map[id]):
            return False

    return True


def relabel_tree(root, perm):
    r"""
    Relabel the leaves of a tree according to a dictionary

    INPUT:

    - ``root`` -- the root of the tree

    - ``perm`` -- a function, dictionary, list, permutation, or ``None``
      representing the relabeling. See
      :meth:`~sage.graphs.generic_graph.GenericGraph.relabel` for description of
      the permutation input.

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: tuple_tree = (NodeType.SERIES, 1, 2, (NodeType.PARALLEL, 3, 4))
        sage: tree = nested_tuple_to_tree(tuple_tree)
        sage: print_md_tree(relabel_tree(tree, (4,3,2,1)))
        SERIES
         4
         3
         PARALLEL
          2
          1
    """
    from sage.groups.perm_gps.permgroup_element import PermutationGroupElement

    # If perm is not a dictionary, we build one !
    if perm is None:

        # vertices() returns a sorted list:
        # this guarantees consistent relabeling
        perm = {v: i for i, v in enumerate(get_vertices(root))}

    elif isinstance(perm, dict):
        from copy import copy

        # If all vertices do not have a new label, the code will touch the
        # dictionary. Let us keep the one we received from the user clean !
        perm = copy(perm)

    elif isinstance(perm, (list, tuple)):
        perm = dict(zip(sorted(get_vertices(root)), perm))

    elif isinstance(perm, PermutationGroupElement):
        n = len(get_vertices(root))
        ddict = {}
        for i in range(1, n):
            ddict[i] = perm(i) % n
        if n > 0:
            ddict[0] = perm(n) % n
        perm = ddict

    elif callable(perm):
        perm = {i: perm(i) for i in get_vertices(root)}

    else:
        raise TypeError("type of perm is not supported for relabeling")

    if root.node_type == NodeType.NORMAL:
        return create_normal_node(perm[root.children[0]])
    else:
        new_root = Node(root.node_type)
        new_root.children = [relabel_tree(child, perm) for child in root.children]
        return new_root


# =============================================================================
# Random tests
# =============================================================================

@random_testing
def test_gamma_modules(trials, vertices, prob, verbose=False):
    r"""
    Verify that the vertices of each gamma class of a random graph are modules
    of that graph.

    INPUT:

    - ``trials`` -- the number of trials to run

    - ``vertices`` -- the size of the graph to use

    - ``prob`` -- the probability that any given edge is in the graph.
      See :meth:`~sage.graphs.generators.random.RandomGNP` for more details.

    - ``verbose`` -- print information on each trial.

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: test_gamma_modules(3, 7, 0.5)
    """
    from sage.graphs.generators.random import RandomGNP
    for _ in range(trials):
        g = RandomGNP(vertices, prob)
        if verbose:
            print(g.graph6_string())
        g_classes = gamma_classes(g)
        for module in g_classes.keys():
            m_list = list(module)
            for v in g:
                if v not in module:
                    assert(either_connected_or_not_connected(v, m_list, g))
        if verbose:
            print("Passes!")


@random_testing
def permute_decomposition(trials, algorithm, vertices, prob, verbose=False):
    r"""
    Check that a graph and its permuted relabeling have the same modular
    decomposition.

    We generate a ``trials`` random graphs and then generate an isomorphic graph
    by relabeling the original graph. We then verify

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: permute_decomposition(30, habib_maurer_algorithm, 10, 0.5)
    """
    from sage.combinat.permutation import Permutations
    from sage.graphs.generators.random import RandomGNP
    for _ in range(trials):
        g1 = RandomGNP(vertices, prob)
        random_perm = Permutations(list(g1)).random_element()
        g2 = g1.relabel(perm=random_perm, inplace=False)
        if verbose:
            print(g1.graph6_string())
            print(random_perm)
        t1 = algorithm(g1)
        t2 = algorithm(g2)
        assert(test_modular_decomposition(t1, g1))
        assert(test_modular_decomposition(t2, g2))
        t1p = relabel_tree(t1, random_perm)
        assert(equivalent_trees(t1p, t2))
        if verbose:
            print("Passses!")


def random_md_tree(max_depth, max_fan_out, leaf_probability):
    r"""
    Create a random MD tree.

    INPUT:

    - ``max_depth`` -- the maximum depth of the tree.

    - ``max_fan_out`` -- the maximum number of children a node can have
      (must be >=4 as a prime node must have at least 4 vertices).

    - ``leaf_probability`` -- the probability that a subtree is a leaf

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: set_random_seed(0)
        sage: tree_to_nested_tuple(random_md_tree(2, 5, 0.5))
        (PRIME, [0, 1, (PRIME, [2, 3, 4, 5, 6]), 7, (PARALLEL, [8, 9, 10])])
    """

    from sage.misc.prandom import choice, randint, random

    if max_fan_out < 4:
        raise ValueError("max_fan_out must be at least 4")

    # Internal function
    def rand_md_tree(max_depth, parent_type):
        r"""
        Create the subtrees of a node.

        A child of a node cannot have the same node type as its parent if its
        parent's node type is either PARALLEL or SERIES.  Also its ``max_depth``
        is one less than its parent's.
        """
        if random() < leaf_probability or max_depth == 1:
            root = create_normal_node(current_leaf[0])
            current_leaf[0] += 1
            return root
        if parent_type == NodeType.PRIME:
            node_type = choice([NodeType.PRIME, NodeType.SERIES, NodeType.PARALLEL])
        elif parent_type == NodeType.SERIES:
            node_type = choice([NodeType.PRIME, NodeType.PARALLEL])
        else:
            node_type = choice([NodeType.PRIME, NodeType.SERIES])
        if node_type == NodeType.PRIME:
            num_children = randint(4, max_fan_out)
        else:
            num_children = randint(2, max_fan_out)
        root = Node(node_type)
        root.children = [rand_md_tree(max_depth - 1, node_type)
                         for _ in range(num_children)]
        return root

    # a hack around python2's lack of 'nonlocal'
    current_leaf = [0]
    node_type = choice([NodeType.PRIME, NodeType.SERIES, NodeType.PARALLEL])
    num_children = randint(4, max_fan_out)
    root = Node(node_type)
    root.children = [rand_md_tree(max_depth, node_type)
                     for _ in range(num_children)]
    return root


def md_tree_to_graph(root):
    r"""
    Create a graph having the given MD tree.

    For the prime nodes we use that every path of length 4 or more is prime.

    TODO: accept a function that generates prime graphs as a parameter and
    use that in the prime nodes.

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: tup1 = (NodeType.PRIME, 1, (NodeType.SERIES, 2, 3),
        ....:        (NodeType.PARALLEL, 4, 5), 6)
        sage: tree1 = nested_tuple_to_tree(tup1)
        sage: g1 = md_tree_to_graph(tree1)
        sage: g2 = Graph({1: [2, 3], 2: [1, 3, 4, 5], 3: [1, 2, 4, 5],
        ....:             4: [2, 3, 6], 5: [2, 3, 6], 6: [4, 5]})
        sage: g1.is_isomorphic(g2)
        True
    """
    from itertools import combinations, product

    from sage.graphs.graph import Graph

    def tree_to_vertices_and_edges(root):
        r"""
        Give the list of vertices and edges of the graph having the given md tree.
        """
        if root.node_type == NodeType.NORMAL:
            return (root.children, [])
        children_ve = [tree_to_vertices_and_edges(child) for child in root.children]
        vertices = [v for vs, es in children_ve for v in vs]
        edges = [e for vs, es in children_ve for e in es]
        vertex_lists = [vs for vs, es in children_ve]
        if root.node_type == NodeType.PRIME:
            for vs1, vs2 in zip(vertex_lists, vertex_lists[1:]):
                for v1, v2 in product(vs1, vs2):
                    edges.append((v1, v2))
        elif root.node_type == NodeType.SERIES:
            for vs1, vs2 in combinations(vertex_lists, 2):
                for v1, v2 in product(vs1, vs2):
                    edges.append((v1, v2))
        return (vertices, edges)

    vs, es = tree_to_vertices_and_edges(root)
    return Graph([vs, es], format='vertices_and_edges')


@random_testing
def recreate_decomposition(trials, algorithm, max_depth, max_fan_out,
                           leaf_probability, verbose=False):
    r"""
    Verify that we can recreate a random MD tree.

    We create a random MD tree, then create a graph having that decomposition,
    then find a modular decomposition for that graph, and verify that the two
    modular decomposition trees are equivalent.

    EXAMPLES::

        sage: from sage.graphs.graph_decompositions.modular_decomposition import *
        sage: recreate_decomposition(3, habib_maurer_algorithm, 4, 6, 0.5,
        ....:                         verbose=False)
    """
    for _ in range(trials):
        rand_tree = random_md_tree(max_depth, max_fan_out, leaf_probability)
        if verbose:
            print_md_tree(rand_tree)
        graph = md_tree_to_graph(rand_tree)
        if verbose:
            print(graph.graph6_string())
            print(graph.to_dictionary())
        reconstruction = algorithm(graph)
        if verbose:
            print_md_tree(reconstruction)
        assert(equivalent_trees(rand_tree, reconstruction))
        if verbose:
            print("Passes!")
