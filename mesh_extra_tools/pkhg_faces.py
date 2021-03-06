bl_info = {
    "name": "PKHG faces",
    "author": " PKHG ",
    "version": (0, 0, 5),
    "blender": (2, 7, 1),
    "location": "View3D > Tools > PKHG (tab)",
    "description": "Faces selected will become added faces of different style",
    "warning": "not yet finished",
    "wiki_url": "",
    "category": "Mesh",
}
import bpy
import bmesh
from mathutils import Vector, Matrix
from bpy.props import BoolProperty, StringProperty, IntProperty, FloatProperty, EnumProperty


class AddFaces(bpy.types.Operator):
    """Get parameters and build object with added faces"""
    bl_idname = "mesh.add_faces_to_object"
    bl_label = "new FACES: add"
    bl_options = {'REGISTER', 'UNDO' , 'PRESET'}
    
    reverse_faces = BoolProperty(name = "reverse_faces", default = False,\
                    description = "revert the normal of selected faces")
    name_source_object = StringProperty(
        name= "which MESH",
        description = "lets you chose a mesh",
        default = "Cube")
    remove_start_faces = BoolProperty(name = "remove_start_faces", default = True,\
                                      description = "make a choice, remove or not")
    base_height = FloatProperty(name="base_height faces", min=-20, \
                    soft_max=10, max=20, default=0.2,\
                    description="sets general base_height")
    
    use_relative_base_height = BoolProperty(name = "rel.base_height", default = False,\
                        description = " reletive or absolute base_height")
    
    relative_base_height = FloatProperty(name="relative_height", min=-5, \
                    soft_max=5, max=20, default=0.2,\
                    description="PKHG>TODO")
    relative_width = FloatProperty(name="relative_width", min=-5, \
                    soft_max=5, max=20, default=0.2,\
                    description="PKHG>TODO")
    second_height =  FloatProperty(name="2. height", min=-5, \
                    soft_max=5, max=20, default=0.2,\
                    description="2. height for this and that")
    width = FloatProperty(name="wds.faces", min = -20, max=20, default=0.5,\
                    description="sets general width")
    repeat_extrude = IntProperty(name = "repeat", min = 1 , \
                                 soft_max = 5, max = 20,\
                        description = "for longer base")    
    move_inside = FloatProperty(name="move inside", min = 0.0,\
                                max= 1.0, default = 0.5,\
                description = "how much move to inside")
    thickness = FloatProperty( name = "thickness", soft_min = 0.01, min = 0,\
                            soft_max = 5.0, max = 20.0, default = 0 )
    depth = FloatProperty( name = "depth",min = -5,\
                           soft_max = 5.0, max = 20.0, default = 0)

    collapse_edges = BoolProperty(name = "make point" , default = False,\
                        description = "collapse vertices of edges")
    spike_base_width = FloatProperty(name = "spike_base_width", default = 0.4,\
                        min = -4.0, soft_max = 1, max = 20,\
                        description = "base width of a  spike")
    base_height_inset = FloatProperty(name = "base_height_inset", default = 0.0,\
                                     min = -5, max = 5,\
                        description = "to elevate/or neg the ...")
    top_spike = FloatProperty(name = "top_spike", default = 1.0, min = -10.0, max = 10.0,
                        description = " the base_height of a spike")
    top_extra_height = FloatProperty(name = "top_extra_height", default = 0.0, min = -10.0, max = 10.0,
                        description = " add extra height")
    step_with_real_spike = BoolProperty(name = "step_with_real_spike", default = False,\
                                        description = " in stepped a real spike")
    use_relative = BoolProperty(name = "use_relative", default = False,\
                                description = "change size using area, min of max")
  
    '''
    min_or_max = EnumProperty(
        description = "use either max area or min area or none",
        default = "no",
        items = [
            ('no', 'no', 'choose one of the other possibilies'),
            ('maxi', 'maxi', 'use max(areas)'),
            ('minii', 'mani', 'use min(areas)'),
        ])
    '''

    face_types = EnumProperty(
        description = "different types of faces",
        default = "no",
        items = [
            ('no', 'choose!', 'choose one of the other possibilies'),
            ('open inset', 'open inset', 'holes'),
            ('with base', 'with base', 'base and ...'),
            ('clsd vertical', 'clsd vertical',  'clsd vertical'),
            ('open vertical', 'open vertical',  'openvertical'),
            ('spiked', 'spiked', 'spike'),
            #('open slanted','open slanted','open slanted'), #PKHG>INFO via ...
            #('clsd point', 'clsd point',  'clsd point'),
            #('pillow', 'pillow',  'pillow'),
            ('stepped', 'stepped',  'stepped'),
            ('boxed', 'boxed',  'boxed'),
            ('bar', 'bar',  'bar'),
    ])
    strange_boxed_effect = BoolProperty(name="strange effect", default=False,
                        description="do not show one extrusion")
    use_boundary = BoolProperty(name = "use_boundary", default = True)
    use_even_offset = BoolProperty(name = "even_offset", default = True)
    use_relative_offset = BoolProperty(name = "relativ_offset", default = True)
    use_edge_rail  = BoolProperty(name = "edge_rail", default = False)
    use_outset = BoolProperty(name = "outset", default = False)
    use_select_inset = BoolProperty(name = "inset", default = False)
    #NOT GOOD FOR split use_individual = BoolProperty(name = "individual", default = True)
    use_interpolate = BoolProperty(name = "interpolate", default = True)


    @classmethod
    def poll(cls, context):
        #return True
        result = False
        active_object = context.active_object
        if active_object:
            mesh_objects_name = [el.name for el in bpy.data.objects if el.type ==\
                             "MESH"]
            if active_object.name in mesh_objects_name:
                result = True
                #if active_object.mode == "OBJECT":
                    #result = True
        return result
        
    def draw(self, context): #PKHG>INFO Add_Faces_To_Object operator GUI
        layout = self.layout
        col = layout.column()
        col.label(text = "ACTIVE object used!")
        #col.prop(self, "reverse_faces")
        #col.prop(self, "remove_start_faces")
        col.prop(self, "face_types")
        col.prop(self, "use_relative")
        if self.face_types == "open inset":
