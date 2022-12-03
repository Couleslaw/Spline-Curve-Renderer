import numpy as np
from math import ceil
from numpy.polynomial import polynomial as pl


def binary_search(a, n):
    l = 0
    r = len(a) - 1
    while l != r:
        m = ceil((l + r)/2)
        if n < a[m]:
            r = m-1
        else:
            l = m
    return l


def update_coords_add(xs, ys, xnew, ynew):
    if len(xs) == 0:
        ind = 0
    else:
        ind = binary_search(xs, xnew)
        ind = ind if xnew < xs[0] else ind+1
    xs.insert(ind, xnew)
    ys.insert(ind, ynew)


def update_coords_del(xs, ys, xremove):
    ind = binary_search(xs, xremove)
    del xs[ind]
    del ys[ind]


def min_interval(a):
    a = sorted(a)
    min_diff = a[1] - a[0]
    for i in range(1, len(a)):
        if a[i] - a[i-1] < min_diff:
            min_diff = a[i] - a[i-1]
    return min_diff


def natural_spline(x, y):
    """
    Solves for the parameters of cubic functions that make up the spline function and returns them in a list.

    The cubics are of the form $f_i = a_i*x^3 + b_i*x^2 + c_i*x + d_i$. They satisfy the following:
        - $f_0(x_0) = y_0,  f_{n-1}(x_n) = y_n$                              --> 2 equations
        - $f''_0(x_0) = 0,  f''_{n-1}(x_n) = 0$                              --> 2 equations
        - $f_i(x_{i+1}) = f_{i+1}(x_{i+1}) = y_{i+1}$ for $0 <= i <= n-2$    --> 2n-2 equations
        - $f'_i(x_{i+1}) = f'_{i+1}(x_{i+1})$ for $0 <= i <= n-2$,           -->  n-1 equations
        - $f''_i(x_{i+1}) = f''_{i+1}(x_{i+1})$ for $0 <= i <= n-2$.         -->  n-1 equations

    None that $f'_i = 3a_ix^2 + 2b_ix + c_i$ and $f''_i = 6a_ix + 2b_i$.

    Overall we have a system of 4n linear equations with 4n unknowns. The matrix will look like:
        - rows 0 to 2n-1:     $f_i(x_i) = y_i$ and $f_i(x_{i+1}) = y_{i+1}$,
        - rows 2n to 3n-2:    $f'_i(x_{i+1}) - f'_{i+1}(x_{i+1}) = 0$,
        - rows 3n-1 to 4n-3:  $f''_i(x_{i+1}) - f''_{i+1}(x_{i+1}) = 0$,
        - rows 4n-2 and 4n-1: $f''_0(x_0) = 0$ and $f''_{n-1}(x_n) = 0$.

    The vector of unknowns will be of the form $(a_0, b_0, c_0, d_0,... a_{n-1}, b_{n-1}, c_{n-1}, d_{n-1})$.
    """

    n = len(x) - 1      # number of polynomials

    # create the SoLE matrix and vector
    matrix = np.zeros(shape=(4*n, 4*n))
    b = np.zeros(4*n)

    # rows 0 to 2n-1
    for i in range(n):
        matrix[2*i][4*i:4*i+4] = [x[i]**3, x[i]**2, x[i], 1]
        matrix[2*i+1][4*i:4*i+4] = [x[i+1]**3, x[i+1]**2, x[i+1], 1]
        b[2*i] = y[i]
        b[2*i+1] = y[i+1]

    # rows 2n to 3n-2
    for j in range(2*n, 3*n-1):
        i = j-2*n
        matrix[j][4*i:4*i+3] = [3*x[i+1]**2, 2*x[i+1], 1]
        matrix[j][4*i+4:4*i+7] = [-3*x[i+1]**2, -2*x[i+1], -1]

    # rows 3n-1 to 4n-3
    for j in range(3*n-1, 4*n-2):
        i = j - (3*n-1)
        matrix[j][4*i:4*i+2] = [6*x[i+1], 2]
        matrix[j][4*i+4:4*i+6] = [-6*x[i+1], -2]

    # rows 4n-2 and 4n-1
    matrix[4*n-2][0:2] = [6*x[0], 2]
    matrix[4*n-1][-4:-2] = [6*x[n], 2]

    v = np.linalg.solve(matrix, b).reshape((n, 4))  # solve the SoLE and reshape the result
    def f(i):
        return lambda t: v[i][0]*t**3 + v[i][1]*t**2 + v[i][2]*t + v[i][3]
    return [f(i) for i in range(n)]


