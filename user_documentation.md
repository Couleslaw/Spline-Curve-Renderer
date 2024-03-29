# User documentation
## Modes
There are three modes which the program can be in. They can be switched via three radio buttons in the top-left corner.
- Add points mode - lets you add new points at the location where you clicked.
- Delete points mode - removes the point on which you cliked.
- Move points mode - lets you pick up and move points.

The spline function is redrawn automatically whenever anything changes.


## Adding new points 
- New points can be added either by right-clicking or by selecting the 'Add points' mode and left-clicking.
- The point will appear at the location where you clicked.

## Deleting existing points
- Existing points can be removed by selecting the 'Delete points' mode and left-clicking on them.
- All points can be deleted by clicking on the 'Delete all' button.

## Moving points
- Points can be picked up and dragged by selecting the 'Move points' mode and using the left mouse button.

## Movement in the figure
- The graph can be moved by left-clicking and dragging.
- This doesn't work when in the 'Add points' mode because a new point will be added instead. 
- You can also zoom.

## Changing the limits of the coordinate axes 
- Limits can be changed manually.
- If the graph does not fit on the screen, limits can be adjusted accordingly by clicling on the 'Fit to screen' button.
- If you toggle 'Auto adjust' this will always be the case. 
- If you want equal scaling on both axes you should toggle 'Equal axes.'
- 'Auto adjust' and 'Equal axes' cannot be toggled at the same time.
- You can't change limits manually while 'Auto adjust' or 'Equal axes' is toggled.
- Original limits are restored if there was no user-movement in the figure while either of these was toggled.

## Changing the degree of splines
- The default degree is 3.
- Degree can be changed via a slider with values 3, 5, 7, 9, 11, 13.
- The degree can't be changed while moving a point. 
- The slider can be incrementing using arrow-keys (if it is focused). 
- You can change focus to the slider by pressing 'Alt+d.'
