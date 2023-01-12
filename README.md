# Zápočtový program 

Základní úloha je proložit zadané body spline funkcí, konkrétně natural splinem. V programu je možné:
- přidávat body
- odebírat body
- pohybovat s body
- pohybovat se v soustavě souřadnic (tedy posunovat graf)
- zoomovat,měnit stupeň polynomů splinů - základní je 3, je možné zvyšovat na 5, 7, 9, 11, 13. Sudé stupně jsem vynechal, protože mají lichý počet okrajových podmínek a ty křivky se nechovají tak jak bychom chtěli
- ručně měnit limity souřadnicových os
- jedním kliknutím změnit limity os tak, aby se celá křivka vešla na obrazovku a nikde nebyly nadbytečné okraje
- určit si jestli chceme nebo nechceme škálovat obě osy stejně
- určit si jestli chceme nebo nechceme automaticky měnit limity aby se křivka vždy vešla na obrazovku.

Celý program je rozdělený do 3 class. První classa slouží k vytvoření GUI pomocí knihovny PyQt5. Druhá classa slouží k vykreslení grafu a implementaci event-handlingu pomocí knihovny matplotlib. Třetí classa zajišťuje komunikaci mezi PyQt5 a matplotlibem.  

# Natural spline

We have $n+1$ points $(x_0, y_0), \dots (x_n, y_n)$ and we want to find $n$ functions $f_0, \dots f_{n-1}$ of the form $f_i = a_ix^3 + b_ix^2 + c_ix + d_i$ such that:
- $f_0(x_0) = y_0, \quad f_{n-1}(x_n) = y_n, \qquad \qquad \qquad \qquad \quad$ 2 equations
- $f_i(x_{i+1}) = f_{i+1}(x_{i+1}) = y_{i+1}, \quad 0 \leq i \leq n-2, \qquad$ 2n-2 equations
- $f'_ i(x_{i+1}) = f'_ {i+1}(x_{i+1}), \quad 0 \leq i \leq n-2, \qquad \qquad \quad$  n-1 equations
- $f''_ i(x_{i+1}) = f''_ {i+1}(x_{i+1}), \quad 0 \leq i \leq n-2. \qquad \qquad \quad$ n-1 equations
- $f''_ 0(x_0) = 0, \quad f''_ {n-1}(x_n) = 0, \qquad \qquad \qquad \qquad \qquad$ 2 equations

Note that $f'_ i = 3a_ix^2 + 2b_ix + c_i$ and $f''_ i = 6a_ix + 2b_i$.
Overall we have a system of $4n$ linear equations with $4n$ unknowns. We can make a matrix:
- rows 0 to 2n-1: $f_i(x_i) = y_i$ and $f_i(x_{i+1}) = y_{i+1}$,
- rows 2n to 3n-2: $f'_ i(x_{i+1}) - f'_ {i+1}(x_{i+1}) = 0$,
- rows 3n-1 to 4n-3: $f''_ i(x_{i+1}) - f''_ {i+1}(x_{i+1}) = 0$,
- rows 4n-2 and 4n-1: $f''_ 0(x_0) = 0$ and $f''_ {n-1}(x_n) = 0$.

With the vector of unknowns: $(a_0, b_0, c_0, d_0,\dots a_{n-1}, b_{n-1}, c_{n-1}, d_{n-1})^\text{T}$.

If we make this more general for order $m$ polynomials we have $(m+1)n$ unknows. So we have to come up with $(m+1)n$ equations. We once again want 
- $f_0(x_0) = y_0, \quad f_{n-1}(x_n) = y_n$,
- $f_i(x_{i+1}) = f_{i+1}(x_{i+1}) = y_{i+1}$.

We can set the first $m-1$ derivatives of adjacent functions to be equal in common points. This leaves us with $m-1$ more conditions we have to give. I chose that the second derivative must be equal to zero at the end points. If we need more conditions, we can just set higher order derivatives to zero at the endpoints.

