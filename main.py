from spline_functions import binary_search, update_coords, min_interval, spline
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QSlider,
    QLineEdit,
    QCheckBox,
    QRadioButton
)

# constants
DEFAULT_xmin = -10
DEFAULT_xmax = 10
DEFAULT_ymin = -10
DEFAULT_ymax = 10

MIN_freq = 100
MAX_len_linspace = 2**18        # max size for int64 will be 2**21B = 2MB
MIN_INTERVAL_num_points = 100

MIN_deg = 3
DEFAULT_deg = 3
MAX_deg = 13

ROUND_input_lines = 7
ZOOM = 2
MAX_zoom = 5e-3


class SplineCurvesBuilder:
    """Plots spline curves using the matplotlib library."""
    def __init__(self, points, app):
        self.press = None               # holds x, y of pressed point while moving, else None
        self.moving_canvas = False      # True if moving canvas, else False
        self.moving_point = False       # True if moving a point on canvas, else False
        self.points = points            # 'points' given to the constructor will be a Line2D ax.plot([0], [0]) object
                                        # we need it to access points.figure.canvas
        self.polynomials = None         # spline functions will be stored here
        self.app = app                  # the MyApp object SCB is embedded in
        self.xs = []                    # x coordinates of the points
        self.ys = []                    # y coordinates of the points
        self.degree = DEFAULT_deg       # degree of the spline function

    def connect(self):
        """Connect to all the events we need."""
        self.cicpick = self.points.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.cidpress = self.points.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.points.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.points.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidzoom = self.points.figure.canvas.mpl_connect('scroll_event', self.on_scroll)

    def on_press(self, event):
        """
        Creates a new point if the 'Add points' button is checked. Otherwise:
        Creates a new point if the right mouse button was clicked.
        Begins canvas movement if the left mouse button was clicked and 'Add points' and 'Auto adjust' are not checked.
        Exception: event.xdata is in self.xs --> does not create a new point because the curve would not be defined.
        """
        if event.inaxes != self.points.axes or self.moving_point:
            return

        if (MyApp.add_point or event.button == 3) and event.xdata not in self.xs:    # create a new point
            update_coords(self.xs, self.ys, event.xdata, event.ydata)
            self.create_spline(self.xs, self.ys)

        elif event.button == 1 and not MyApp.auto_adjust:  # left mouse button --> begin canvas movement
            self.moving_canvas = True
            # redraw the whole spline (so that we don't have to redraw it while moving the canvas)
            self.create_spline(self.xs, self.ys)
            self.press = (event.xdata, event.ydata)

    def on_pick(self, event):
        """
        Deletes the selected point if the 'Delete points' button checked.
        Begins point movement if the 'Move points' button checked.
        Works only for left mouse button.
        """
        if self.press is not None or MyApp.add_point or event.mouseevent.button != 1:
            return

        ind = event.ind[0]  # point index
        x = self.points.get_xdata()[ind]    # coords of the point
        y = self.points.get_ydata()[ind]

        if MyApp.delete_point:  # delete the point
            self.xs.remove(x)
            self.ys.remove(y)
            self.create_spline(self.xs, self.ys)
        elif MyApp.move_point_or_canvas:   # begin point movement
            self.press = (x, y)
            self.moving_point = True
            # self.remove_point = True    # the point will be deleted and replaced by a new point upon mouse movement
            self.app.slider.setEnabled(False)   # disable changing degree

    def on_motion(self, event):
        """ Changes axes lims if moving_canvas, draws spline curves if moving_point."""
        if self.press is None or event.inaxes != self.points.axes:
            return
        xlast, ylast = self.press

        if self.moving_canvas:
            dx, dy = event.xdata - xlast, event.ydata - ylast
            self.points.axes.set_xlim([x - dx for x in self.points.axes.get_xlim()])
            self.points.axes.set_ylim([y - dy for y in self.points.axes.get_ylim()])
            self.app.update_displayed_lims()
            self.points.figure.canvas.draw()

        elif self.moving_point:
            if event.xdata not in self.xs: # update coords if the new x coordinate is valid
                self.xs.remove(xlast)
                self.ys.remove(ylast)
                self.press = (event.xdata, event.ydata)     # remember the coord if they are valid
                update_coords(self.xs, self.ys, event.xdata, event.ydata)
            self.create_spline(self.xs, self.ys)

    def on_release(self, event):
        """Stops canvas movement or point movement."""
        if self.press is None or event.inaxes != self.points.axes:
            return

        if self.moving_canvas:
            self.moving_canvas = False
            self.create_spline(self.xs, self.ys)
        elif self.moving_point:
            self.moving_point = False
            self.app.slider.setEnabled(True)   # enable changing degree
        self.press = None

    def on_scroll(self, event):
        """Zooms in and out based on 'ZOOM' by scaling the x and y lims accordingly.
        Doesn't zoom if 'Auto adjust' is checked."""
        if event.inaxes != self.points.axes or MyApp.auto_adjust:
            return

        margin = (ZOOM - 1) / 2     # how much to add on both sides
        (xmin, xmax), (ymin, ymax) = self.points.axes.get_xlim(), self.points.axes.get_ylim()
        xleft, xright, ydown, yup = event.xdata - xmin, xmax - event.xdata, event.ydata - ymin, ymax - event.ydata

        if event.button == "down":  # zoom out
            xlim = (xmin - margin * xleft, xmax + margin * xright)
            ylim = (ymin - margin * ydown, ymax + margin * yup)
        else:   # zoom in
            if xmax - xmin < MAX_zoom:  # if max zoom has been reached
                return
            margin = margin / ZOOM
            xlim = (xmin + margin * xleft, xmax - margin * xright)
            ylim = (ymin + margin * ydown, ymax - margin * yup)

        self.points.axes.set_xlim(xlim)
        self.points.axes.set_ylim(ylim)
        self.app.update_displayed_lims()
        self.create_spline(self.xs, self.ys)

    def create_spline(self, xs, ys):
        """Calculates polynomials and draws the spline function for the coords given."""
        xs, ys = np.array(xs), np.array(ys)
        xlim = self.points.axes.get_xlim()  # save old lims
        ylim = self.points.axes.get_ylim()
        self.points.axes.cla()
        if not MyApp.auto_adjust:  # set old lims if auto_adjust is off
            self.points.axes.set_xlim(xlim)
            self.points.axes.set_ylim(ylim)

        if len(xs) >= 2:        # calculate spline if it is defined
            self.polynomials = spline(xs, ys, self.degree)
            if MyApp.auto_adjust:   # the graph takes up all screen
                t = np.sort(np.concatenate([xs, np.linspace(xs[0], xs[-1], 1+int(self.app.width()))]))
            # it would be slow to redraw the spline while moving, so we
            # just draw it with a lot of points and that only change lims
            elif self.moving_canvas:
                freq = max(MIN_freq, MIN_INTERVAL_num_points / min_interval(xs))
                # len(t) ~ freq * (xs[-1] - xs[0])
                freq = min(freq, MAX_len_linspace / (xs[-1] - xs[0]))
                t = np.sort(np.concatenate([xs, np.linspace(xs[0], xs[-1], 1+int(freq * (xs[-1] - xs[0])))]))
            else:
                xmin, xmax = max(xlim[0], xs[0]), min(xlim[1], xs[-1])
                xrange, xmaxrange = xmax - xmin, xlim[1] - xlim[0]
                c = 0 if xrange < 0 else xrange / xmaxrange   # c = 0 if all points are off screen
                t = np.sort(np.concatenate([xs, np.linspace(xmin, xmax, 1+int(c * self.app.width()))]))

            s = t.copy()
            start = 0
            for i in range(len(xs)-1):
                end = binary_search(t, xs[i+1])
                s[start:end+1] = self.polynomials[i](t[start:end+1])
                start = end
            self.points.axes.plot(t, s)

        # draw the points, picker=True allows us to use the 'pick_event'
        self.points, = self.points.axes.plot(xs, ys, "o", c="r", picker=True, pickradius=5)
        self.points.figure.canvas.draw()