#            col.prop(self, "remove_start_faces")
            col.prop(self, "move_inside")
            col.prop(self, "base_height")
        elif self.face_types == "with base":
#            col.prop(self, "remove_start_faces")
            col.prop(self, "move_inside")
            col.prop(self, "base_height")
            col.prop(self, "second_height")
            col.prop(self, "width")
        elif self.face_types == "clsd vertical":
            col.prop(self, "base_height")
            #col.prop(self, "use_relative_base_height")
        elif self.face_types == "open vertical":
            col.prop(self, "base_height")
            #col.prop(self, "use_relative_base_height")
        elif self.face_types == "boxed":
            col.prop(self, "move_inside")
            col.prop(self, "base_height")
            col.prop(self, "top_spike")
            col.prop(self, "strange_boxed_effect")
        elif self.face_types == "spiked":
            col.prop(self, "spike_base_width")
            col.prop(self, "base_height_inset")
            col.prop(self, "top_spike")
        elif self.face_types == "bar":
            #PKHG>INFO not used yet col.prop(self, "base_height_inset")
#            col.prop(self, "remove_start_faces")
            col.prop(self, "spike_base_width")
            col.prop(self, "top_spike")
            col.prop(self, "top_extra_height")
            #col.prop(self, "top_relative")
        elif self.face_types == "stepped":
            col.prop(self, "spike_base_width")
            col.prop(self, "base_height_inset")
            col.prop(self, "top_extra_height")
            col.prop(self, "second_height")
            col.prop(self, "step_with_real_spike")
           

    def execute(self, context):
        #PKHG>DBG print("\n======== TODO executer of Add_Faces_To_Object L93")
        bpy.context.scene.objects.active
        #print("face_types =", self.face_types)
        obj_name = self.name_source_object
        face_type = self.face_types
        if face_type == "spiked":
            Spiked(spike_base_width = self.spike_base_width,\
                    base_height_inset = self.base_height_inset,\
                    top_spike = self.top_spike, top_relative = self.use_relative)
        elif face_type == "boxed":
            startinfo = prepare(self, context, self.remove_start_faces)
            #print(startinfo)
            bm = startinfo['bm']
            top = self.top_spike
            obj = startinfo['obj']
            obj_matrix_local = obj.matrix_local
            
            
            
            distance = None
            base_heights = None
            t = self.move_inside
            areas = startinfo['areas']
            base_height = self.base_height

            #PKHG>INFO relative to size of area?!
            if self.use_relative:
                distance = [ min(t * area, 1.0) for i, area  in enumerate(areas)]
                base_heights = [ base_height * area for i, area  in enumerate(areas)]
            else:
                distance = [t] * len(areas)
                base_heights = [base_height] * len(areas)

            rings = startinfo['rings']
            centers = startinfo['centers']
            normals = startinfo['normals']
            for i in range(len(rings)):
                make_one_inset(self,context, bm = bm, ringvectors = rings[i],\
                               center = centers[i], normal = normals[i],\
                               t = distance[i], base_height = base_heights[i])
                bpy.ops.mesh.select_mode(type="EDGE")
                bpy.ops.mesh.select_more()
                bpy.ops.mesh.select_more()
            bpy.ops.object.mode_set(mode='OBJECT')
            #PKHG>INFO base extrusion done and set to the mesh
        
            #PKHG>INFO if the extrusion is NOT  done ... it looks straneg soon!
            if not self.strange_boxed_effect:
                bpy.ops.object.mode_set(mode='EDIT')
                obj = context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                bmfaces =  [face for face in bm.faces if face.select]
                res = extrude_faces(self, context, bm = bm, face_l = bmfaces)
                ring_edges = [face.edges[:] for face in res]
                #print("ring_edges L219", ring_edges)
            
            bpy.ops.object.mode_set(mode='OBJECT')

            #PKHG>INFO now the extruded facec have to move in normal direction
            bpy.ops.object.mode_set(mode='EDIT')
            obj = bpy.context.scene.objects.active
            bm = bmesh.from_edit_mesh(obj.data)
            todo_faces = [ face for face in bm.faces if face.select]
            for face in todo_faces:
                bmesh.ops.translate( bm, vec = face.normal * top, space = obj_matrix_local,\
                                     verts = face.verts)
            bpy.ops.object.mode_set(mode='OBJECT')
            

        elif face_type == "stepped":
            Stepped(spike_base_width = self.spike_base_width,\
                    base_height_inset = self.base_height_inset,\
                    top_spike = self.second_height,\
                    top_extra_height = self.top_extra_height,
                    use_relative_offset = self.use_relative, with_spike = self.step_with_real_spike)
            
        elif face_type == "open inset":
            startinfo = prepare(self, context, self.remove_start_faces)
            #print(startinfo)
            bm = startinfo['bm']
            
            #PKHG>INFO adjust for relative, via areas
            t = self.move_inside
            areas = startinfo['areas']
            base_height = self.base_height
            base_heights = None
            distance = None
            if self.use_relative:
                distance = [ min(t * area, 1.0) for i, area  in enumerate(areas)]
                base_heights = [ base_height * area for i, area  in enumerate(areas)]
            else:
                distance = [t] * len(areas)
                base_heights = [base_height] * len(areas)

            rings = startinfo['rings']
            centers = startinfo['centers']
            normals = startinfo['normals']
            for i in range(len(rings)):
                make_one_inset(self,context, bm = bm, ringvectors = rings[i],\
                               center = centers[i], normal = normals[i],\
                               t = distance[i], base_height = base_heights[i])
            bpy.ops.object.mode_set(mode='OBJECT')

        elif face_type == "with base":
            startinfo = prepare(self, context, self.remove_start_faces)
            #print(startinfo)
            bm = startinfo['bm']
            obj = startinfo['obj']
            object_matrix = obj.matrix_local
            
            #PKHG>INFO for relative (using areas)
            t = self.move_inside
            areas = startinfo['areas']
            base_height = self.base_height
            distance = None
            base_heights = None
            if self.use_relative:

                distance = [ min(t * area, 1.0) for i, area  in enumerate(areas)]
                base_heights = [ base_height * area for i, area  in enumerate(areas)]
            else:
                distance = [t] * len(areas)
                base_heights = [base_height] * len(areas)

            next_rings = []
            rings = startinfo['rings']
            centers = startinfo['centers']
            normals = startinfo['normals']
            for i in range(len(rings)):
                next_rings.append(make_one_inset(self,context, bm = bm, ringvectors = rings[i],\
                               center = centers[i], normal = normals[i],\
                               t = distance[i], base_height = base_heights[i]))

            prepare_ring = extrude_edges(self,context, bm = bm, edge_l_l = next_rings)

            second_height = self.second_height
            width = self.width
            vectors = [[ele.verts[:] for ele in edge] for edge in prepare_ring]
            n_ring_vecs = []
            for rings in vectors:
                v = []
                for edgv in rings:
                    v.extend(edgv)
                #PKHF>INFO no double verts allowed, coming from two adjacents edges!
                bm.verts.ensure_lookup_table()
                vv = list(set([ ele.index for ele in v]))

                vvv = [bm.verts[i].co for i in vv]
                n_ring_vecs.append(vvv)
            for i, ring in enumerate(n_ring_vecs):
                make_one_inset(self,context, bm = bm, ringvectors = ring,\
                               center = centers[i], normal = normals[i],\
                               t = width, base_height = base_heights[i]+second_height)
            bpy.ops.object.mode_set(mode='OBJECT')

        else:
        
            if face_type == "clsd vertical":
                #PKHG>DBG print("just extrude")
                obj_name = context.active_object.name
                ClosedVertical(name = obj_name,base_height = self.base_height,\
                               use_relative_base_height = self.use_relative )

            elif face_type == "open vertical":
                #PKHG>DBG print("just open extrude")
                obj_name = context.active_object.name
                OpenVertical(name = obj_name, base_height = self.base_height,\
                             use_relative_base_height = self.use_relative )

            elif face_type == "bar":
                startinfo = prepare(self,context, self.remove_start_faces)

                #print(startinfo)
                #obj = startinfo['obj']
                #object_matrix = obj.matrix_local
                #areas = startinfo['areas']
                #t = self.move_inside
                #base_height = self.base_height
                #distance = None
                #base_heights = None
                #base_height_inset = self.base_height_inset
                
                result = []
                bm = startinfo['bm']
                rings = startinfo['rings']
                centers = startinfo['centers']
                normals = startinfo['normals']
                spike_base_width = self.spike_base_width
                for i,ring  in enumerate(rings):
                    result.append(make_one_inset(self,context, bm = bm,\
                                    ringvectors = ring, center = centers[i],\
                                    normal = normals[i], t = spike_base_width))
                #PKHG>DBG print("first insets done")

                next_ring_edges_list  = extrude_edges(self,context, bm = bm,\
                                                      edge_l_l = result)
                #PKHG>DBG print("rings extruded")
                top_spike = self.top_spike
                fac = top_spike
                object_matrix = startinfo['obj'].matrix_local
                for i in range(len(next_ring_edges_list)):
                    translate_ONE_ring(self,context, bm = bm,\
                                    object_matrix = object_matrix,\
                                    ring_edges = next_ring_edges_list[i],\
                                    normal = normals[i], distance = fac )
                #PKHG>DBG print("rings translated om fac", fac)
                next_ring_edges_list_2  = extrude_edges(self,context, bm = bm,\
                                                        edge_l_l = next_ring_edges_list)
                #PKHG>DBG print("\n\nupper rings are extruded now \n----------------------\n")

                top_extra_height = self.top_extra_height
                for i in range(len(next_ring_edges_list_2)):
                    move_corner_vecs_outside(self,context, bm = bm,
                                             edge_list = next_ring_edges_list_2[i],\
                                             center = centers[i], normal = normals[i],\
                                             base_height_erlier = fac + top_extra_height,\
                                             distance = fac)
                #PKHG>DBG print("should be now corner moved")
                bpy.ops.mesh.select_mode(type="VERT")
                bpy.ops.mesh.select_more()

                bpy.ops.object.mode_set(mode='OBJECT')
       

        return {'FINISHED'}

