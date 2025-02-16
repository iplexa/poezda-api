
for x in range(1, 1000):
    L, M =0, 0
    original_x = x
    while x>0:
        L+=1
        M=M+x%10
        x=x//10
        if L == 3 and M == 7:
            print(original_x)
            