# Natural spline

We have $n+1$ points of the form $(x_0, y_0), \dots (x_n, y_n)$ and we want to find $n$ functions $f_0, \dots f_{n-1}$ of the form $f_i = a_ix^3 + b_ix^2 + c_ix + d_i$ such that:
- $f_0(x_0) = y_0, \quad f_{n-1}(x_n) = y_n, \qquad \qquad \qquad \qquad \qquad \qquad$ 2 equations
- $f''_ 0(x_0) = 0, \quad f''_ {n-1}(x_n) = 0, \qquad \qquad \qquad \qquad \qquad \qquad$ 2 equations
- $f_i(x_{i+1}) = f_{i+1}(x_{i+1}) = y_{i+1}$ for $0 \leq i \leq n-2$, $\qquad \qquad$ 2n-2 equations
- $f'_i(x_{i+1}) = f'_{i+1}(x_{i+1})$ for $0 \leq i \leq n-2$, $\qquad$ $\qquad$  n-1 equations
- $f''_i(x_{i+1}) = f''_{i+1}(x_{i+1})$ for $0 \leq i \leq n-2$. $\qquad$ $\qquad$ n-1 equations

None that $f'_i = 3a_ix^2 + 2b_ix + c_i$ and $f''_i = 6a_ix + 2b_i$.
Overall we have a system of $4n$ linear equations with $4n$ unknowns. The matrix will look like:
- rows 0 to 2n-1: $f_i(x_i) = y_i$ and $f_i(x_{i+1}) = y_{i+1}$,
- rows 2n to 3n-2: $f'_i(x_{i+1}) - f'_{i+1}(x_{i+1}) = 0$,
- rows 3n-1 to 4n-3: $f''_i(x_{i+1}) - f''_{i+1}(x_{i+1}) = 0$,
- rows 4n-2 and 4n-1: $f''_0(x_0) = 0$ and $f''_{n-1}(x_n) = 0$.

The vector of unknowns will be of the form $(a_0, b_0, c_0, d_0,\dots a_{n-1}, b_{n-1}, c_{n-1}, d_{n-1})^\text{T}$.