def spline(x, y, m):
    """
    m is the degree of polynomials
    f_i = a_im * x^m + a_i{m-1} * x^{m-1} + ... + a_i1 * x + ai0
    The vector of unknowns will be of the form:
    $(a_00, a_01,... a_0m,... a_{n-1}0, a_{n-1}1, ...a_{n-1}m)$.
    """
    if m == 3:
        return natural_spline(x, y)
    n = len(x) - 1  # number of polynomials
    m = m + 1   # m := number of coefficients of polynomials
    # if m % 2 == 0:  # don't allow even m (asymmetric final conditions)
    #     m += 1
    # create the SoLE matrix and vector
    
    matrix = np.zeros(shape=(m * n, m * n))
    b = np.zeros(m * n)

    # rows 0 to 2n-1
    for i in range(n):
        matrix[2 * i][m*i:m*(i+1)] = [x[i] ** j for j in range(m)]
        matrix[2*i+1][m*i:m*(i+1)] = [x[i+1] ** j for j in range(m)]
        b[2 * i] = y[i]
        b[2 * i + 1] = y[i + 1]

    fder = 2
    for der in range(1, m-1):   # m-1 = degree of the polynomial
        for j in range((der+1)*n, (der+2)*n-1):
            i = j - (der+1) * n
            p = pl.polyder(np.ones(m), der)
            matrix[j][m * i + der:m*(i+1)] = [ p[k]*x[i+1]**k for k in range(m-der)]
            matrix[j][m*(i+1)+der:m*(i+2)] = [-p[k]*x[i+1]**k for k in range(m-der)]

        # matrix[(der+2)*n - 1] will be unused
        if der == m - 2 and (m-1) % 2 == 0:   # set the first derivative in the left-most point to zero for even degree
            p = pl.polyder(np.ones(m), 1)
            matrix[m*n-1][1:m] = [p[i]*x[0]**i for i in range(m-1)]
        elif der % 2 == 1:
            p = pl.polyder(np.ones(m), fder)
            matrix[(der+2)*n - 1][fder:m] = [p[k]*x[0]**k for k in range(m-fder)]
        else:
            p = pl.polyder(np.ones(m), fder)
            matrix[(der+2)*n - 1][fder-m:] = [p[k]*x[n]**k for k in range(m-fder)]
            fder += 1

    v = np.linalg.solve(matrix, b).reshape((n, m))  # solve the SoLE and reshape the result
    def f(i):
        return lambda t: pl.polyval(t, v[i])
    return [f(i) for i in range(n)]


def spline4(x, y):
    """ f_i = ax^4 + bx^3 + cx^2 + dx + e
        f'_i = 4ax^3 + 3bx^2 + 2cx + d
        f''_i = 12ax^2 + 6bx + 2c
        f'''_i = 24ax + 6b
    """

    n = len(x) - 1  # number of polynomials

    # create the SoLE matrix and vector
    matrix = np.zeros(shape=(5 * n, 5 * n))
    b = np.zeros(5 * n)

    # rows 0 to 2n-1
    for i in range(n):
        matrix[2 * i][5 * i:5 * i + 5] = [x[i] ** 4, x[i] ** 3, x[i] ** 2, x[i], 1]
        matrix[2 * i + 1][5 * i:5 * i + 5] = [x[i + 1] ** 4, x[i + 1] ** 3, x[i + 1] ** 2, x[i + 1], 1]
        b[2 * i] = y[i]
        b[2 * i + 1] = y[i + 1]

    # rows 2n to 3n-2
    for j in range(2 * n, 3 * n - 1):
        i = j - 2 * n
        matrix[j][5 * i:5 * i + 4] = [4 * x[i + 1]**3, 3 * x[i + 1] ** 2, 2 * x[i + 1], 1]
        matrix[j][5 * i + 5:5 * i + 9] = [-4 * x[i + 1]**3, -3 * x[i + 1] ** 2, -2 * x[i + 1], -1]

    # rows 3n-1 to 4n-3
    for j in range(3 * n - 1, 4 * n - 2):
        i = j - (3 * n - 1)
        matrix[j][5 * i:5 * i + 3] = [12 * x[i + 1]**2, 6 * x[i + 1], 2]
        matrix[j][5 * i + 5:5 * i + 8] = [-12 * x[i + 1]**2, -6 * x[i + 1], -2]

    # rows 4n-2 to 5n-4
    for j in range(4 * n - 2, 5 * n - 3):
        i = j - (4 * n - 2)
        matrix[j][5 * i:5 * i + 2] = [24 * x[i + 1], 6]
        matrix[j][5 * i + 5:5 * i + 7] = [-24 * x[i + 1], -6]

    # rows 5n-3 and 5n-2 --> f_0'''(x0) = f_{n-1}'''(xn) = 0
    matrix[5 * n - 3][0:2] = [24 * x[0], 6]
    matrix[5 * n - 2][-5:-3] = [24 * x[n], 6]

    # row 5n-1 --> f0''(x0) = 0
    matrix[5 * n - 1][0:3] = [12 * x[0]**2, 6 * x[0], 2]

    v = np.linalg.solve(matrix, b).reshape((n, 5))  # solve the SoLE and reshape the result

    def f(i):
        return lambda t: v[i][0] * t ** 4 + v[i][1] * t ** 3 + v[i][2] * t**2 + v[i][3] * t + v[i][4]

    return [f(i) for i in range(n)]
