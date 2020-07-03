# ported from https://github.com/vadimg/js_bintrees/blob/master/lib/rbtree.js

class TreeBase:
    def iterator(self):
        return Iterator(self)

    # removes all nodes from the tree
    def clear(self):
        self._root = None
        self.size = 0

    # returns node data if found, null otherwise
    def find(self, data):
        cur = self._root

        while cur is not None:
            c = self._comparator(data, cur.data)
            if c == 0:
                return cur.data
            else:
                cur = cur.get_child(c > 0)

        return None

    # returns iterator to node if found, null otherwise
    def findIter(self, data):
        cur = self._root
        iter = self.iterator()

        while cur is not None:
            c = self._comparator(data, cur.data)
            if c == 0:
                iter._cursor = cur
                return iter
            else:
                iter._ancestors.append(cur)
                cur = cur.get_child(c > 0)

        return None

    # returns an iterator to the tree node at or immediately after the item
    def lowerBound(self, item):
        cur = self._root
        iter = self.iterator()
        cmp = self._comparator

        while cur is not None:
            c = cmp(item, cur.data)
            if c == 0:
                iter._cursor = cur
                return iter
            iter._ancestors.append(cur)
            cur = cur.get_child(c > 0)

        for i in range(len(iter._ancestors)-1, -1, -1):
            cur = iter._ancestors[i]
            if cmp(item, cur.data) < 0:
                iter._cursor = cur
                iter._ancestors = iter._ancestors[:i]
                return iter

        iter._ancestors = []
        return iter

    # returns an iterator to the tree node immediately after the item
    def upperBound(self, item):
        iter = self.lowerBound(item)
        cmp = self._comparator

        while iter.data() is not None and cmp(iter.data(), item) == 0:
            iter.next()

        return iter

    def min(self):
        cur = self._root
        if cur is None:
            return None

        while cur.left is not None:
            cur = cur.left

        return cur.data

    def max(self):
        cur = self._root
        if cur is None:
            return None

        while cur.right is not None:
            cur = cur.right

        return cur.data


class Iterator:
    def __init__(self, tree):
        self._tree = tree
        self._ancestors = []
        self._cursor = None

    def data(self):
        return self._cursor.data if self._cursor is not None else None

    def _minNode(self, node):
        while node.left is not None:
            self._ancestors.append(node)
            node = node.left

        self._cursor = node

    def _maxNode(self, node):
        while node.right is not None:
            self._ancestors.append(node)
            node = node.right

        self._cursor = node

    # if cursor point to None, go back to FIRST node in tree
    # otherwise, return next node
    def next(self):
        if self._cursor is None:
            root = self._tree._root
            if root is not None:
                self._minNode(root)
        else:
            if self._cursor.right is None:

                while True:
                    save = self._cursor

                    if len(self._ancestors):
                        self._cursor = self._ancestors.pop()
                    else:
                        self._cursor = None
                        break

                    if self._cursor.right is not save:
                        break

            else:
                self._ancestors.append(self._cursor)
                self._minNode(self._cursor.right)

        return self.data()

    # if cursor point to None, go back to LAST node in tree
    # otherwise, return previous node
    def prev(self):
        if self._cursor is None:
            root = self._tree._root
            if root is not None:
                self._maxNode(root)
        else:
            if self._cursor.left is None:
                save = self._cursor

                while True:
                    save = self._cursor
                    if len(self._ancestors) > 0:
                        self._cursor = self._ancestors.pop()
                    else:
                        self._cursor = None
                        break

                    if self._cursor.left is not save:
                        break

            else:
                self._ancestors.append(self._cursor)
                self._maxNode(self._cursor.left)

        return self.data()


class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.red = True

    def get_child(self, dir):
        return self.right if dir else self.left

    def set_child(self, dir, val):
        if dir:
            self.right = val
        else:
            self.left = val


class RBTree(TreeBase):
    def __init__(self, comparator):
        self._root = None
        self._comparator = comparator
        self.size = 0

    def insert(self, data):
        success = False

        # empty tree
        if self._root is None:
            self._root = Node(data)
            success = True
            self.size += 1
        else:
            head = Node(None)

            dir = False
            lastDir = dir

            # parent
            p = None
            # grand-parent
            gp = None
            # grand-grand-parent
            ggp = head

            node = self._root
            ggp.right = self._root

            while True:
                if node is None:
                    node = Node(data)
                    p.set_child(dir, node)
                    success = True
                    self.size += 1
                elif is_red(node.left) and is_red(node.right):
                    node.red = True
                    node.left.red = False
                    node.right.red = False

                if is_red(node) and is_red(p):
                    dir2 = ggp.right is gp
                    if node is p.get_child(lastDir):
                        ggp.set_child(dir2, single_rotate(gp, not lastDir))
                    else:
                        ggp.set_child(dir2, double_rotate(gp, not lastDir))

                cmp = self._comparator(node.data, data)

                # stop if found
                if (cmp == 0):
                    break

                lastDir = dir
                dir = cmp < 0

                if gp is not None:
                    ggp = gp
                gp = p
                p = node
                node = node.get_child(dir)

            self._root = head.right

        # mark root black
        self._root.red = False
        return success

    def remove(self, data):
        if self._root is None:
            return False

        head = Node(None)
        node = head
        node.right = self._root

        p = None
        gp = None
        found = None

        dir = True

        while (node.get_child(dir) is not None):
            lastDir = dir

            gp = p
            p = node
            node = node.get_child(dir)

            cmp = self._comparator(data, node.data)
            dir = cmp > 0

            if cmp == 0:
                found = node

            if not is_red(node) and not is_red(node.get_child(dir)):
                if is_red(node.get_child(not dir)):
                    sr = single_rotate(node, dir)
                    p.set_child(lastDir, sr)
                    p = sr

                elif not is_red(node.get_child(not dir)):
                    sibling = p.get_child(not lastDir)
                    if sibling is not None:
                        if not is_red(sibling.left) and \
                                not is_red(sibling.right):
                            # color flip
                            p.red = False
                            sibling.red = True
                            node.red = True

                        else:
                            dir2 = gp.right is p

                            if is_red(sibling.get_child(lastDir)):
                                gp.set_child(dir2, double_rotate(p, lastDir))
                            elif is_red(sibling.get_child(not lastDir)):
                                gp.set_child(dir2, single_rotate(p, lastDir))

                            gpc = gp.get_child(dir2)
                            gpc.red = True
                            node.red = True
                            gpc.left.red = False
                            gpc.right.red = False
        # end while

        # replace and remove if found
        if found is not None:
            found.data = node.data
            p.set_child(p.right is node, node.get_child(node.left is None))
            self.size -= 1

        # update root and make it black
        self._root = head.right
        if self._root is not None:
            self._root.red = False

        return found is not None


def is_red(node):
    if node is not None and node.red is True:
        return True
    else:
        return False


def single_rotate(root, dir):
    n_dir = not dir
    save = root.get_child(n_dir)

    root.set_child(n_dir, save.get_child(dir))
    save.set_child(dir, root)

    root.red = True
    save.red = False

    return save


def double_rotate(root, dir):
    n_dir = not dir
    root.set_child(n_dir, single_rotate(root.get_child(n_dir), n_dir))
    return single_rotate(root, dir)