class ReverseFacesOperator(bpy.types.Operator):
    """Reverse selected Faces"""
    bl_idname = "mesh.revers_selected_faces"
    bl_label = "reverse normal of selected faces1"
    bl_options = {'REGISTER', 'UNDO' , 'PRESET'}
    reverse_faces = BoolProperty(name = "reverse_faces", default = False,\
                    description = "revert the normal of selected faces")
    def execute(self, context):
        name = context.active_object.name
        ReverseFaces(name = name)
        return {'FINISHED'}
   
class pkhg_help(bpy.types.Operator):
	bl_idname = 'help.pkhg'
	bl_label = ''

	def draw(self, context):
		layout = self.layout
		layout.label('To use:')
		layout.label('Make a selection or selection of Faces.')
		layout.label('Extrude, rotate extrusions & more.')

	def invoke(self, context, event):
		return context.window_manager.invoke_popup(self, width = 300)
		
class VIEW3D_Faces_Panel(bpy.types.Panel):
    bl_label = "Face Extrude"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = 'Tools'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        #return True
        result = False
        active_object = context.active_object
        if active_object:
            mesh_objects_name = [el.name for el in bpy.data.objects if el.type ==\
                             "MESH"]
            if active_object.name in mesh_objects_name:
                if active_object.mode == "OBJECT":
                    result = True
        return result
    
    def draw(self, context):
        layout = self.layout
        layout.operator(AddFaces.bl_idname, "Selected Faces!")
        layout.label("Use this to separate")
        layout.label("Selected Faces Only")
        layout.label("In OBJECT mode")
       
        layout.operator(ReverseFacesOperator.bl_idname,"Reverse faceNormals")


