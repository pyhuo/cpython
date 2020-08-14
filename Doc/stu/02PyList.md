## 相关文件
* cpython/Objects/listobject.c
* cpython/Objects/clinic/listobject.c.h
* cpython/Include/listobject.h
* cpython/Objects/listsort.txt

## 成员
* ob_size
* ob_item 指针
* allocated 真实的内存容量

```
1. 0 <= ob_size <= allocated
2. len(list) == ob_size
3. ob_item == NULL 意味着 ob_size == allocated == 0
```

## 方法
* get_list_state: 解释器中list池.interp->list->free_list
* PyList_New->PyObject_GC_New
* PyList_Append


### PyList_New
```pythno
data = list()
data = []
data = [0] * 10
```
```c
PyObject *
PyList_New(Py_ssize_t size)
{
    // step1: 获取解释器中interp->list
    struct _Py_list_state *state = get_list_state();
    PyListObject *op;
    if (state->numfree) { // 有空闲的list
        state->numfree--;
        op = state->free_list[state->numfree];
        _Py_NewReference((PyObject *)op);
    }
    else {               // 没有空闲的list
        op = PyObject_GC_New(PyListObject, &PyList_Type);
    }
    if (size <= 0) {
        op->ob_item = NULL; // list(), data = [] 空列表
    }
    else {
        op->ob_item = (PyObject **) PyMem_Calloc(size, sizeof(PyObject *));
        if (op->ob_item == NULL) {
            Py_DECREF(op);
            return PyErr_NoMemory();
        }
    }
    Py_SET_SIZE(op, size);  // 可变对象，ob_size 为元素个数
    op->allocated = size;   // 初始相等, 扩容后 0<= ob_size <= allocated
    _PyObject_GC_TRACK(op);
    return (PyObject *) op;
}
```

