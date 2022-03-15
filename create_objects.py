import random
import logging

import maya.cmds as cmds

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtCore import QFile, QObject
from PySide2 import QtGui, QtWidgets, QtCore


logger = logging.getLogger("create_objects")
logger.setLevel(logging.WARNING)

# create console handler with debug log level
c_handler = logging.StreamHandler()

# create file handler with debug log level
# log_path = "/Users/sanazsanayei/Library/Preferences/Autodesk/maya/2022/scripts/scene_builder/log.log"
# f_handler = logging.FileHandler(filename=log_path)

# create formatter and add it to handlers
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
c_handler.setFormatter(formatter)
# f_handler.setFormatter(formatter)

# add handlers to logger
logger.addHandler(c_handler)
# logger.addHandler(f_handler)


class WrapperRandomShape:

    def __init__(self, user_shape):
        self.user_shape = user_shape

        self.shape = ""
        self.transform = ""
        self.shader_name = ""
        self.shading_group = ""
        self.matrix = []
        self.color = []

        self.create_object()
        self.set_random_position()
        self.create_material()
        self.assign_material()


    def create_object(self):
        if self.user_shape == "Cube":
            self.transform, self.shape = cmds.polyCube()
            logger.info("cube created : transform: {} - shape: {}".format(self.transform, self.shape))
        elif self.user_shape == "Sphere":
            self.transform, self.shape = cmds.polySphere()
            logger.info("sphere created : transform: {} , shape: {}".format(self.transform, self.shape))
        elif self.user_shape == "Cylinder":
            self.transform, self.shape = cmds.polyCylinder()
            logger.info("cylinder created : transform: {} , shape: {}".format(self.transform, self.shape))
        elif self.user_shape == "Cone":
            self.transform, self.shape = cmds.polyCone()
            logger.info("cone created : transform: {} , shape: {}".format(self.transform, self.shape))
        elif self.user_shape == "Torus":
            self.transform, self.shape = cmds.polyTorus()
            logger.info("torus created : transform: {} , shape: {}".format(self.transform, self.shape))

    def create_material(self):
        self.shader_name = cmds.shadingNode("blinn", asShader=True)
        logger.info("shader name is {}".format(self.shader_name))
        self.shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        logger.info("shading group is {}".format(self.shading_group))
        a = cmds.connectAttr('{}.outColor'.format(self.shader_name), '{}.surfaceShader'.format(self.shading_group),
                             f=True)
        logger.debug("shader name and shading group are connected : {}".format(a))

    def assign_material(self):
        b = cmds.sets(self.transform, edit=True, forceElement=self.shading_group)
        logger.info("material assigned: {}".format(b))

    def set_shader_color(self, color_array):
        cmds.setAttr(self.shader_name + ".color", color_array[0], color_array[1], color_array[2], type="double3")
        self.color = color_array
        logger.info("color_array:{},{},{}".format(color_array[0], color_array[1], color_array[2]))

    def set_random_position(self):
        x = random.uniform(-10.0, 10.0)
        y = random.uniform(-10.0, 10.0)
        z = random.uniform(-10.0, 10.0)
        cmds.move(x, y, z, self.transform)
        self.matrix = [x, y, z]
        logger.info("object set in a random position: {},{},{}".format(x, y, z))

    def clear_object(self):
        cmds.delete([self.transform, self.shader_name, self.shading_group])
        logger.info("{} deleted".format(self.transform))



