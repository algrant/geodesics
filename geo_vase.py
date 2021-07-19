
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

  def calc_indexed_vertices(self):
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

    # create list of vertices...
    vertices = [v1]

    for i in range(self.columns-1):
        r = R.from_euler('y', 360*(i+1)/self.columns, degrees=True)
        vertices.append(r.apply(v1))

    self.indexed_vertices = vertices

  def calc_indexed_faces(self):
    faces = []

    for r in range(self.rows):
      for c in range(r%2, self.columns, 2):

        verts = [(c, r)]
        
        if r + 1 < self.rows:
          verts.append(((c + 1)%self.columns, r +1))
        
        verts.append(((c + 2)%self.columns, r))

        if r - 1 >= 0:
          verts.append(((c + 1)%self.columns, r -1 ))
        
        if 0 < r < self.rows - 1:
          faces.append([verts[3], verts[0], verts[1]])
          faces.append([verts[1], verts[2], verts[3]])
        else:
          faces.append(verts)

    bottom_face = [(c, 0) for c in range(0, self.columns, 2)]
    top_face = [(c, self.rows - 1) for c in range(self.columns - self.rows%2 - 1, -1, -2)]

    self.indexed_faces = faces + [bottom_face, top_face]


  def calc(self):
    self.calc_indexed_faces()
    self.calc_indexed_vertices()

    indexed_vert_to_vert = {}
    verts = []
    faces = []
    triangles = []

    for indexed_face in self.indexed_faces:
      face = []
      for iv in indexed_face:
        if iv not in indexed_vert_to_vert:
          indexed_vert_to_vert[iv] = len(verts)
          verts.append(self.indexed_vertices[iv[0]][iv[1]])
        face.append(indexed_vert_to_vert[iv])
      faces.append(face)

      if len(face) == 3:
        triangles.append(face)
      else:
        for i in range(2, len(face)):
          triangles.append([face[0], face[i-1], face[i]])

    self.verts = verts
    self.faces = faces
    self.triangles = triangles

    
  def json(self):
    for f in self.faces:
      f.reverse()
    return json.dumps({ "vertices": np.array(self.verts).tolist(), "faces": self.faces, "triangles": self.triangles })

if __name__ == "__main__":
  gv = GeoVase()

  print(gv.json())