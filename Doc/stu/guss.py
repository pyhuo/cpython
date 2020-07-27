pick = 6

def guess(num):
    if num == pick:
        return 0
    elif num > pick:
        return 1
    else:
        return -1

def guessNum(n):
    l, r, ans = 0, n, -1 
    while l < r:
        mid = (l + r) // 2
        ret = guess(mid)
        print(f"l:{l} r:{r} m:{mid} ret:{ret}")
        if ret == 0:
            return mid
        elif ret > 0:
            r = mid - 1
        elif ret < 0:
            l = mid + 1
    return ans

def main():
    ret = guessNum(10)
    print(f"ret:{ret}")


if __name__ == "__main__":
    main()