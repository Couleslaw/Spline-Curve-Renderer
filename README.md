# Interactive natural spline curve

Natural splines are a way to interpolate a set of points with a smooth curve. The curve is made up of multiple polynomials, each defined on a different interval. This program allows you to add, delete, and move points and see the spline curve change in real-time. See [this section](#math-of-natural-splines) for exact details on how natural splines are defined.

## How to install

Windows users can download an executable file from the [releases page](https://github.com/Couleslaw/Spline-Curve-Renderer/releases/latest). Linux and MacOS users can run the program by following the instructions below.

## Dependencies

This project is not compatible with the newer versions of matplotlib. It works with version 3.6.2. I recommend creating a virtual environment and installing the dependencies from the `requirements.txt` file.

Create and activate the virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Run the program with:

```bash
python3 main.py
```

Deactivate the virtual environment by running `deactivate`.

## User documentation

There are three modes which the program can be in. They can be switched via three radio buttons in the top-left corner.

- Add points mode - lets you add new points at the location where you clicked.
- Delete points mode - removes the point on which you cliked.
- Move points mode - lets you pick up and move points.

The spline function is redrawn automatically whenever anything changes.

### Adding new points

- New points can be added either by right-clicking or by selecting the 'Add points' mode and left-clicking.
- The point will appear at the location where you clicked.

### Deleting existing points

- Existing points can be removed by selecting the 'Delete points' mode and left-clicking on them.
- All points can be deleted by clicking on the 'Delete all' button.

### Moving points

- Points can be picked up and dragged by selecting the 'Move points' mode and using the left mouse button.

### Movement in the figure

- The graph can be moved by left-clicking and dragging.
- This doesn't work when in the 'Add points' mode because a new point will be added instead.
- You can also zoom.

### Changing the limits of the coordinate axes

- Limits can be changed manually.
- If the graph does not fit on the screen, limits can be adjusted accordingly by clicling on the 'Fit to screen' button.
- If you toggle 'Auto adjust' this will always be the case.
- If you want equal scaling on both axes you should toggle 'Equal axes.'
- 'Auto adjust' and 'Equal axes' cannot be toggled at the same time.
- You can't change limits manually while 'Auto adjust' or 'Equal axes' is toggled.
- Original limits are restored if there was no user-movement in the figure while either of these was toggled.

### Changing the degree of splines

- The default degree is 3.
- Degree can be changed via a slider with values 3, 5, 7, 9, 11, 13.
- The degree can't be changed while moving a point.
- The slider can be incrementing using arrow-keys (if it is focused).
- You can change focus to the slider by pressing 'Alt+d.'

## How does it work?

The whole program is divided into 3 classes. The first class is used to create the GUI using the PyQt5 library. The second class is used to draw the graph and implement event-handling using the matplotlib library. The third class is used to communicate between PyQt5 and matplotlib.

## Math of natural splines

We have $n+1$ points $(x_0, y_0), \dots (x_n, y_n)$ and we want to find $n$ functions $f_0, \dots f_{n-1}$ of the form $f_i = a_ix^3 + b_ix^2 + c_ix + d_i$ such that:

- $f_0(x_0) = y_0, \quad f_{n-1}(x_n) = y_n$
- $f_i(x_{i+1}) = f_{i+1}(x_{i+1}) = y_{i+1}, \quad 0 \leq i \leq n-2$
- $f'_ i(x_{i+1}) = f'_ {i+1}(x_{i+1}), \qquad\qquad 0 \leq i \leq n-2$
- $f''_ i(x_{i+1}) = f''_ {i+1}(x_{i+1}), \qquad\quad\,\,\,\,\, 0 \leq i \leq n-2$
- $f''_ 0(x_0) = 0, \quad f''_ {n-1}(x_n) = 0$

Note that $f'_ i = 3a_ix^2 + 2b_ix + c_i$ and $f''_ i = 6a_ix + 2b_i$.
Overall we have a system of $4n$ linear equations with $4n$ unknowns which can be solved using linear algebra.

If we make this more general for order $m$ polynomials we have $(m+1)n$ unknows. So we have to come up with $(m+1)n$ equations. We once again want

- $f_0(x_0) = y_0, \quad f_{n-1}(x_n) = y_n$,
- $f_i(x_{i+1}) = f_{i+1}(x_{i+1}) = y_{i+1}$.

We can set the first $m-1$ derivatives of adjacent functions to be equal in common points. This leaves us with $m-1$ more conditions we have to give. I chose that the second derivative must be equal to zero at the end points. If we need more conditions for higher order polynomials, we can just set higher order derivatives to zero at the endpoints.
