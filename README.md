# colorExplorer
### Aesthetic 2D visualization of functions

Work in Progress.

The objective of this project is to explore the artistic aspects of two-dimensional mathematics. To put it simply, it is about visualizing a function in 2D, but with fancy colors and some extra options. It is not very useful, but I like it. If you're interested, I'd be delighted to see your creations and exchange tips !

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
## Tutorial
The first thing to know is that each pixel on the picture corresponds to a unique ```(i,j)``` value. In particular, the point in the center is at ```(0,0)```. For example, the function ```100*(i**2+j**2)``` takes the form of concentric circles after coloration by function value.

**colorExplorer** provides 3 different color-representation modes. Here is how the previous example looks under each color mode:

RGB | B&W | HSV
:-------------------------:|:-------------------------:|:-----------------------:
![ex1](Images/Tutorial/rgb.png) | ![ex1](Images/Tutorial/bw.png) |  ![ex1](Images/Tutorial/hsv.png)

If you want to experiment with different visualization effects of a function, try out the sliders. For example, you can add an ```α``` or a ```β``` in your function to change the amplitude of the entire (or parts of the) function. ```α*(i**2+j**2)``` looks very different under ```α=5``` and ```α=200``` :

```α=5``` | ```α=200```
:-------------------------:|:-----------------------:
![ex1](Images/Tutorial/alpha5.png) | ![ex1](Images/Tutorial/alpha200.png) |  

## Example creations  
example | example    
:-------------------------:|:-----------------------:
![ex1](Images/wavies.png) |  ![ex1](Images/the%20pear%20of%20illusions.png) |
![ex1](Images/ring_of_truth.png) | ![ex1](Images/sundisk.png) |
![ex1](Images/vinyl.png) | ![ex1](Images/sparkling%20sun.png) |
![ex1](Images/red%20perspective.png) | ![ex1](Images/circle%20chess.png) |