class SceneBuilder(QObject):

    def __init__(self, ui_file, parent=None):
        super(SceneBuilder, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.window.setMinimumSize(900,500)
        self.create_menu()
        self.created_objects = []
        self.last_cube_color = [0, 0, 0]
        self.last_sphere_color = [0, 0, 0]
        self.last_cylinder_color = [0, 0, 0]
        self.last_cone_color = [0, 0, 0]
        self.last_torus_color = [0, 0, 0]

        # connections
        self.window.setWindowTitle("Maya Scene Builder")

        self.window.cancel_btn.clicked.connect(self.window.close)
        self.window.clear_btn.clicked.connect(self.clear_objects)
        self.window.ok_btn.clicked.connect(self.create_object)
        # objects buttons
        self.window.cube_color_btn.clicked.connect(self.show_color_selection_cube)
        self.window.sphere_color_btn.clicked.connect(self.show_color_selection_sphere)
        self.window.cylinder_color_btn.clicked.connect(self.show_color_selection_cylinder)
        self.window.cone_color_btn.clicked.connect(self.show_color_selection_cone)
        self.window.torus_color_btn.clicked.connect(self.show_color_selection_torus)
        self.create_pixmap()
        self.window.cube_sb.setRange(0, 500)
        self.window.sphere_sb.setRange(0, 500)
        self.window.cylinder_sb.setRange(0, 500)
        self.window.cone_sb.setRange(0, 500)
        self.window.torus_sb.setRange(0, 500)

    def update_data_table(self):
        self.window.tableWidget.setColumnWidth(4, 250)
        self.window.tableWidget.clearContents()
        self.window.tableWidget.setRowCount(len(self.created_objects))

        for wrapper_instance in self.created_objects:
            formatted_color = [float(f"{float(x):.2}") for x in wrapper_instance.color]
            attrs = [wrapper_instance.transform,
                     wrapper_instance.shape,
                     wrapper_instance.shader_name,
                     wrapper_instance.shading_group,
                     formatted_color,
                     [float(f"{float(x):.2}") for x in wrapper_instance.matrix]]
            for attr in attrs:
                item = QtWidgets.QTableWidgetItem(str(attr))
                self.window.tableWidget.setItem(self.created_objects.index(wrapper_instance), attrs.index(attr), item)

            color_item = self.window.tableWidget.item(self.created_objects.index(wrapper_instance),
                                                          attrs.index(formatted_color))

            pixmap = QtGui.QPixmap(25, 25)
            pixmap.fill(QtGui.QColor(wrapper_instance.color[0]*255,
                                     wrapper_instance.color[1]*255,
                                     wrapper_instance.color[2]*255))
            icon = QtGui.QIcon(pixmap)
            color_item.setIcon(icon)
            logger.warning("color is : {},{},{}".format(wrapper_instance.color[0]*255,
                                                        wrapper_instance.color[1]*255,
                                                        wrapper_instance.color[2]*255))

    def shuffle_cube(self):
        self.shuffle_objects(kind="Cube")

    def shuffle_sphere(self):
        self.shuffle_objects(kind="Sphere")

    def shuffle_cylinder(self):
        self.shuffle_objects(kind="Cylinder")

    def shuffle_cone(self):
        self.shuffle_objects(kind="Cone")

    def shuffle_torus(self):
        self.shuffle_objects(kind="Torus")

    def clear_cube_objects(self):
        self.clear_objects(kind="Cube")

    def clear_sphere_objects(self):
        self.clear_objects(kind="Sphere")

    def clear_cylinder_objects(self):
        self.clear_objects(kind="Cylinder")

    def clear_cone_objects(self):
        self.clear_objects(kind="Cone")

    def clear_torus_objects(self):
        self.clear_objects(kind="Torus")

    def create_menu(self):
        mapping = {self.window.cube_action_btn: [self.clear_cube_objects, self.update_color_cube, self.shuffle_cube],
                   self.window.sphere_action_btn: [self.clear_sphere_objects, self.update_color_sphere,
                                                   self.shuffle_sphere],
                   self.window.cylinder_action_btn: [self.clear_cylinder_objects, self.update_color_cylinder,
                                                     self.shuffle_cylinder],
                   self.window.cone_action_btn: [self.clear_cone_objects, self.update_color_cone, self.shuffle_cone],
                   self.window.torus_action_btn: [self.clear_torus_objects, self.update_color_torus,
                                                  self.shuffle_torus]}

        for button, (clear_slot, color_slot,shuffle_slot) in mapping.items():
            menu = QtWidgets.QMenu(button)
            clear_action = QtWidgets.QAction("Clear", button)
            clear_action.triggered.connect(clear_slot)

            update_action = QtWidgets.QAction("Update Color", button)
            update_action.triggered.connect(color_slot)

            shuffle_action = QtWidgets.QAction("Shuffle objects", button)
            shuffle_action.triggered.connect(shuffle_slot)

            menu.addAction(update_action)
            menu.addAction(clear_action)
            menu.addAction(shuffle_action)
            button.setMenu(menu)

    # black pixmap is filled in all labels
    def create_pixmap(self):
        pixmap = QtGui.QPixmap(50, 25)
        pixmap.fill(0, 0, 0)
        self.window.cube_label.setPixmap(pixmap)
        self.window.sphere_label.setPixmap(pixmap)
        self.window.cylinder_label.setPixmap(pixmap)
        self.window.cone_label.setPixmap(pixmap)
        self.window.torus_label.setPixmap(pixmap)

        # selected color is updated in pixmap

    def update_pixmap(self, selected_color):
        pixmap = QtGui.QPixmap(50, 25)
        pixmap.fill(selected_color)
        return pixmap

    def show_color_selection_cube(self):
        # user pick her color
        selected_color = QtWidgets.QColorDialog.getColor()
        # RGB format of selected color is return
        self.last_cube_color = selected_color.getRgbF()
        # labels are updated by selected color
        self.window.cube_label.setPixmap(self.update_pixmap(selected_color))

    def update_color_cube(self):
        self.update_color(kind="Cube", color=self.last_cube_color)

    def show_color_selection_sphere(self):
        selected_color = QtWidgets.QColorDialog.getColor()
        self.last_sphere_color = selected_color.getRgbF()
        self.window.sphere_label.setPixmap(self.update_pixmap(selected_color))

    def update_color_sphere(self):
        self.update_color(kind="Sphere", color=self.last_sphere_color)

    def show_color_selection_cylinder(self):
        selected_color = QtWidgets.QColorDialog.getColor()
        self.last_cylinder_color = selected_color.getRgbF()
        self.window.cylinder_label.setPixmap(self.update_pixmap(selected_color))

    def update_color_cylinder(self):
        self.update_color(kind="Cylinder", color=self.last_cylinder_color)

    def show_color_selection_cone(self):
        selected_color = QtWidgets.QColorDialog.getColor()
        self.last_cone_color = selected_color.getRgbF()
        self.window.cone_label.setPixmap(self.update_pixmap(selected_color))

    def update_color_cone(self):
        self.update_color(kind="Cone", color=self.last_cone_color)

    def show_color_selection_torus(self):
        selected_color = QtWidgets.QColorDialog.getColor()
        self.last_torus_color = selected_color.getRgbF()
        self.window.torus_label.setPixmap(self.update_pixmap(selected_color))

    def update_color_torus(self):
        self.update_color(kind="Torus", color=self.last_torus_color)

    def create_objects(self, kind, count, selected_color):
        progress_dialog = QtWidgets.QProgressDialog("Waiting to Process...", "Cancel", 0, count, self.window)
        progress_dialog.setWindowTitle("Progress...")
        progress_dialog.setValue(0)
        progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        progress_dialog.show()
        QtCore.QCoreApplication.processEvents()

        for i in range(count):
            if progress_dialog.wasCanceled():
                break
            progress_dialog.setLabelText("Processing Operation: {} of {} from {}".format(i, count, kind))
            progress_dialog.setValue(i + 1)
            QtCore.QCoreApplication.processEvents()

            # call wrapper class for selected object
            wrapper = WrapperRandomShape(kind)

            # set selected color
            wrapper.set_shader_color(selected_color)

            # add instances to the list
            self.created_objects.append(wrapper)

        self.update_data_table()

    def create_object(self):
        if self.window.cube_cb.isChecked():
            self.create_objects("Cube", self.window.cube_sb.value(), self.last_cube_color)
        if self.window.sphere_cb.isChecked():
            self.create_objects("Sphere", self.window.sphere_sb.value(), self.last_sphere_color)
        if self.window.cylinder_cb.isChecked():
            self.create_objects("Cylinder", self.window.cylinder_sb.value(), self.last_cylinder_color)
        if self.window.cone_cb.isChecked():
            self.create_objects("Cone", self.window.cone_sb.value(), self.last_cone_color)
        if self.window.torus_cb.isChecked():
            self.create_objects("Torus", self.window.torus_sb.value(), self.last_torus_color)

        checks = [self.window.cube_cb.isChecked(),
                  self.window.sphere_cb.isChecked(),
                  self.window.cylinder_cb.isChecked(),
                  self.window.cone_cb.isChecked(),
                  self.window.torus_cb.isChecked()]
        if not any(checks):
            QMessageBox.warning(self.window, "Warning!", "No object selected!")

    def shuffle_objects(self, kind=""):
        for wrapper_instance in self.created_objects:
            if kind:
                if kind == wrapper_instance.user_shape:
                    wrapper_instance.set_random_position()
            else:
                wrapper_instance.set_random_position()
        self.update_data_table()

    def update_color(self, kind="", color=[0, 0, 0]):
        for wrapper_instance in self.created_objects:
            if kind:
                if kind == wrapper_instance.user_shape:
                    wrapper_instance.set_shader_color(color)
            else:
                wrapper_instance.set_shader_color(color)
        self.update_data_table()

    def clear_objects(self, kind=''):
        deleted_items = []
        for wrapper_instance in self.created_objects:
            if kind:
                if kind == wrapper_instance.user_shape:
                    deleted_items.append(wrapper_instance)
                    wrapper_instance.clear_object()
            else:
                wrapper_instance.clear_object()
                deleted_items.append(wrapper_instance)

        for item in deleted_items:
            if item in self.created_objects:
                self.created_objects.remove(item)
        self.update_data_table()

def launch():
    print("launch application")
    cmds.file(f=True, new=True)
    form = SceneBuilder('/Users/sanazsanayei/PycharmProjects/pythonProject/my_tool/Shape.ui')
    form.window.exec_()
