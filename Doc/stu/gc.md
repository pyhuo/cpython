## 1.gc
相关文件位置
* cpython/Include/object.h
* cpython/Modules/gcmodule.c
* cpython/Include/internal/pycore_pymem.h



## 2.CPython中的垃圾回收机制包含了两个部分

* 引用计数器机制 (大部分在 Include/object.h 中定义)
* 分代回收机制 (大部分在 Modules/gcmodule.c 中定义)

### 3.引用计数
* 创建对象时引用计数为1
* 被引用时，引用计数+1
* 变量不引用时，引用计数-1
* 引用计数为0时，释放对象

引用计数: 简单方便
无法解决: A<->B 互相引用

```c
typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;  
    PyTypeObject *ob_type;
} PyObject;
/* cpython/Include/object.h */
static inline void _Py_DECREF(const char *filename, int lineno,
                              PyObject *op)
{
    _Py_DEC_REFTOTAL;
    if (--op->ob_refcnt != 0) {
    }
    else {
    	/* // _Py_Dealloc 会找到对应类型的 descructor, 并且调用这个 descructor
        destructor dealloc = Py_TYPE(op)->tp_dealloc;
        (*dealloc)(op);
        */
        _Py_Dealloc(op);
    }
}
```


循环引用:
```py
class A:
    pass

>>> a1 = A()
>>> a2 = A()
>>> a1.other = a2
>>> a2.other = a1
```

### 4.分代回收机制
* 分代回收
* 标记清除 
* generations[3]: 0代，1代，2代


1.长时间存活的对象: 重复的对这些对象进行垃圾回收会浪费性能
2.当一个对象在一次垃圾回收后存活了, 这个对象会被移动到相近的下一代中.
代越年轻, 里面的对象也就越年轻, 年轻的代也会比年长的代更频繁的进行垃圾回收.

#### 4.1 gc 相关代码
generation0
```c
typedef struct {
    uintptr_t _gc_next;
    uintptr_t _gc_prev;
} PyGC_Head;
struct _gc_runtime_state {
    PyObject *trash_delete_later;
    int trash_delete_nesting;

    int enabled;
    int debug;
    struct gc_generation generations[NUM_GENERATIONS]; //3代数组
    PyGC_Head *generation0;
    struct gc_generation permanent_generation;
    struct gc_generation_stats generation_stats[NUM_GENERATIONS];
    int collecting;
    PyObject *garbage;
    PyObject *callbacks;
    Py_ssize_t long_lived_total;
    Py_ssize_t long_lived_pending;
};
```
首先检查 generation2, generation2 的 count 比对应的 threashold 小

CPython总共使用了3代:
* 新创建的对象都会被存储到第一代中链表尾(generation0)
* 肯定存在一个办法能追踪到所有从heap中新分配的对象

### 4.2 collect 收集流程
* 0/1/2 三代
* 1. 收集第一代:collect(generation=1)
    *  gcstate->generations[generation+1].count += 1;
    *  gcstate->generations[i].count = 0; [0, 1] 更新count为0
    *(GEN_HEAD(gcstate, i), GEN_HEAD(gcstate, generation))  gc_list_merge 合并generation 之前的代. [0, 1] 合并
    *  合并后的generation叫做young

收集函数:
* _PyObject_GC_Alloc(int use_calloc, size_t basicsize): 分配对象
* collect_generations(PyThreadState *tstate)
* collect_with_callback(PyThreadState *tstate, int generation)
* collect(tstate, generation, &collected, &uncollectable, 0);

垃圾收集的时机:
* 手动,立马执行:gc.collection(generation)
* 自动,分配对象时:_PyObject_GC_Alloc
    * gcstate->collecting = 1; 开启垃圾收集
    * collect_generations(tstate);
    * gcstate->collecting = 0; 完成垃圾收集


