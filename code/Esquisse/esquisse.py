# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

import bpy
import re
import os

from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty
from bpy.props import PointerProperty, FloatVectorProperty, CollectionProperty
from bpy.types import Panel, Operator, AddonPreferences, PropertyGroup, BlendData, Object
from .GhostProperties import *
from .GestureProperties import *

class Esquisse(PropertyGroup):


	title = StringProperty(default="Library")

	SVG_output_path = StringProperty(
		name = "SVG output path",
		description = "SVG output path",
		default = "/tmp/Esquisse_output.svg",
		subtype = 'FILE_PATH'
	)

	esquisse_library_path = StringProperty(
		name = "path of the library",
		description = 'Path of folder containing "object" and "templates" sub-folders for Esquisse',
		subtype = 'FILE_PATH'
	)

	# Fills properties
	render_fills = BoolProperty(
		default = True,
		description = "Enable the rendering of fills in the SVG file"
	)

	render_screens = BoolProperty(
		default = True,
		description = "Enable the rendering of external SVG screen interfaces in the SVG file"
	)


	# Visible Strokes properties
	render_visible_strokes = BoolProperty(
		default = True,
		description = "Enable the rendering of visible strokes in the SVG file"
	)


	visible_strokes_width = IntProperty(
		name = "Visible strokes thickness",
		description="Set the width for visible strokes",
		default = 2,
		min = 0,
		max = 20
	)

	visible_strokes_color = FloatVectorProperty(
		subtype='COLOR',
		size = 4,
		default=(0.0, 0.0, 0.0, 1.0),
		min=0.0, max=1.0,
		description="Set the color for visible strokes"
	)


	visible_strokes_style = EnumProperty(
		items=(
			('PLAIN', 'Plain strokes', 'A plain stroke style'),
			('DASHED', 'Dashed strokes', 'A dashed stroke style'),
		),
		name="Style for visible strokes",
		description="Set the style for visible strokes",
		default = 'PLAIN'
	)

	plain_dashed_value_visible_strokes = IntProperty (
		name = "plain_dashed_value",
		description="Set the plain interval of a dashed stroke",
		default = 4,
		min = 1,
		max = 10
	)

	space_dashed_value_visible_strokes = IntProperty (
		name = "space_dashed_value",
		description="Set the space interval of a dashed stroke",
		default = 4,
		min = 1,
		max = 10
	)



	# Hidden Strokes properties
	render_hidden_strokes = BoolProperty(
		default = False,
		description = "Enable the rendering of hidden strokes in the SVG file"
	)


	hidden_strokes_width = IntProperty(
		name = "Visible strokes thickness",
		description="Set width for hidden strokes",
		default = 2,
		min = 0,
		max = 20
	)

	hidden_strokes_color = FloatVectorProperty(
		name="strokes_color",
		subtype='COLOR',
		size = 4,
		default=(0.0, 0.0, 0.0, 1.0),
		min=0.0, max=1.0,
		description="Set the color for hidden strokes"
	)


	hidden_strokes_style = EnumProperty(
		items=[
			('PLAIN', 'Plain strokes', 'A plain stroke style'),
			('DASHED', 'Dashed strokes', 'A dashed stroke style'),
		],
		name="Style for invisible strokes",
		description="Set the style for hidden strokes",
		default = 'DASHED'
	)

	plain_dashed_value_hidden_strokes = IntProperty (
		name = "plain_dashed_value",
		description="Set the plain interval of a dashed stroke",
		default = 4,
		min = 1,
		max = 10
	)

	space_dashed_value_hidden_strokes = IntProperty (
		name = "space_dashed_value",
		description="Set the space interval of a dashed stroke",
		default = 4,
		min = 1,
		max = 10
	)

	###### COLLSION #######

	def direct_collision_updated(self, context):
		if self.direct_collision_enable:
			print("ENABLE DIRECT COLLISION")
		else:
			print("DISABLE DIRECT COLLISION")

	direct_collision_enable = BoolProperty(
		default = False,
		description = "Enable the direct collision checking",
		update = direct_collision_updated
	)

	def check_collision_before_rendering_update(self, context):
		if self.check_collision_before_rendering_enable:
			print("ENABLE COLLISION BEFORE RENDERING")
		else:
			print("DISABLE COLLISION BEFORE RENDERING")

	check_collision_before_rendering_enable = BoolProperty(
		default = False,
		description = "Enable the direct collision checking",
		update = check_collision_before_rendering_update
	)

	###### GHOST #######

	def ghost_mode_updated(self, context):
		if self.ghost_mode_enable:
			n = len(self.ghost_screenshots_list)
			if n > 0:
				self.current_screenshot_number = self.ghost_screenshots_list[n-1].number
		else:
			self.current_screenshot_number = -1

	ghost_screenshots_list = CollectionProperty(type = GhostScreenshot)
	current_screenshot_number = IntProperty(name = "current_screenshot_number", default = -1)
	ghost_mode_enable = BoolProperty(default = False, update = ghost_mode_updated)
	ghost_save_group = PointerProperty(type = bpy.types.Group)

	ease_blender_controls = BoolProperty(
		name = "Ease blender controls",
		description = "Active to simply the manipulation of armatures and parent-childs objects",
		default = True,
	)

	###### Gesture #######

	def select_gesture(self, context):
		_mode = None
		if bpy.context.object != None:
			_mode = bpy.context.object.mode
			if _mode != "OBJECT":
				bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		context.scene.objects.active = self.gesture_list[self.gesture_selected].gesture_path_object
		self.gesture_list[self.gesture_selected].gesture_object.hide_select = False
		self.gesture_list[self.gesture_selected].gesture_object.select = True
		self.gesture_list[self.gesture_selected].gesture_object.hide_select = True
		self.gesture_list[self.gesture_selected].gesture_path_object.select = True

	gesture_auto_enable = BoolProperty(default = False)
	gesture_select_type = EnumProperty(
		items=[
			('SELECT', 'Select', 'Select the wanted ones'),
			('ANCHOR', 'Anchors', 'Use the anchors'),
		],
		name="Gestures selection type",
		description="Choose how the gestures are selected",
		default = 'ANCHOR'
	)
	gesture_list = CollectionProperty(type = Gesture, description="List of all the gestures")
	gesture_selected = IntProperty(update = select_gesture, description="")
	gesture_auto_update = BoolProperty(default = True, description="Automatically update the gestures")

	###### CAMERA #######

	def camera_aspect_updated(self, context):
		if self.camera_aspect < 0:
			context.scene.render.resolution_x = 2000
			context.scene.render.resolution_y = (self.camera_aspect+1)*context.scene.render.resolution_x
		else:
			context.scene.render.resolution_y = 2000
			context.scene.render.resolution_x = (1-self.camera_aspect)*context.scene.render.resolution_y


	camera_aspect = FloatProperty(
		name = "Camera Aspect",
		description = "-1 : horizontal aspect, 0: square aspect, 1: vertical aspect",
		default = 1,
		max = 1,
		min = -1,
		update = camera_aspect_updated)



	##### Rendering ######
	is_rendering = BoolProperty(default = False)


################ PANEL ################

	useless = IntProperty()

def register():
	bpy.types.Scene.esquisse = PointerProperty(type=Esquisse)


def unregister():
	del bpy.types.Scene.esquisse
