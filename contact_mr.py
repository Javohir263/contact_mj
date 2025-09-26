def f(a):
    def g(b):
        return b + b
    def h(a):
        a = a + 2
        return  a
    return h


a = 5
b = 1

h = f(a)
natijs = h(b)

print(natijs)
