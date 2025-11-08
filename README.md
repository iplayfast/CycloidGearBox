# FreeCAD Cycloid Gear Box
Cycloidal gear box code for FreeCad

This workbench will provide a working model of a cycloidal drive that can be 3d printed. This was done as a workbench since all parts need to be mathematically correct in shape and size in order to work. The goal of this workbench is to provide the broad strokes in getting a cycloidal gearbox. It creates all the parametric primitives for each part so you can modify them as you see fit. 



See [wikipedia](https://en.wikipedia.org/wiki/Cycloidal_drive) for an explanation.

### Screenshot
![Screen Shot](screenshot.png?raw=true "Screen Shot")

### Status
released

### Prerequisites
* FreeCAD v1.0 or >

### Installation

#### Linux and MacOSX

```bash
cd ~/.local/share/FreeCAD/Mod
git clone git@github.com:iplayfast/CycloidGearBox.git 
```

### Usage 

1. Start FreeCad
2. Select **cycloidalGearBox** workspace from the Workbench dropdown menu
3. Click on the **cycloidalgearbox** icon and it will create (the beginnings of it) with some default parameters.

![logo](icons/cycloidgearbox.svg) **cycloidal gearbox icon**

After much effort, I'm happy to report that the math works! I've verified this by doing a 3d print of the default parameters, and another with different parameters. Both gearboxs are functional!
### Feedback

Please open a ticket in this repository's issue queue.

### License
LGPLv2.1 (see [LICENSE](LICENSE))
