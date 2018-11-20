class Node:
    RED = True
    BLACK = False

    def __init__(self, id, key, color = RED):
        self.color = color
        self.key = key
        self.left = self.right = self.parent = NilNode.instance()
        self.id = id

    def __str__(self, level = 0, indent = "   "):
        left_id = "Nil" if not self.left else self.left.id
        right_id = "Nil" if not self.right else self.right.id
        parent_id = "Nil" if not self.parent else self.parent.id
        return f"Node(id={self.id}, parent={parent_id}, left={left_id}, right={right_id}, red={self.color})"

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    def is_red(self):
        return self.color == Node.RED


class NilNode(Node):
    __instance__ = None

    @classmethod
    def instance(self):
        if self.__instance__ is None:
            self.__instance__ = NilNode()
        return self.__instance__

    def __init__(self):
        self.color = Node.BLACK
        self.key = None
        self.left = self.right = self.parent = None

    def __nonzero__(self):
        return False

    def __bool__(self):
        return False

    def is_red(self):
        return False

class BinarySearchTree:
    def __init__(self):
        self.root = NilNode.instance()
        self.size = 0
        self.control = {}

    def __str__helper(self, node, level: int = 0, indent: str = "   "):
        s = level * indent + str(node)
        if node.left:
            s += "\n" + self.__str__helper(node.left, level + 1, indent)
        if node.right:
            s += "\n" + self.__str__helper(node.right, level + 1, indent)
        return s

    def __str__(self, indent="  "):
        if not self.root:
            return "(root.size = 0, balanced = True)\n(Empty tree)"
        res, err = self.is_rbt()
        return f"(root.size = {self.size}, RBT = {res})\n" + \
                self.__str__helper(self.root, indent=indent)

    def is_empty(self) -> bool:
        return bool(self.root)

    def insert(self, id: int, key):
        x = Node(id, key)
        self.control[x.id] = x
        self.root = self.__insert(self.root, x)
        self.root.parent = NilNode.instance()
        self.root.color = Node.BLACK
        self.size += 1
        res, err = self.is_rbt()
        if not res:
            print(str(self))
            raise Exception(err)

    def __insert(self, act_node, new_node: Node) -> Node:
        if not act_node:
            return new_node

        if new_node.key < act_node.key:
            act_node.left = self.__insert(act_node.left, new_node)
            act_node.left.parent = act_node
        else:
            act_node.right = self.__insert(act_node.right, new_node)
            act_node.right.parent = act_node

        if act_node.right.is_red() and not act_node.left.is_red():
            act_node = self.__rotate_left(act_node)
        if act_node.left.is_red() and act_node.left.left.is_red():
            act_node = self.__rotate_right(act_node)
        if act_node.left.is_red() and act_node.right.is_red():
            self.__flip_colors(act_node)

        return act_node

    def delete(self, id: int):
        if not (id in self.control):
            return

        z = self.control[id]
        del self.control[id]
        if not z.left or not z.right:
            y = z
        else:
            y = self.successor(z)
            z.key = y.key
            z.id = y.id
            self.control[y.id] = z

        x = y.right if not y.left else y.left
        x.parent = y.parent
        if y == y.parent.left:
            y.parent.left = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            self.root = x

        if not y.is_red():
            if x.is_red():
                x.color = Node.BLACK
            else:
                self.__balance(x)

        self.size -= 1
        res, err = self.is_rbt()
        if not res:
            print(str(self))
            raise Exception(err)
        return y

    def __balance(self, node):
        if self.root == node or node.is_red():
            # CASE 1/4
            node.color = Node.BLACK
            return
        left = (node == node.parent.left)
        parent = node.parent
        sibling = node.parent.right if left else node.parent.left
        if sibling.is_red():
            # CASE 2
            if left:
                self.__rotate_left(parent)
                sibling = parent.right
            else:
                self.__rotate_right(parent)
                sibling = parent.left
        if not sibling.right.is_red() and not sibling.left.is_red():
            # CASE 3
            sibling.color = Node.RED
            self.__balance(parent)
        else:
            if left:
                if not sibling.right.is_red():
                    # CASE 5 left
                    self.__rotate_right(sibling)
                    sibling = parent.right
                # CASE 6 left
                parent = self.__rotate_left(parent)
                parent.left.color = Node.BLACK
                parent.right.color = Node.BLACK
            else:
                if not sibling.left.is_red():
                    # CASE 5 right
                    self.__rotate_left(sibling)
                    sibling = parent.left
                # CASE 6 right
                parent = self.__rotate_right(parent)
                parent.left.color = Node.BLACK
                parent.right.color = Node.BLACK

    def minimum(self, node = None):
        if node is None: node = self.root
        while node.left:
            node = node.left
        return node

    def maximum(self, node = None):
        if node is None: node = self.root
        while node.right:
            node = node.right
        return node

    def successor(self, node):
        if node.right:
            return self.minimum(node.right)
        y = node.parent
        while y and node == y.right:
            node = y
            y = y.parent
        return y

    def predecessor(self, node):
        if node.left:
            return self.maximum(node.left)
        y = node.parent
        while y and node == y.left:
            node = y
            y = y.parent
        return y

    def __rotate_right(self, node):
        x = node.left
        node.left = x.right
        x.right = node
        x.color = x.right.color
        x.right.color = Node.RED
        x.parent = node.parent
        node.parent = x
        if node.left: node.left.parent = node
        if x.parent.left == node:
            x.parent.left = x
        elif x.parent.right == node:
            x.parent.right = x
        else:
            self.root = x
        return x

    def __rotate_left(self, node):
        x = node.right
        node.right = x.left
        x.left = node
        x.color = x.left.color
        x.left.color = Node.RED
        x.parent = node.parent
        node.parent = x
        if node.right: node.right.parent = node
        if x.parent.left == node:
            x.parent.left = x
        elif x.parent.right == node:
            x.parent.right = x
        else:
            self.root = x
        return x

    def __flip_colors(self, node):
        node.color = not node.color
        node.left.color =  not node.left.color
        node.right.color =  not node.right.color

    def is_rbt(self):
        if not self.root:
            return (True, "")
        node = self.root
        final_blacks = 1
        while node:
            node = node.right
            if not node.is_red():
                final_blacks += 1
        errors, ids = self.__is_rbt(self.root, 0, final_blacks, 0)
        if errors == 0:
            return (True, "")
        elif errors == 1:
            return (False, f"Tree is not balanced on ids {ids}")
        elif errors == 2:
            return (False, f"Tree has double red nodes on ids {ids}")
        return (False, f"Tree is not balanced and has double red nodes on ids {ids}")

    def __is_rbt(self, node, blacks, final_blacks, level):
        if not node.is_red():
            blacks += 1
        elif node.left.is_red() or node.right.is_red():
            return (2, [node.id])
        if not node:
            return (0, []) if blacks == final_blacks else (1, [-1])
        lerr, lids = self.__is_rbt(node.left, blacks, final_blacks, level + 1)
        rerr, rids =self.__is_rbt(node.right, blacks, final_blacks, level + 1)
        if lerr != 0 and rerr != 0:
            return (lerr ^ rerr, lids + rids)
        if lerr != 0:
            return (lerr, lids)
        if rerr != 0:
            return (rerr, rids)
        return (0, [])