```c
/* This is the main function.  Read this to understand how the
 * collection process works. */
static Py_ssize_t
collect(PyThreadState *tstate, int generation,
        Py_ssize_t *n_collected, Py_ssize_t *n_uncollectable, int nofail)
{
    int i;
    Py_ssize_t m = 0; /* # objects collected */
    Py_ssize_t n = 0; /* # unreachable objects that couldn't be collected */
    PyGC_Head *young; /* the generation we are examining */
    PyGC_Head *old; /* next older generation */
    PyGC_Head unreachable; /* non-problematic unreachable trash */
    PyGC_Head finalizers;  /* objects with, & reachable from, __del__ */
    PyGC_Head *gc;
    _PyTime_t t1 = 0;   /* initialize to prevent a compiler warning */
    GCState *gcstate = &tstate->interp->gc;

    /* update collection and allocation counters */
    if (generation+1 < NUM_GENERATIONS)
        gcstate->generations[generation+1].count += 1;
    for (i = 0; i <= generation; i++)
        gcstate->generations[i].count = 0;

    /* merge younger generations with one we are currently collecting */
    for (i = 0; i < generation; i++) {
        gc_list_merge(GEN_HEAD(gcstate, i), GEN_HEAD(gcstate, generation));
    }

    /* handy references */
    young = GEN_HEAD(gcstate, generation);
    if (generation < NUM_GENERATIONS-1)
        old = GEN_HEAD(gcstate, generation+1);
    else
        old = young;
    validate_list(old, collecting_clear_unreachable_clear);

    deduce_unreachable(young, &unreachable);

    untrack_tuples(young);
    /* Move reachable objects to next generation. */
    if (young != old) {
        if (generation == NUM_GENERATIONS - 2) {
            gcstate->long_lived_pending += gc_list_size(young);
        }
        gc_list_merge(young, old);
    }
    else {
        untrack_dicts(young);
        gcstate->long_lived_pending = 0;
        gcstate->long_lived_total = gc_list_size(young);
    }

    gc_list_init(&finalizers);
    move_legacy_finalizers(&unreachable, &finalizers);
    move_legacy_finalizer_reachable(&finalizers);

    validate_list(&finalizers, collecting_clear_unreachable_clear);
    validate_list(&unreachable, collecting_set_unreachable_clear);
    /* Clear weakrefs and invoke callbacks as necessary. */
    m += handle_weakrefs(&unreachable, old);

    validate_list(old, collecting_clear_unreachable_clear);
    validate_list(&unreachable, collecting_set_unreachable_clear);
    finalize_garbage(tstate, &unreachable);

    PyGC_Head final_unreachable;
    handle_resurrected_objects(&unreachable, &final_unreachable, old);
    m += gc_list_size(&final_unreachable);
    delete_garbage(tstate, gcstate, &final_unreachable, old);
    for (gc = GC_NEXT(&finalizers); gc != &finalizers; gc = GC_NEXT(gc)) {
        n++;
        if (gcstate->debug & DEBUG_UNCOLLECTABLE)
            debug_cycle("uncollectable", FROM_GC(gc));
    }
    handle_legacy_finalizers(tstate, gcstate, &finalizers, old);
    validate_list(old, collecting_clear_unreachable_clear);
    if (generation == NUM_GENERATIONS-1) {
        clear_freelists(tstate);
    }
    struct gc_generation_stats *stats = &gcstate->generation_stats[generation];
    stats->collections++;
    stats->collected += m;
    stats->uncollectable += n;

    if (PyDTrace_GC_DONE_ENABLED()) {
        PyDTrace_GC_DONE(n + m);
    }
    return n + m;
}
```

首先检查 generation2, generation2 的 count 比对应的threashold小, 收集.
收集generation1时，合并所有小于generation2的代，标记为young。
在收集活下来的进入下一代。

```c
 for (int i = NUM_GENERATIONS-1; i >= 0; i--) {
        // 10, 10, 700
        if (gcstate->generations[i].count > gcstate->generations[i].threshold) {
            if (i == NUM_GENERATIONS - 1
                && gcstate->long_lived_pending < gcstate->long_lived_total / 4)
                continue;
            n = collect_with_callback(tstate, i);
            break;
        }
    }
```

#### 4.3 free_list 
* 当最高代完成收集时. 调用clear_freelists，清理所有的freelist
* 所有PyObject对象在创建时连接到GC链表中.

```c
/* Clear all free lists
 * All free lists are cleared during the collection of the highest generation.
 * Allocated items in the free list may keep a pymalloc arena occupied.
 * Clearing the free lists may give back memory to the OS earlier.
 */
static void
clear_freelists(PyThreadState *tstate)
{
    _PyFrame_ClearFreeList(tstate);
    _PyTuple_ClearFreeList(tstate);
    _PyFloat_ClearFreeList(tstate);
    _PyList_ClearFreeList(tstate);
    _PyDict_ClearFreeList(tstate);
    _PyAsyncGen_ClearFreeLists(tstate);
    _PyContext_ClearFreeList(tstate);
}
void
_PyList_ClearFreeList(PyThreadState *tstate)
{
    // 获取当前解释器中的list缓存池.
    struct _Py_list_state *state = &tstate->interp->list;
    while (state->numfree) {
        PyListObject *op = state->free_list[--state->numfree];
        assert(PyList_CheckExact(op));
        PyObject_GC_Del(op);
    }
}
```
