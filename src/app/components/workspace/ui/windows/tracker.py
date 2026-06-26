from PyQt5.QtCore import QRect


class GeometryTracker:
    def __init__(self):
        self.top = []
        self.bottom = []
        self.left = []
        self.right = []

        self.indexTop = {}
        self.indexBottom = {}
        self.indexLeft = {}
        self.indexRight = {}

    def addGeometry(self, id: str, rect: QRect):
        self._insert_sorted(self.top, self.indexTop, rect.top(), id)
        self._insert_sorted(self.bottom, self.indexBottom, rect.bottom(), id)
        self._insert_sorted(self.left, self.indexLeft, rect.left(), id)
        self._insert_sorted(self.right, self.indexRight, rect.right(), id)

    def _insert_sorted(self, arr, indexMap, value, id):
        arr.append((value, id))
        i = len(arr) - 1
        indexMap[id] = i

        # bubble left until sorted
        while i > 0 and arr[i][0] < arr[i - 1][0]:
            self._swap(arr, indexMap, i, i - 1)
            i -= 1

    def _swap(self, arr, indexMap, i, j):
        arr[i], arr[j] = arr[j], arr[i]

        id_i = arr[i][1]
        id_j = arr[j][1]

        indexMap[id_i] = i
        indexMap[id_j] = j

    def updateGeometry(self, id, rect: QRect):
        self._update_axis(self.top, self.indexTop, id, rect.top())
        self._update_axis(self.bottom, self.indexBottom, id, rect.bottom())
        self._update_axis(self.left, self.indexLeft, id, rect.left())
        self._update_axis(self.right, self.indexRight, id, rect.right())

    def _update_axis(self, arr, indexMap, id, new_value):
        i = indexMap[id]

        value, _ = arr[i]
        arr[i] = (new_value, id)

        # move left if smaller
        while i > 0 and arr[i][0] < arr[i - 1][0]:
            self._swap(arr, indexMap, i, i - 1)
            i -= 1

        # move right if larger
        while i < len(arr) - 1 and arr[i][0] > arr[i + 1][0]:
            self._swap(arr, indexMap, i, i + 1)
            i += 1

    def removeGeometry(self, id):
        self._remove_axis(self.top, self.indexTop, id)
        self._remove_axis(self.bottom, self.indexBottom, id)
        self._remove_axis(self.left, self.indexLeft, id)
        self._remove_axis(self.right, self.indexRight, id)

    def _remove_axis(self, arr, indexMap, id):
        i = indexMap.pop(id)

        # remove the element
        arr.pop(i)

        # fix indices of shifted elements
        for j in range(i, len(arr)):
            _, other_id = arr[j]
            indexMap[other_id] = j

    def boundingBox(self):
        if not self.left:
            return QRect()
        return QRect(
            self.left[0][0],
            self.top[0][0],
            self.right[-1][0] - self.left[0][0] + 1,
            self.bottom[-1][0] - self.top[0][0] + 1,
        )
