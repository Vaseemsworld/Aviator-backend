# def absolutePermutation(n, k):
#     # Write your code here
#     pos = [i for i in range(1,n+1)]
#     for i,j in enumerate(pos):
#         absolute = abs(pos[i-1]-i)
#         if absolute != k:
            
#     return pos

# print(absolutePermutation(6,2))


a = [1,2,3,4]
k = 2
b = a.copy()
for i in range(1,len(a)+1):
    if abs(a[i-1]-i) != k:
        if a[i-1]-i < k:
            print(f'{b[(i-1) + k]} =  {a[i-1]}')
            b[(i-1) + k] =  a[i-1]
        elif a[i-1]-i > k:
            print('{b[(i-1) - k]} = {a[i-1]}')
            b[(i-1) - k] = a[i-1]
    print(b)