def find_one_ring(sel_vertices):
    ring0 = sel_vertices.pop(0)
    #print("eerste weg van sel_vertices???", sel_vertices)
    #print("ring0" , ring0)
    #print(sel_vertices)
    to_delete = []
    for i, edge in enumerate(sel_vertices):
        len_nu = len(ring0)
        if len(ring0 - edge) < len_nu:
            #print(i, edge)
            to_delete.append(i)
            ring0 = ring0.union(edge)
        
    #print(ring0)
    #print(to_delete.sort())
    to_delete.reverse()
    #print(to_delete)
    for el in to_delete:
        sel_vertices.pop(el)
    #print(sel_vertices)
    return (ring0,sel_vertices)


class Stepped:
    def __init__(self, spike_base_width = 0.5, base_height_inset = 0.0, top_spike = 0.2, top_relative = False, top_extra_height = 0 , use_relative_offset = False, with_spike = False):
        #print("%%%%%%%%%%%%%%%%%%%%%%%%%Class Stepped called \n\n")
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.inset(use_boundary = True, use_even_offset=True, use_relative_offset=False, use_edge_rail = False, thickness = spike_base_width , depth = 0, use_outset=True, use_select_inset=False, use_individual=True, use_interpolate=True)
        bpy.ops.mesh.inset(use_boundary = True, use_even_offset=True, use_relative_offset = use_relative_offset, use_edge_rail = False, thickness = top_extra_height , depth = base_height_inset, use_outset=True, use_select_inset=False, use_individual=True, use_interpolate=True)
        
        bpy.ops.mesh.inset(use_boundary = True, use_even_offset=True, use_relative_offset= use_relative_offset, use_edge_rail = False, thickness = spike_base_width , depth = 0, use_outset=True, use_select_inset=False, use_individual=True, use_interpolate=True)
        bpy.ops.mesh.inset(use_boundary = True, use_even_offset=True, use_relative_offset=False, use_edge_rail = False, thickness = 0, depth = top_spike, use_outset=True, use_select_inset=False, use_individual=True, use_interpolate=True)
        if with_spike:
            bpy.ops.mesh.merge(type='COLLAPSE')
        #bm = bmesh.from_edit_mesh(obj.data) 
        #selected_faces = [face for face in bm.faces if face.select]
        #PKHF>DBG print("\n\n selected faces = ",selected_faces)
        #edges_todo = []
        bpy.ops.object.mode_set(mode='OBJECT')

