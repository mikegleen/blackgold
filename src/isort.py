"""
func insertionsort(A []*Node) {
    for i := 1; i < len(A); i++ {
        key := A[i]
        j := i - 1
        for j > -1 && A[j].Distance > key.Distance {
            A[j+1] = A[j]
            j -= 1
        }
        A[j+1] = key
    }
}
"""


def insertionsort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j > -1 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key


if __name__ == '__main__':
    ll = [40, 30, 20, 10]
    insertionsort(ll)
    print(ll)
