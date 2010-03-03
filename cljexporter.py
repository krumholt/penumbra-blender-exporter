#!BPY

"""
Name: 'Penumbra exporter(.clj)'
Blender: 249
Group: 'Export'
Tooltip: 'Clojure Penumbra Exporter'
"""

__author__ = ["Tobias Krumholz"]
__url__ = ("")
__version__ = "0.1.0"
__bpydoc__ = """\

Clojure Penumbra exporter

This script Exports a clojure file.

It will create a clojure map datastructure containing all relevant information.
This is version 0.1.0 so expect lots of changes. Currently only materials per 
face, color per vertex, normal per vertex and vertex position are exported.
"""

# ***** BEGIN EPL LICENSE BLOCK *****
#
#   Copyright (c) Tobias Krumholz. All rights reserved.
#   The use and distribution terms for this software are covered by the
#   Eclipse Public License 1.0 (http://opensource.org/licenses/eclipse-1.0.php).
#   By using this software in any fashion, you are agreeing to be bound by
#   the terms of this license.
#   You must not remove this notice, or any other, from this
#   software.
#
# NO WARRANTY
#
# EXCEPT AS EXPRESSLY SET FORTH IN THIS AGREEMENT, THE PROGRAM IS PROVIDED ON AN "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED 
# INCLUDING, WITHOUT LIMITATION, ANY WARRANTIES OR CONDITIONS OF TITLE, NON-INFRINGEMENT, 
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. Each Recipient is solely responsible 
# for determining the appropriateness of using and distributing the Program and assumes 
# all risks associated with its exercise of rights under this Agreement , including but 
# not limited to the risks and costs of program errors, compliance with applicable laws, 
# damage to or loss of data, programs or equipment, and unavailability or interruption of 
# operations.
#
#
# DISCLAIMER OF LIABILITY
#
# EXCEPT AS EXPRESSLY SET FORTH IN THIS AGREEMENT, NEITHER RECIPIENT NOR ANY CONTRIBUTORS
# SHALL HAVE ANY LIABILITY FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING WITHOUT LIMITATION LOST PROFITS), HOWEVER CAUSED AND 
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OR DISTRIBUTION OF THE 
# PROGRAM OR THE EXERCISE OF ANY RIGHTS GRANTED HEREUNDER, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGES.
#
# ***** END EPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

import Blender
from Blender import Draw, BGL
import bpy

file_str = "No file choosen"
global_toggle = 0
local_toggle = 1
active_scene = bpy.data.scenes.active
active_object = active_scene.objects.active
all_to_triangle = 1

def write_material(mat):
        ambient_color = [mat.amb * x for x in Blender.World.GetCurrent().amb]
        ambient_color.append(mat.alpha)
        diffuse_color = mat.rgbCol
        diffuse_color.append(mat.alpha)
        specular_color = mat.specCol
        specular_color.append(mat.alpha)
        shininess = mat.hard / 4
        s = "{:ambient " + str(ambient_color) + "\n"\
            + ":diffuse " + str(diffuse_color) + "\n"\
            + ":specular " + str(specular_color) + "\n"\
            + ":emission " + str([0, 0, 0, 0]) + "\n"\
            + ":shininess" + " " + str(shininess) + "}\n"
        return s

def write_materials(materials):
        s = "{"
        for mat in materials:
                s += ":" + str(mat.name) + " \n" + write_material(mat)
        s += "}\n"
        return s

def write_face_v_n_uvVert(face):
        s = "["
        for v in reversed(face.v):
                s += "{:normal " + str([x for x in v.no]) + " :vertex " + str([x for x in v.co]) + " :tex-coords " + str([x for x in v.uvco]) + "}\n"
        s += "]"
        return s

def write_face_v_n_uvFace(face):
        s = "["
        rev_verts = reversed(face.v)
        uvs = reversed(face.uv)
        i = 0
        for v in rev_verts:
                s += "{:normal " + str([x for x in v.no]) + " :vertex " + str([x for x in v.co]) + " :tex-coords " + str([x for x in uvs[i]]) + "}\n"
                i += 1
        s += "]"
        return s

def write_face_v_n(face):
        s = "["
        for v in face.v:
                s += "{:normal " + str([x for x in v.no]) + " :vertex " + str([x for x in v.co]) + " :tex-coords nil}\n"
        s += "]"
        return s