class Spiked:
    def __init__(self, spike_base_width = 0.5, base_height_inset = 0.0, top_spike = 0.2, top_relative = False):
        #print("%%%%%%%%%%%%%%%%%%%%%%%%%Class Spiked called \n\n")
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.inset(use_boundary = True, use_even_offset=True, use_relative_offset=False, use_edge_rail = False, thickness = spike_base_width , depth = base_height_inset, use_outset=True, use_select_inset=False, use_individual=True, use_interpolate=True)
        bpy.ops.mesh.inset(use_boundary = True, use_even_offset=True, use_relative_offset=top_relative, use_edge_rail = False, thickness = 0 , depth = top_spike, use_outset=True, use_select_inset=False, use_individual=True, use_interpolate=True)
        bm = bmesh.from_edit_mesh(obj.data) 
        selected_faces = [face for face in bm.faces if face.select]
        #PKHF>DBG print("\n\n selected faces = ",selected_faces)
        edges_todo = []
        bpy.ops.mesh.merge(type='COLLAPSE')
        bpy.ops.object.mode_set(mode='OBJECT')


class ClosedVertical:
    def __init__(self,name = "Plane", base_height = 1, use_relative_base_height = False):
        obj = bpy.data.objects[name]
        # print("relative_base_height ", relative_base_height)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        #PKHG>INFO deselect chosen faces
        sel = [f for f in bm.faces if f.select]
        for f in sel: 
            f.select = False
        res = bmesh.ops.extrude_discrete_faces(bm,faces=sel )
        #PKHG>INFO select extruded faces
        for f in res['faces']: 
            f.select = True
           
        lood = Vector((0,0,1))
        #PKHG>INFO adjust extrusion by a vector! test just only lood
        factor = base_height
        for face  in res['faces']:
            if use_relative_base_height:
                area = face.calc_area()
                #PKHG>DBG print("area of ", face.index, "  is", area)
                factor = area * base_height
            else:
                factor = base_height
            for el in face.verts:
                tmp = el.co + face.normal * factor
                el.co = tmp
        
        #me = bpy.data.meshes.new("Mesh")
        me = bpy.data.meshes[name]
        bm.to_mesh(me)
        bm.free()


        # Add the mesh to the scene
        #PKHG>INFO not needed?
        """
        scene = bpy.context.scene
        obj = bpy.data.objects.new("Object", me)
        scene.objects.link(obj)
        

        # Select and make active
        scene.objects.active = obj
        obj.select = False
        """
