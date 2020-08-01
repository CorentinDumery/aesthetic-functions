# colorExplorer
### Aesthetic 2D visualization of functions

Work in Progress.

The objective of this project is to explore the depths of two-dimensional mathematics. To put it simply, it is about visualizing a function in 2D, but with fancy colors and some extra options. It is not very useful, but I like it. If you're interested, I'd be delighted to see your creations and exchange tips !

## Tutorial

The first thing you need to know is that each pixel on the picture corresponds to a unique ```(i,j)``` value. In particular, the point in the center is at ```(0,0)```. So for example if we represent the function ```100*(i**2+j**2)```, we should get a circle.

We can then choose from the different color-representation modes to get the following results:

RGB | B&W | HSV
:-------------------------:|:-------------------------:|:-----------------------:
![ex1](Images/Tutorial/rgb.png) | ![ex1](Images/Tutorial/bw.png) |  ![ex1](Images/Tutorial/hsv.png)

Now if you want to experiment with different values without having to enter a new function every time, you can use the sliders. To do so, you must include an ```α``` or a ```β``` in your formula, and this value will be replaced by the value of the associated slider each time it is moved. For example let's try the formula ```α*(i**2+j**2)```:

```α=5``` | ```α=200```
:-------------------------:|:-----------------------:
![ex1](Images/Tutorial/alpha5.png) | ![ex1](Images/Tutorial/alpha200.png) |  

Examples | Examples |
:-------------------------:|:-----------------------:
![ex1](Images/wavies.png) |  ![ex1](Images/the%20pear%20of%20illusions.png) |
![ex1](Images/ring_of_truth.png) | ![ex1](Images/sundisk.png) |
![ex1](Images/vinyl.png) | ![ex1](Images/sparkling%20sun.png) |
![ex1](Images/red%20perspective.png) | ![ex1](Images/circle%20chess.png) |

## Install & Run
### Ubuntu, python3
The following python libraries are required:
```
python3-tk
python3-pil.imagetk
python3-numpy
python3-scipy
python3-matplotlib
```
To run the project, navigate to the project's folder and run:
```
python3 colorExplorer.py
```
