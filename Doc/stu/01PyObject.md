## 01 PyObject
[参考](https://github.com/zpoint/CPython-Internals/blob/master/Interpreter/pyobject/pyobject_cn.md)
* 定长对象与变长对象
* 类型对象


### 0101.相关位置文件
* cpython/Include/object.h
* cpython/Include/cpython/object.h
* cpython/Python/ceval.c
* cpython/Include/ceval.h
* cpython/Python/pythonrun.c


### 0102.内存构造
* PyObject
    * _PyObject_HEAD_EXTRA: 维护所有在堆中对象的双向链表
    * ob_refcnt: 变量引用次数, 与内存管理有关
    * ob_type: 对象的类型信息, 诸如int, string, function等
* PyVarObject: 
    * ob_base: PyObject
    * ob_size: 元素的个数
* PyObject_HEAD: 定义每个PyObject的初始段。
* PyObject_VAR_HEAD: 定义每个PyVarObject的初始化段。


```c
/* Define pointers to support a doubly-linked list of all live heap objects. */
#define _PyObject_HEAD_EXTRA            \
    struct _object *_ob_next;           \
    struct _object *_ob_prev;

typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;   //引用计数
    PyTypeObject *ob_type;  //对象类型
} PyObject;

typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size; /* Number of items in variable part */
} PyVarObject;             //变长对象

#define PyObject_HEAD   PyObject ob_base
#define PyObject_VAR_HEAD PyVarObject ob_base
```

built-in:
* type: PyType_Type
* object: PyBaseObject_Type
* supper: PySuper_Type

ob_size 表示容纳元素的个数, 不是对象占用的内存字节数:

|int	        |string	    |list	    |dict
| ------        |----       |---        | ---
|ob_refnt	    |ob_refnt	|ob_refnt	|ob_refnt
|ob_type	    |ob_type	|ob_type	|ob_type
|ob_digit[1]	|ob_size	|ob_size	|其他信息
|空	其他信息	  |其他信息	   |空         | 空