class Canvas(FigureCanvas):
    """Ensures communication between the matplotlib figure and PyQt5 GUI."""
    def __init__(self, parent):     # parent is the QtWidget object the figure will be embedded in
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.setParent(parent)
        self.parent = parent
        self.pyplot_code()

    def pyplot_code(self):
        """Create the SplineCurvesBuilder object and set default parameters."""
        self.ax.set_xlim(DEFAULT_xmin, DEFAULT_xmax)
        self.ax.set_ylim(DEFAULT_ymin, DEFAULT_ymax)
        empty_point, = self.ax.plot([0], [0])
        self.spl = SplineCurvesBuilder(empty_point, self.parent)
        self.spl.connect()

    def get_xlim(self):
        return self.ax.get_xlim()

    def get_ylim(self):
        return self.ax.get_ylim()

    def set_xlim(self, xlim):
        self.ax.set_xlim(xlim)
        self.fig.canvas.draw()

    def set_ylim(self, ylim):
        self.ax.set_ylim(ylim)
        self.fig.canvas.draw()

    def redraw(self):
        self.spl.create_spline(self.spl.xs, self.spl.ys)

    def set_equal_axes(self):
        self.spl.points.axes.axis('equal')
        self.redraw()

    def set_auto_axes(self):
        self.spl.points.axes.axis('auto')
        self.redraw()