#bmesh.ops.reverse_faces(bm, faces)

class ReverseFaces:
    def __init__(self, name = "Cube"):
        obj = bpy.data.objects[name]
        me = obj.data
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.new()
        bm.from_mesh(me)
        bpy.ops.object.mode_set(mode='OBJECT')
        sel = [f for f in bm.faces if f.select]
        #OK so far 
       
        #print("sel in ReverseFaces = ", sel)
        bmesh.ops.reverse_faces(bm, faces = sel)
        bm.to_mesh(me)
        bm.free()
       

class OpenVertical:
    def __init__(self,name = "Plane", base_height = 1, use_relative_base_height = False):

        obj = bpy.data.objects[name]
        #PKHG>DBG print("relative_base_height ", relative_base_height)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        #PKHG>INFO deselect chosen faces
        sel = [f for f in bm.faces if f.select]
        for f in sel: 
            f.select = False
        res = bmesh.ops.extrude_discrete_faces(bm,faces=sel )
        #PKHG>INFO select extruded faces
        for f in res['faces']: 
            f.select = True
           
        #PKHG>INFO adjust extrusion by a vector! test just only lood
        factor = base_height
        for face  in res['faces']:
            if use_relative_base_height:
                area = face.calc_area()
                #PKHG>DBG print("area of ", face.index, "  is", area)
                factor = area * base_height
            else:
                factor = base_height
            for el in face.verts:
                tmp = el.co + face.normal * factor
                el.co = tmp
        
        #me = bpy.data.meshes.new("Mesh")
        
        #bmesh.ops.delete(bm,geom = res['faces'] )
        me = bpy.data.meshes[name]
        bm.to_mesh(me)
        bm.free()
    
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.editmode_toggle()


        # Add the mesh to the scene
        #PKHG>INFO not needed?
        """
        scene = bpy.context.scene
        obj = bpy.data.objects.new("Object", me)
        scene.objects.link(obj)
        

        # Select and make active
        scene.objects.active = obj
        obj.select = False
        """

        '''
use_boundary=True, 
use_even_offset=True, 
use_relative_offset=False, 
use_edge_rail=False, 
use_outset=False, 
use_select_inset=True, 
use_individual=False, 
use_interpolate=True
        '''
 
