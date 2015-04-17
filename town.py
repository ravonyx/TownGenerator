import sys
import os
sys.path.append(os.path.dirname(bpy.data.filepath))

from tools_blender import *

import bmesh
import bpy
from random import *
from bpy.props import *
from math import *
 
#properties of the panel
def initSceneProperties(scn):
	bpy.types.Scene.Length = IntProperty(
		name = "Length", 
		description = "Enter an integer",
		default = 6,
		min = 5,
		max = 8)
	bpy.types.Scene.Taille = IntProperty(
		name = "Taille", 
		description = "Enter an integer",
		default = 3,
		min = 1,
		max = 6)
	return
initSceneProperties(bpy.context.scene)

#gui panel
class ToolsPanel(bpy.types.Panel):
	bl_label = "Tools For Town"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
 
	def draw(self, context):
		layout = self.layout
		scn = context.scene
		layout.prop(scn, 'Length')
		layout.prop(scn, 'Taille')
		layout.operator("town.gen")
		layout.operator("town.delete")
		layout.operator("town.print_index")

class OBJECT_OT_GenButton(bpy.types.Operator):
	bl_idname = "town.gen"
	bl_label = "Create town"
	def execute(self, context):
		lenght = bpy.context.scene.Length
		taille = bpy.context.scene.Taille
		generate_town(taille)
		return{'FINISHED'}    

class OBJECT_OT_DeleteButton(bpy.types.Operator):
	bl_idname = "town.delete"
	bl_label = "Delete town"
	def execute(self, context):
		for ob in bpy.context.scene.objects:
			ob.select = (ob.type == 'MESH' or ob.type == 'LAMP') and (ob.name.startswith("Cylinder") or ob.name.startswith("Cube") or ob.name.startswith("Branch_pivot") or ob.name.startswith("Branch_feuille"))
			bpy.ops.object.delete()
		return{'FINISHED'}    

class OBJECT_OT_PrintButton(bpy.types.Operator):
	bl_idname = "town.print_index"
	bl_label = "Print Index"
	def execute(self, context):
		print_index()
		return{'FINISHED'}    
#registration
bpy.utils.register_module(__name__)

def createMaterial(name):
	img = bpy.data.images.load('//'+name)
	tex = bpy.data.textures.new('TexName', type = 'IMAGE')
	tex.image = img
	mat = bpy.data.materials.new('MatName')
	
	ctex = mat.texture_slots.add()
	ctex.texture = tex
	ctex.texture_coords = 'ORCO'
	ctex.mapping = 'CUBE'
	return mat

def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)
	

def generate_town(taille):
	print("test")
	#bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
	#bpy.ops.transform.resize(value=(0.2, 0.2, 0.2), constraint_axis=(False, False, True))
	#bpy.ops.transform.resize(value=(taille, taille, taille), constraint_axis=(False, False, False))
	
	#FRACTURE LE PLAN
	#bpy.ops.mesh.subdivide(number_cuts=2, smoothness=0, fractal=1.8)

	#EDGE OFFSET
	#we had to select the edge first 
	#bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_resize={"value":(0.8, 0.8, 0.8), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

	mesh = bpy.data.meshes.new(name="Mesh")
	coords = []
	faces = []
	idx = 0;
	px = 0
	py = 0
	pz = 0
	create_objecttriangle_coords(coords,px, py, pz, 2, 3)
	create_object_faces(faces, idx)
	
	#on cree le mesh à partir des coordonnées et faces crées
	object = bpy.data.objects.new( 'Triangle', mesh )
	#link de l'object à la scene
	bpy.context.scene.objects.link( object )
	bpy.context.scene.objects.active = object
	mesh.from_pydata( coords, [], faces )
	mesh.update( calc_edges=True )
	
	
	#mesh = bpy.context.object
	mesh_data = object.data
	
	bpy.ops.object.mode_set(mode='EDIT')
	mesh = bmesh.from_edit_mesh(mesh_data)
	
	extrude_face(mesh,  0, 0, 0, 2)
	
def create_objecttriangle_coords(coords,px, py, pz, stepx, stepy):
	coords.append(( px, py, pz ))
	coords.append(( px + stepx, py, pz ))
	coords.append(( px, py + stepy, pz))

def create_object_faces(faces, idx):
	faces.append(( idx, idx+1, idx+2))
	
def roads_gen(width, height, num_cells):
	bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
	bpy.ops.transform.resize(value=(0.2, 0.2, 0.2), constraint_axis=(False, False, True))
	bpy.ops.transform.resize(value=(width, width, width), constraint_axis=(False, False, False))
	nx = []
	ny = []
	nr = []
	ng = []
	nb = []
	for i in range(num_cells):
		nx.append(randrange(width))
		ny.append(randrange(width))
		nr.append(randrange(256))
		ng.append(randrange(256))
		nb.append(randrange(256))
		
	for y in range(width):
		for x in range(width):
			dmin = hypot(width-1, width-1)
			j = -1
			for i in range(num_cells):
				d = hypot(nx[i]-x, ny[i]-y)
				if d < dmin:
					dmin = d
					j = i
			bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=(x ,y, 1))
	generate_voronoi_diagram(500, 500, 25)