class MyApp(QWidget):
    """Creates the GUI using the PyQt5 library."""
    add_point = True       # True if the user clicked the 'Add a point' button (and hasn't added one yet)
    delete_point = False    # True if the user clicked the 'Delete a point' button (and hasn't added one yet)
    move_point_or_canvas = False
    auto_adjust = False     # True if the 'Auto adjust' checkbox is checked
    equal_axes = False      # True if the 'Equal axes' checkbox is checked

    def __init__(self):
        super().__init__()
        self.setMinimumSize(1500, 800)
        self.setWindowTitle("Spline curves")

        self.layout = QVBoxLayout()
        self.topLayout = QHBoxLayout()      # store all top-bar widgets here
        self.layout.addLayout(self.topLayout)
        self.setLayout(self.layout)

        self.initUI()

    def initUI(self):
        # create the 'Add points' radio button
        self.add_button = QRadioButton("Add points")
        self.add_button.setChecked(True)
        self.add_button.toggled.connect(self.checked_add)
        self.topLayout.addWidget(self.add_button)

        # create the 'Delete points' button
        self.del_button = QRadioButton(self)
        self.del_button.setText("Delete points")
        self.del_button.clicked.connect(self.checked_del)
        self.topLayout.addWidget(self.del_button)

        # create the 'Move points' button
        self.move_button = QRadioButton(self)
        self.move_button.setText("Move points")
        self.move_button.clicked.connect(self.checked_move)
        self.topLayout.addWidget(self.move_button)

        # create the 'Fit to screen' button
        self.fit_button = QPushButton(self)
        self.fit_button.setText("Fit to screen")
        self.fit_button.clicked.connect(self.clicked_fit)
        self.topLayout.addWidget(self.fit_button)

        # create the 'x min' input line
        self.xmin_input = QLineEdit()
        self.xmin_input.setText(str(DEFAULT_xmin))
        self.xmin_input.textChanged.connect(self.update_xmin)
        form = QFormLayout()
        form.addRow("  x min:", self.xmin_input)      # spaces at the beginning are for additional padding
        self.topLayout.addLayout(form)

        # create the 'x max' input line
        self.xmax_input = QLineEdit()
        self.xmax_input.setText(str(DEFAULT_xmax))
        self.xmax_input.textChanged.connect(self.update_xmax)
        form = QFormLayout()
        form.addRow("  x max:", self.xmax_input)      # spaces at the beginning are for additional padding
        self.topLayout.addLayout(form)

        # create the 'y min' input line
        self.ymin_input = QLineEdit()
        self.ymin_input.setText(str(DEFAULT_ymin))
        self.ymin_input.textChanged.connect(self.update_ymin)
        form = QFormLayout()
        form.addRow("  y min:", self.ymin_input)      # spaces at the beginning are for additional padding
        self.topLayout.addLayout(form)

        # create the 'y max' input line
        self.ymax_input = QLineEdit()
        self.ymax_input.setText(str(DEFAULT_ymax))
        self.ymax_input.textChanged.connect(self.update_ymax)
        form = QFormLayout()
        form.addRow("  y max:", self.ymax_input)      # spaces at the beginning are for additional padding
        self.topLayout.addLayout(form)

        # deg_val = 2*displayed - 1 --> displayed = (deg_val + 1)//2
        # create the 'Degree' slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum((MIN_deg+1)//2)
        self.slider.setMaximum((MAX_deg+1)//2)
        self.slider.setValue((DEFAULT_deg+1)//2)
        self.slider.setMinimumWidth(150)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.changed_degree)
        self.label = QLabel()
        self.label.setText(f"&Degree: {DEFAULT_deg}   ")  # spaces at end for padding
        self.label.setBuddy(self.slider)
        form = QFormLayout()
        form.addRow(self.label, self.slider)
        form.setContentsMargins(30, 0, 30, 0)
        self.topLayout.addLayout(form)

        # create the 'Auto adjust' checkbox
        self.autoAdjust = QCheckBox("Auto adjust")
        self.autoAdjust.stateChanged.connect(self.checked_autoAdjust)
        self.topLayout.addWidget(self.autoAdjust)

        # create the 'Equal axes' checkbox
        self.equalAxes = QCheckBox("Equal axes")
        self.equalAxes.stateChanged.connect(self.checked_equalAxes)
        self.topLayout.addWidget(self.equalAxes)

        # create the matplotlib graph
        self.canvas = Canvas(self)
        self.layout.addWidget(self.canvas)

    def checked_add(self):
        """Sets add-points-mode. The user can not move canvas nor points in this mode."""
        MyApp.add_point = True
        MyApp.delete_point = False
        MyApp.move_point_or_canvas = False

    def checked_del(self):
        """Sets delete-points-mode. The user can still add points by right-clicking and move canvas."""
        MyApp.add_point = False
        MyApp.delete_point = True
        MyApp.move_point_or_canvas = False

    def checked_move(self):
        """Sets move-points-mode. The user can still add points by right-clicking and move canvas and places points."""
        MyApp.add_point = False
        MyApp.delete_point = False
        MyApp.move_point_or_canvas = True

    def clicked_fit(self):
        """Redraws the graph with tight layout."""
        MyApp.auto_adjust = True       # turn auto_adjust off
        self.canvas.redraw()           # redraw spline curve with auto_adjust on
        MyApp.auto_adjust = False      # turn auto_adjust off
        self.update_displayed_lims()

    def checked_autoAdjust(self, checked):
        """Turns auto_adjust on and off."""
        MyApp.auto_adjust = not MyApp.auto_adjust
        if checked:
            self.enable_input_lines(False)
        if not checked:
            if not self.equalAxes.isChecked():
                self.enable_input_lines(True)
            self.update_xmin()      # set pre-auto_adjust lims
            self.update_xmax()
            self.update_ymin()
            self.update_ymax()
        self.canvas.redraw()

    def checked_equalAxes(self, checked):
        """Turns equal_axes on and off."""
        MyApp.equal_axes = not MyApp.equal_axes
        if checked:
            self.enable_input_lines(False)
            self.canvas.set_equal_axes()
        else:
            if not self.autoAdjust.isChecked():
                self.enable_input_lines(True)
            self.canvas.set_auto_axes()
            self.update_xmin()      # set pre-equal_axes lims
            self.update_xmax()
            self.update_ymin()
            self.update_ymax()
        self.canvas.redraw()

    def changed_degree(self):
        """Changes the degree of the spline function."""
        deg = 2*self.slider.value() - 1   # we want only odd degrees
        self.label.setText(f"&Degree: {deg}   ")
        self.canvas.spl.degree = deg
        self.canvas.redraw()

    def update_xmin(self):
        """Updates xmin according to the xmin input line."""
        xmin = self.xmin_input.text()
        try:
            xmin = float(xmin)
        except ValueError:      # don't change anything if the input is not valid
            return
        xlim = self.canvas.get_xlim()
        if xmin == round(xlim[0], ROUND_input_lines):
            return
        self.canvas.set_xlim((xmin, xlim[1]))

    def update_xmax(self):
        """Updates xmax according to the xmax input line."""
        xmax = self.xmax_input.text()
        try:
            xmax = float(xmax)
        except ValueError:      # don't change anything if the input is not valid
            return
        xlim = self.canvas.get_xlim()
        if xmax == round(xlim[1], ROUND_input_lines):
            return
        self.canvas.set_xlim((xlim[0], xmax))

    def update_ymin(self):
        """Updates ymin according to the ymin input line."""
        ymin = self.ymin_input.text()
        try:
            ymin = float(ymin)
        except ValueError:      # don't change anything if the input is not valid
            return
        ylim = self.canvas.get_ylim()
        if ymin == round(ylim[0], ROUND_input_lines):
            return
        self.canvas.set_ylim((ymin, ylim[1]))

    def update_ymax(self):
        """Updates ymax according to the ymax input line."""
        ymax = self.ymax_input.text()
        try:
            ymax = float(ymax)
        except ValueError:      # don't change anything if the input is not valid
            return
        ylim = self.canvas.get_ylim()
        if ymax == round(ylim[1], ROUND_input_lines):
            return
        self.canvas.set_ylim((ylim[0], ymax))

    def update_displayed_lims(self):
        """Updates all displayed lims according to actual lims."""
        (xmin, xmax), (ymin, ymax) = self.canvas.get_xlim(), self.canvas.get_ylim()
        self.xmin_input.setText(f"{xmin:.{ROUND_input_lines}f}")
        self.xmax_input.setText(f"{xmax:.{ROUND_input_lines}f}")
        self.ymin_input.setText(f"{ymin:.{ROUND_input_lines}f}")
        self.ymax_input.setText(f"{ymax:.{ROUND_input_lines}f}")

    def enable_input_lines(self, enabled):
        self.xmin_input.setEnabled(enabled)
        self.xmax_input.setEnabled(enabled)
        self.ymin_input.setEnabled(enabled)
        self.ymax_input.setEnabled(enabled)


def main():
    app = QApplication(sys.argv)
    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Window...")


if __name__ == '__main__':
    main()