class StripFaces:
   #PKHG>OLD def __init__(self,  thickness = 0.5, depth = 0.2, type = 0):
    def __init__(self, use_boundary = True, use_even_offset=True, use_relative_offset=False, use_edge_rail = True, thickness = 0.0, depth = 0.0, use_outset = False, use_select_inset = False, use_individual = True, use_interpolate = True):
        '''
        use_boundary = args[0]
        use_even_offset = args[1]
        use_relative_offset = args[2]
        use_edge_rail = args[3]
        thickness = args[4]
        depth = args[5]
        use_outset = args[6]
        use_select_inset = args[7] 
        use_individual = args[8]
        use_interpolate = args[9]
        '''

        #print("StripFaces called" )
        #obj = bpy.data.objects[name]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.inset(use_boundary = use_boundary, use_even_offset=True, use_relative_offset=False, use_edge_rail = True, thickness = thickness, depth = depth, use_outset=use_outset, use_select_inset=use_select_inset, use_individual=use_individual, use_interpolate=use_interpolate)
        bpy.ops.object.mode_set(mode='OBJECT')
        #type = 0
        #PKHG>IMFO only 3 parameters inc execution context supported!! 
        #PKHG>IMPOSSIBLE: bpy.ops.mesh.inset(use_boundary , use_even_offset, use_relative_offset, use_edge_rail,thickness, depth, use_outset, use_select_inset,use_individual, use_interpolate)
        #bpy.ops.mesh.inset(use_boundary = use_boundary, use_even_offset=True, use_relative_offset=False, use_edge_rail = True, thickness = thickness, depth = depth, use_outset=use_outset, use_select_inset=use_select_inset, use_individual=use_individual, use_interpolate=use_interpolate)
        if False:
            bpy.ops.mesh.inset(use_boundary, use_even_offset, use_relative_offset, use_edge_rail , thickness, depth, use_outset, use_select_inset, use_individual, use_interpolate)
        elif type == 0:
            bpy.ops.mesh.inset(use_boundary = True, use_even_offset=True, use_relative_offset=False, use_edge_rail = True, thickness = thickness, depth= depth, use_outset=False, use_select_inset=False, use_individual = True , use_interpolate=True)
        elif type == 1:
            bpy.ops.mesh.inset(use_boundary = True, use_even_offset=True, use_relative_offset= False, use_edge_rail = True, thickness = thickness, depth = depth, use_outset=False, use_select_inset=False, use_individual=True, use_interpolate=False)
            bpy.ops.mesh.delete(type='FACE')           

        elif type == 2:
            bpy.ops.mesh.inset(use_boundary = True, use_even_offset=False, use_relative_offset = True, use_edge_rail = True, thickness = thickness, depth = depth, use_outset=False, use_select_inset=False, use_individual=True, use_interpolate=False)
            bpy.ops.mesh.delete(type='FACE')
            
        elif type == 3:
            bpy.ops.mesh.inset(use_boundary = True, use_even_offset=False, use_relative_offset = True, use_edge_rail = True, thickness = depth, depth = thickness, use_outset=False, use_select_inset=False, use_individual=True, use_interpolate=True)
            bpy.ops.mesh.delete(type='FACE')
        elif type == 4:
            bpy.ops.mesh.inset(use_boundary = True, use_even_offset=False, use_relative_offset = True, use_edge_rail = True, thickness = thickness, depth = depth, use_outset = True, use_select_inset=False, use_individual=True, use_interpolate=True)
            bpy.ops.mesh.inset(use_boundary = True, use_even_offset=False, use_relative_offset = True, use_edge_rail = True, thickness = thickness , depth = depth , use_outset = True, use_select_inset=False, use_individual=True, use_interpolate=True)

            '''
            bpy.ops.mesh.inset(use_boundary = True, use_even_offset=False, use_relative_offset = True, use_edge_rail = True, thickness = 0.5, depth = thickness * 2, use_outset = True, use_select_inset=False, use_individual=True, use_interpolate=True)
            bpy.ops.mesh.inset(use_boundary = True, use_even_offset=False, use_relative_offset = True, use_edge_rail = True, thickness = 0.5, depth = thickness , use_outset = True, use_select_inset=False, use_individual=True, use_interpolate=True)
            '''
            #bpy.ops.mesh.delete(type='FACE')

        bpy.ops.mesh.delete(type='FACE')

        bpy.ops.object.mode_set(mode='OBJECT')

#http://en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro/Advanced_Tutorials/Python_Scripting/Addon_User_Interface
def prepare(self, context, remove_start_faces = True):
    """Start for a face selected change of faces
       select an object of type mesh, with  activated severel (all) faces
    """
    #print("prepare called")
    obj = bpy.context.scene.objects.active
    #objmode = obj.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    selectedpolygons = [el for el in obj.data.polygons if el.select]
    #edge_index_list = [[el.index for el in face.edges  ] for face in selectedpolygons]
    #print("start edge_index_list", edge_index_list)
    #PKHG>INFO copies of the vectors are needed, otherwise Blender crashes!
    centers = [face.center for face in selectedpolygons]
    centers_copy = [Vector((el[0],el[1],el[2])) for el in centers]
    normals = [face.normal for face in selectedpolygons]
    normals_copy = [Vector((el[0],el[1],el[2])) for el in normals]
    vertindicesofpolgons = [[vert for vert in face.vertices] for face in selectedpolygons]
    vertVectorsOfSelectedFaces = [[obj.data.vertices[ind].co for ind in  vertIndiceofface]\
                    for vertIndiceofface in  vertindicesofpolgons]
    vertVectorsOfSelectedFaces_copy = [[Vector((el[0],el[1],el[2])) for el in listofvecs]\
                         for listofvecs in vertVectorsOfSelectedFaces]
   
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    selected_bm_faces = [ ele for ele in bm.faces if ele.select]
    selected_edges_per_face_ind = [[ele.index for ele in face.edges] for face in selected_bm_faces]
    #print("\n\nPKHG>DBG selected_edges_per_face", selected_edges_per_face_ind)
    indices = [el.index for el in selectedpolygons]
    #print("indices", indices, bm.faces[:])
    selected_faces_areas = [bm.faces[:][i] for i in indices ]
    tmp_area =  [el.calc_area() for el in selected_faces_areas]
    
    #PKHG>INFO, selected faces are removed, only their edges are used!
    if remove_start_faces:    
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.data.update()
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

    start_ring_raw = [[bm.verts[ind].index for ind in  vertIndiceofface]  \
                    for vertIndiceofface in  vertindicesofpolgons]
    start_ring = []
    
    for el in start_ring_raw:
        #el.sort()
        start_ring.append(set(el))
    bm.edges.ensure_lookup_table()

    bm_selected_edges_l_l = [[bm.edges[i] for i in bm_ind_list  ] for bm_ind_list in  selected_edges_per_face_ind]            

    result = {'obj': obj, 'centers':centers_copy, 'normals': normals_copy,\
              'rings': vertVectorsOfSelectedFaces_copy, 'bm': bm ,\
              'areas': tmp_area,'startBMRingVerts':start_ring,\
              'base_edges':bm_selected_edges_l_l}
    return result



