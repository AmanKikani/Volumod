import FreeCad
import Mesh
import Part
shape = Part.Shape()
shape.read('my_shape.step')
doc = App.newDocument('Doc')
pf = doc.addObject("Part::Feature","MyShape")
pf.Shape = shape
Mesh.export([pf], 'my_shape.stl')