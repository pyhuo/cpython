import sys

def sizeof_dict(d, n=10):
    old_size = sys.getsizeof(d)
    print(f"dicct init_size:{old_size}")
    l = 0
    for i in range(n):
        # d[i] = i
        d.append(i)
        cur_size = sys.getsizeof(d)
        if cur_size != old_size:
            print(f"i:{i} l:{l} resize old_size:{old_size} => cur_size:{cur_size}")
            old_size = cur_size
            l = 0
        else:
            l += 1
            print(f"i:{i} not resize")

def main():
    # d = list()
    # 0 4 8 
    d = [0] * 50
    sizeof_dict(d, 50)

if __name__ == "__main__":
    main()