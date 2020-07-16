## main.c

Modules/main.c:pymain_main 入口函数



### ceval.c: 
* Python/celval.c

main_loop:
    加载编译后的代码，循环解析.

## 02:python代码==>汇编==>python解释器解析汇编指令

### 02.1 python 文件test.py
```python
#!/bin/python
def foo(x):
    return x ** 2
    
def bar(x):
    y = x /2
    return y
```
### 02.2 源码转为汇编指令
* fram
* function 
* code object
* bytecode

```shell
➜  cpython git:(hyh_debug) ✗ ./python.exe -m dis Doc/stu/test.py 
  2           0 LOAD_CONST               0 (<code object foo at 0x10f94e9d0, file "Doc/stu/test.py", line 2>)
              2 LOAD_CONST               1 ('foo')
              4 MAKE_FUNCTION            0
              6 STORE_NAME               0 (foo)

  5           8 LOAD_CONST               2 (<code object bar at 0x10f94ea80, file "Doc/stu/test.py", line 5>)
             10 LOAD_CONST               3 ('bar')
             12 MAKE_FUNCTION            0
             14 STORE_NAME               1 (bar)
             16 LOAD_CONST               4 (None)
             18 RETURN_VALUE

Disassembly of <code object foo at 0x10f94e9d0, file "Doc/stu/test.py", line 2>:
  3           0 LOAD_FAST                0 (x)
              2 LOAD_CONST               1 (2)
              4 BINARY_POWER
              6 RETURN_VALUE

Disassembly of <code object bar at 0x10f94ea80, file "Doc/stu/test.py", line 5>:
  6           0 LOAD_FAST                0 (x)
              2 LOAD_CONST               1 (2)
              4 BINARY_TRUE_DIVIDE
              6 STORE_FAST               1 (y)

  7           8 LOAD_FAST                1 (y)
             10 RETURN_VALUE
exitcode:-521753028
➜  cpython git:(hyh_debug) ✗ 
```

### 02.3 python解释器解析汇编指令
* 源码路径:Python/ceval.c
* 调用函数指令解析.

```c
PyObject* _Py_HOT_FUNCTION
_PyEval_EvalFrameDefault(PyThreadState *tstate, PyFrameObject *f, int throwflag)
{
    ...
main_loop:
    for (;;) {
        switch (opcode) {
            case TARGET(NOP): {
                FAST_DISPATCH();
            }
            // 函数名入栈
            case TARGET(LOAD_NAME): {
                PyObject *name = GETITEM(names, oparg);
                PyObject *locals = f->f_locals;
                PyObject *v;
                // 是否是关键字参数
                if (PyDict_CheckExact(locals)) {
                    // 获取
                    v = PyDict_GetItemWithError(locals, name);
                    if (v != NULL) {
                        // 增加引用
                        Py_INCREF(v);
                    }
                }
                else {
                    v = PyObject_GetItem(locals, name);
                }
                // v入栈
                PUSH(v);
                DISPATCH();
            }
            // 变量入栈
            case TARGET(LOAD_CONST): {
                PREDICTED(LOAD_CONST);
                PyObject *value = GETITEM(consts, oparg);
                Py_INCREF(value);
                PUSH(value);
                FAST_DISPATCH();
            }
            /* 
             * 1.函数调用
             *   a.出栈获取函数名
             *   b.出栈获取变量.
             *   c.函数调用, 获取函数结果.
             *   c.压入栈
             */
            case TARGET(CALL_FUNCTION): {
                PREDICTED(CALL_FUNCTION);
                // sp栈指针， res返回结果
                PyObject **sp, *res;
                sp = stack_pointer;
                // 函数调用，获取返回值，压入栈
                res = call_function(tstate, &sp, oparg,NULL);
                stack_pointer = sp;
                PUSH(res);
                if (res == NULL) {
                    goto error;
                }
                DISPATCH();
            }
            ...
        }
    }
}
```

call_function: 解析
```c
```

## 04 python一切皆对象
版本:
```shell
➜  cpython git:(hyh_debug) ✗ ./python.exe --version
Python 3.10.0a0
➜  cpython git:(hyh_debug) ✗ 
```

相关目录:
* Include/object.h
* Objects/object.c


### 0401 Python Object protocol
* id: 使用id函数查看, 通常是对象的地址, 一旦创建就不可变。
* type: 通过type函数查看, 返回对象的类型, 一旦创建就不可变。
* 值: 
    * 可变: mutable, list
    * 不可变: immutable, tuple

* refcount: 引用计数。
    * del: 引用计数减少.
    * gc: 垃圾回收机制，自动清除。


### 0402 PyObject
<!-- *.h 定义
*.c 该类型API的实现 -->
* Include/object.h 
* 引用计数
* 类型

PyObject: object.h
```c
typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;  //引用计数
    PyTypeObject *ob_type; //类型
} PyObject;

/* PyObject_HEAD defines the initial segment of every PyObject. */
#define PyObject_HEAD   PyObject ob_base;

typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size; /* Number of items in variable part */
} PyVarObject;

typedef struct _typeobject PyTypeObject;
```

Objects/object.c

API:
```c

```


### 0403 float

* Include/floatobject.h 
* Include/floatobject.c 

float:floatobject.c

```c
typedef struct {
    PyObject_HEAD
    double ob_fval;
} PyFloatObject;
```

### 0404 list
list: listobject.h
list: api 的实现在listobject.c中

```c
typedef struct {
    PyObject_VAR_HEAD
    /* Vector of pointers to list elements.  list[0] is ob_item[0], etc. */
    PyObject **ob_item;

    /* ob_item contains space for 'allocated' elements.  The number
     * currently in use is ob_size.
     * Invariants:
     *     0 <= ob_size <= allocated
     *     len(list) == ob_size
     *     ob_item == NULL implies ob_size == allocated == 0
     * list.sort() temporarily sets allocated to -1 to detect mutations.
     *
     * Items must normally not be NULL, except during construction when
     * the list is not yet visible outside the function that builds it.
     */
    Py_ssize_t allocated;
} PyListObject;

```

### 0404 func对象
func:funcobject.h
```c
typedef struct {
    PyObject_HEAD
    PyObject *func_code;        /* A code object, the __code__ attribute */
    PyObject *func_globals;     /* A dictionary (other mappings won't do) */
    PyObject *func_defaults;    /* NULL or a tuple */
    PyObject *func_kwdefaults;  /* NULL or a dict */
    PyObject *func_closure;     /* NULL or a tuple of cell objects */
    PyObject *func_doc;         /* The __doc__ attribute, can be anything */
    PyObject *func_name;        /* The __name__ attribute, a string object */
    PyObject *func_dict;        /* The __dict__ attribute, a dict or NULL */
    PyObject *func_weakreflist; /* List of weak references */
    PyObject *func_module;      /* The __module__ attribute, can be anything */
    PyObject *func_annotations; /* Annotations, a dict or NULL */
    PyObject *func_qualname;    /* The qualified name */
    vectorcallfunc vectorcall;

    /* Invariant:
     *     func_closure contains the bindings for func_code->co_freevars, so
     *     PyTuple_Size(func_closure) == PyCode_GetNumFree(func_code)
     *     (func_closure may be NULL if PyCode_GetNumFree(func_code) == 0).
     */
} PyFunctionObject;
```