def write_faces(mesh):
        s = "["
        if len(mesh.materials) == 0:
                if mesh.vertexUV == 1:
                        for f in mesh.faces:
                                s += "{:material nil\n"\
                                    + ":vertices " + write_face_v_n_uvVert(f) + "}\n"
                elif mesh.faceUV == 1:
                        for f in mesh.faces:
                                s += "{:material nil\n"\
                                    + ":vertices " + write_face_v_n_uvFace(f) + "}\n"
                else:
                        for f in mesh.faces:
                                s += "{:material nil\n"\
                                    + ":vertices " + write_face_v_n(f) + "}\n" 
        else:
                if mesh.vertexUV == 1:
                        for f in mesh.faces:
                                s += "{:material :" + mesh.materials[f.mat].name + "\n"\
                                    + ":vertices " + write_face_v_n_uvVert(f) + "}\n"
                elif mesh.faceUV == 1:
                        for f in mesh.faces:
                                s += "{:material :" + mesh.materials[f.mat].name + "\n"\
                                    + ":vertices " + write_face_v_n_uvFace(f) + "}\n"
                else:
                        for f in mesh.faces:
                                s += "{:material :" + mesh.materials[f.mat].name + "\n"\
                                    + ":vertices " + write_face_v_n(f) + "}\n" 
        s += "]\n"
        return s

def write_obj(filepath):
	global active_object, all_to_triangle
	Blender.Window.EditMode(0)
	out = file(filepath, 'w')
	ob = active_object
	mesh = ob.getData(mesh=1)
	
	if all_to_triangle == 1:
		mesh.quadToTriangle()
	
	#writing object name
	out.write( '{:name "%s"\n' % ob.name)

        #writing texture type textured or not textured
        if mesh.vertexUV == 0 and mesh.faceUV == 0:
                out.write( ':textured? false\n' )
        else:
                out.write( ':textured? true\n' )

        #writing object materials
        out.write( ':materials\n' + write_materials(mesh.materials) )

	#writing object faces	
	out.write( ':faces\n' + write_faces(mesh) )

        #writing rest
        out.write( '}' )
	out.close()

def file_str_choosen(str):
	global file_str
	file_str = str

def key_event(evt, val):
	if evt == Draw.ESCKEY:
		Draw.Exit()

def checkLegal():
	return active_object.type == "Mesh"

def button_event(evt):
	global all_to_triangle,local_toggle, global_toggle
	if evt == 0 or evt == 1:
		local_toggle = 1 - local_toggle
		global_toggle = 1 - global_toggle
		Draw.Redraw(1)
	elif evt == 2:
		Blender.Window.FileSelector(file_str_choosen, "Choose file")
	elif evt == 3:
		if file_str != "No file choosen":
			if checkLegal():
				write_obj(file_str)	
				Draw.Exit()
			else:
				Draw.PupBlock("Error",["No legal object selected", "(active object is a lamp or ", "camera?). Select an object", "then restart the script."])
		else:
			Draw.PupBlock("Error",["No file selected."])
	elif evt == 4:
		Draw.Exit()	
	elif evt == 5:
		all_to_triangle = 1 - all_to_triangle
	

def gui():
	global active_object, file_str, local_toggle, global_toggle, all_to_triangle
	my_export_button = Draw.PushButton("Export", 3, 100, 50 , 70, 20, "Export active object to selected file.")
	#my_local_toggle = Draw.Toggle("local coordinates", 0, 100, 100, 150, 20, local_toggle, "When selected local mesh coordinates will be exported.")
	#my_global_toggle = Draw.Toggle("global coordinates", 1, 250, 100, 150, 20, global_toggle, "When selected global mesh coordinates will be exported.")
	#my_triangles_toggle = Draw.Toggle("Quads to Triangles", 5, 100, 75, 150, 20, all_to_triangle, "When selected all faces will be transformed to triangles.")
	#BGL.glRasterPos2i(255, 80)
	#Draw.Text("!! THIS WILL ALTER YOUR OBJECT !!", "normal")
	my_file_choose_btn = Draw.PushButton("Choose file", 2, 100, 150, 120, 20 , "Click here to select a file to save to")
	my_exit_btn = Draw.PushButton("Exit", 4, 200, 50, 70, 20 , "Click here to abort and exit.") 
	BGL.glRasterPos2i(230, 155)
	Draw.Text(file_str, "normal")
	BGL.glRasterPos2i(100, 175)
	Draw.Text("Selected object:", "normal")
	BGL.glRasterPos2i(230, 175)
	Draw.Text(active_object.name, "normal")

Draw.Register(gui, key_event, button_event)