def make_one_inset(self,context, bm = None, ringvectors = None, center = None,\
                   normal = None, t = None, base_height = 0):
    """a face will get  'inserted' faces to create  (normaly) 
        a hole it t is > 0 and < 1)
    """
    tmp = []
    #PKHG>DBG print("ringvectors", ringvectors,"\ncenter=", center)
    for el in ringvectors:
        tmp.append((el * (1 - t) + center * t) + normal * base_height)

    tmp = [bm.verts.new(v) for v in tmp] #the new corner bmvectors
    #PKHG>INFO so to say sentinells, ot use ONE for ...
    tmp.append(tmp[0])
    vectorsFace_i = [bm.verts.new(v) for v in ringvectors]
    vectorsFace_i.append(vectorsFace_i[0])
    myres = []
    for ii in range(len(vectorsFace_i) - 1):
        #PKHG>INFO next line: sequence important! for added edge 
        bmvecs = [vectorsFace_i[ii],vectorsFace_i[ii + 1], tmp[ii + 1], tmp[ii]] 
        res = bm.faces.new(bmvecs)
        myres.append(res.edges[2])
        myres[-1].select = True #PKHG>INFO to be used later selected!
    return (myres)




def extrude_faces(self, context, bm = None, face_l = None):
    """ 
       to make a ring extrusion!
    """
    all_results = []
    res = bmesh.ops.extrude_discrete_faces(bm, faces = face_l)['faces']
    #print(res)
    for face in res:
        face.select = True
    #for face in face_l:
        #for edge in edge_l:
        #    edge.select = False
        
        #print(res)
        #tmp = [ ele for ele in res['geom'] if isinstance(ele, bmesh.types.BMFace)]
        #for edge in tmp:
        #    edge.select = True
        #all_results.append(tmp)
    return res

def extrude_edges(self, context, bm = None, edge_l_l = None):
    """ 
       to make a ring extrusion!
    """
    all_results = []
    for edge_l in edge_l_l:
        for edge in edge_l:
            edge.select = False
        res = bmesh.ops.extrude_edge_only(bm, edges = edge_l)
        tmp = [ ele for ele in res['geom'] if isinstance(ele, bmesh.types.BMEdge)]
        for edge in tmp:
            edge.select = True
        all_results.append(tmp)
    return all_results
        

def translate_ONE_ring(self,context, bm = None, object_matrix = None, ring_edges = None ,\
                       normal = (0,0,1), distance = 0.5):
    """
       translate a ring in given (normal?!) direction with given (global) amount
    """
    tmp = []
    for edge in ring_edges:
        tmp.extend(edge.verts[:])
    #PKHG>INFO no double vertices allowed by bmesh!
    tmp = set(tmp)
    tmp = list(tmp)
    bmesh.ops.translate(bm, vec = normal * distance, space = object_matrix, verts = tmp)
    return ring_edges
    #PKHG>INFO relevant edges will stay selected
    
def move_corner_vecs_outside(self, context, bm = None, edge_list = None, center = None, normal = None,\
                             base_height_erlier = 0.5, distance = 0.5):
    """
       move corners (outside meant mostly) dependent on the parameters
    """
    tmp = []
    for edge in edge_list:
        tmp.extend([ele for ele in edge.verts if isinstance(ele, bmesh.types.BMVert)])
    #PKHG>INFO to remove vertices, they are all twices used in the ring!
    tmp = set(tmp)
    tmp = list(tmp)
    
    for i in range(len(tmp)):
        vec = tmp[i].co
        direction = vec  + (vec - ( normal * base_height_erlier + center))* distance
        tmp[i].co = direction

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
