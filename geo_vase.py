
import numpy as np
from scipy.spatial.transform import Rotation as R

import bezier
import json

demo = {
  "rows": 8,
  "sides": 5,
  "bez_nodes": [
        [0.30, 1.00, 0.35], 
        [0.00, 1.00, 1.25], 
        [0.00, 0.00, 0.00]
    ],
  "weights": [0, 0.1, 0.2, 1.0]
}

class GeoVase:
  def __init__(self, rows=demo["rows"], sides=demo["sides"], bez_nodes=demo["bez_nodes"], weights=demo["weights"]):

    # bezier edge profile
    self.bez_nodes1 = np.array(bez_nodes)

    # a way to manipulate at what level (as a percentage of bez_nodes) the rows verts will be
    self.weights = np.array([
        weights
    ])

    self.rows = rows

    self.columns = sides*2

    self.calc()

  def calc(self):
    curve1 = bezier.Curve(self.bez_nodes1, degree=len(self.bez_nodes1)-1)

    # initial distribution along bezier curve
    s_vals = np.linspace(0.0, 1.0, self.rows)

    # weighted distribution along bezier curve
    try:
      weight_curve = bezier.Curve(self.weights, degree=len(self.weights)-1)
      weighted_vals = weight_curve.evaluate_multi(s_vals)
    except:
      weighted_vals = np.array([s_vals])

    # find all points along bezier curve
    v = curve1.evaluate_multi(weighted_vals[0])

    # bezier curve lib has verts defined orthogonally to the way I think ¯\_(ツ)_/¯
    v1 = v.transpose()

    # create list of 
    vertices = [v1]

    for i in range(self.columns-1):
        r = R.from_euler('y', 360*(i+1)/self.columns, degrees=True)
        vertices.append(r.apply(v1))

    faces = []

    for i in range(self.columns):
        verts = []
        if i%2 == 0:
            verts.append([(i+2)%self.columns, 0])
            for r in range(self.rows):
                s = i + r%2
                verts.append([s%self.columns, r])
            # deals with triangle connecting to top face when row count is odd
            if self.rows%2 == 1:
              verts.append([(i + 2)%self.columns, self.rows-1])
        else:
            for r in range(self.rows):
                s = i + 1 - r%2
                verts.append([s%self.columns, r])

            # deals with triangle connecting to top face when row count is even
            if self.rows%2 == 0:
              verts.append([(i + 2)%self.columns, self.rows-1])

        for i in range(2, len(verts)):
            face = [verts[i - 2 + j] for j in range(3)]
            faces.append([f[0]*self.rows + f[1] for f in face])

    # bottom face hits every other base point
    bottom_face = [s*2*self.rows for s in range(int(self.columns/2))]

    # for rendering generate triangles...
    bottom_triangles = []

    for i in range(2, len(bottom_face)):
        face = [bottom_face[0], bottom_face[i-1], bottom_face[i]]
        bottom_triangles.append(face)

    self.verts = np.concatenate(vertices).tolist()
    self.faces = faces + [bottom_face]
    self.triangles = faces + bottom_triangles

  def json(self):
    return json.dumps({ "vertices": self.verts, "faces": self.faces, "triangles": self.triangles })

if __name__ == "__main__":
  gv = GeoVase()
  gv.calc()

  print(gv.json())