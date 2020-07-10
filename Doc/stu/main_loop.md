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

            case TARGET(LOAD_CONST): {
                PREDICTED(LOAD_CONST);
                PyObject *value = GETITEM(consts, oparg);
                Py_INCREF(value);
                PUSH(value);
                FAST_DISPATCH();
            }
            ...
        }
    }
}
```