import sys


def print_list_size(nums=None):
    nums_size = sys.getsizeof(nums)
    if nums:
        print(f"id({id(nums)}) v:{nums[-1]} len:{len(nums)} size:{nums_size}")
    else:
        print(f"id({id(nums)}) v:{nums} len:{len(nums)} size:{nums_size}")


def test_0_4():
    data = []
    print_list_size(nums=data)
    for i in range(1, 35):
        data.append(i)
        print_list_size(nums=data)


test_0_4()

def resize_list(x):
    return (x + (x >> 3) + 6) & (~3)

"""

## 3.9
Add padding to make the allocated size multiple of 4
The growth pattern is:  0, 4, 8, 16, 24, 32, 40, 52, 64, 76
https://github.com/python/cpython/blob/3.9/Objects/listobject.c
new_allocated = ((size_t)newsize + (newsize >> 3) + 6) & ~(size_t)3;

id(4554271168) v:[] len:0 size:56
id(4554271168) v:1 len:1 size:88
id(4554271168) v:2 len:2 size:88
id(4554271168) v:3 len:3 size:88
id(4554271168) v:4 len:4 size:88
id(4554271168) v:5 len:5 size:120
id(4554271168) v:6 len:6 size:120
id(4554271168) v:7 len:7 size:120
id(4554271168) v:8 len:8 size:120
id(4554271168) v:9 len:9 size:184
id(4554271168) v:10 len:10 size:184
id(4554271168) v:11 len:11 size:184
id(4554271168) v:12 len:12 size:184
id(4554271168) v:13 len:13 size:184
id(4554271168) v:14 len:14 size:184
id(4554271168) v:15 len:15 size:184
id(4554271168) v:16 len:16 size:184
id(4554271168) v:17 len:17 size:248
id(4554271168) v:18 len:18 size:248
id(4554271168) v:19 len:19 size:248
id(4539054528) v:20 len:20 size:248
id(4539054528) v:21 len:21 size:248
id(4539054528) v:22 len:22 size:248
id(4539054528) v:23 len:23 size:248
id(4539054528) v:24 len:24 size:248
id(4506298816) v:25 len:25 size:312
id(4506298816) v:26 len:26 size:312
id(4506298816) v:27 len:27 size:312
id(4506298816) v:28 len:28 size:312
id(4506298816) v:29 len:29 size:312
id(4506298816) v:30 len:30 size:312
id(4506298816) v:31 len:31 size:312
id(4506298816) v:32 len:32 size:312
id(4506298816) v:33 len:33 size:376
id(4506298816) v:34 len:34 size:376


## 3.7/3.8
The growth pattern is: 0, 4, 8, 16, 25, 35, 46, 58, 72, 88
https://github.com/python/cpython/blob/3.7/Objects/listobject.c
https://github.com/python/cpython/blob/3.8/Objects/listobject.c

new_allocated = (size_t)newsize + (newsize >> 3) + (newsize < 9 ? 3 : 6);

(py3) ➜  stu git:(hyh_debug_01_main) ✗ python --version 
Python 3.7.4
(py3) ➜  stu git:(hyh_debug_01_main) ✗ python test_list_resize.py 
id(4538606048) v:[] len:0 size:72
id(4538606048) v:1 len:1 size:104
id(4538606048) v:2 len:2 size:104
id(4538606048) v:3 len:3 size:104
id(4538606048) v:4 len:4 size:104       4个空间使用完. 增加4
id(4538606048) v:5 len:5 size:136
id(4538606048) v:6 len:6 size:136
id(4538606048) v:7 len:7 size:136
id(4538606048) v:8 len:8 size:136       8个空间使用完. 增加4
id(4538606048) v:9 len:9 size:200
id(4538606048) v:10 len:10 size:200
id(4538606048) v:11 len:11 size:200
id(4538606048) v:12 len:12 size:200
id(4538606048) v:13 len:13 size:200
id(4538606048) v:14 len:14 size:200
id(4538606048) v:15 len:15 size:200
id(4538606048) v:16 len:16 size:200    16个空间使用完. 增加8
id(4538606048) v:17 len:17 size:272
id(4538606048) v:18 len:18 size:272
id(4538606048) v:19 len:19 size:272
id(4538606048) v:20 len:20 size:272
id(4538606048) v:21 len:21 size:272
id(4538606048) v:22 len:22 size:272
id(4538606048) v:23 len:23 size:272
id(4538606048) v:24 len:24 size:272
id(4538606048) v:25 len:25 size:272    25个空间使用完. 增加9
id(4538606048) v:26 len:26 size:352
id(4538606048) v:27 len:27 size:352
id(4538606048) v:28 len:28 size:352
id(4538606048) v:29 len:29 size:352
id(4538606048) v:30 len:30 size:352
id(4538606048) v:31 len:31 size:352
id(4538606048) v:32 len:32 size:352
id(4538606048) v:33 len:33 size:352
id(4538606048) v:34 len:34 size:352
# 关于size不一致问题，_typeobject 类型对象结构体在py3.9中删除了部分元素比3.8更小
"""