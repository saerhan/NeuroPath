import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
import numpy.linalg as la
import math
global renderer
renderer = slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow().GetRenderers().GetFirstRenderer()
renderWindow = slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = slicer.app.layoutManager().threeDWidget(0).threeDView().interactor()
renderWindowInteractor.SetRenderWindow(renderWindow)
 
#
# NeuroPath
#
 
class NeuroPath(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
 
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "NeuroPath" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
 
#
# NeuroPathWidget
#
 
class NeuroPathWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
 
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
 
    # Instantiate and connect widgets ...
 
    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)
 
    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    #
    # Fiducial  Selector
    #
    self.ROISelector = slicer.qMRMLNodeComboBox()
    self.ROISelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
    self.ROISelector.selectNodeUponCreation = True
    self.ROISelector.addEnabled = True
    self.ROISelector.removeEnabled = True
    self.ROISelector.noneEnabled = True
    self.ROISelector.showHidden = False
    self.ROISelector.showChildNodeTypes = False
    self.ROISelector.setMRMLScene( slicer.mrmlScene )
    self.ROISelector.setToolTip( "Pick the ROI Interactive Box to define the region for labeling of Fibers." )
    parametersFormLayout.addRow("Fiducial : ", self.ROISelector)
    self.ROISelector.connect("currentNodeChanged(vtkMRMLNode*)", self.OnSelect_ROI)
 
    #
    # Sphere value
    #
    self.SliderSphere = ctk.ctkSliderWidget()
    self.SliderSphere.singleStep = 0.1
    self.SliderSphere.minimum = 0
    self.SliderSphere.maximum = 75
    self.SliderSphere.value = 10
    self.SliderSphere.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    self.SliderSphere.valueChanged.connect(self.onSliderChange)
    parametersFormLayout.addRow("Sphere Radius", self.SliderSphere)
     
    #
    # Cylinder value
    #
    self.SliderCylinder = ctk.ctkSliderWidget()
    self.SliderCylinder.singleStep = 0.1
    self.SliderCylinder.minimum = 0
    self.SliderCylinder.maximum = 50
    self.SliderCylinder.value = 7
    self.SliderCylinder.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    self.SliderCylinder.valueChanged.connect(self.onSliderChange)
    parametersFormLayout.addRow("Cylinder Radius", self.SliderCylinder)
     
     
    #
    # Cylinder value
    #
    self.SliderCylinder_2 = ctk.ctkSliderWidget()
    self.SliderCylinder_2.singleStep = 0.1
    self.SliderCylinder_2.minimum = 0
    self.SliderCylinder_2.maximum = 120
    self.SliderCylinder_2.value = 15
    self.SliderCylinder_2.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    self.SliderCylinder_2.valueChanged.connect(self.onSliderChange)
    parametersFormLayout.addRow("Cylinder Height", self.SliderCylinder_2)
    #
    # Apply Button
    #
    self.applyButton_7 = qt.QCheckBox("Update the graphics")
    self.applyButton_7.toolTip = "Run the algorithm!!."
    #self.applyButton_5.enabled = True
    parametersFormLayout.addRow("Image threshold", self.applyButton_7)
    # connections
    self.applyButton_7.stateChanged.connect(self.onApplyButton_7)
     
     
  def OnSelect_ROI(self):
      global ftone,fttwo,ft12,fss,markupNode,sphere,cylinder,logic,Actor2, plane, actor3
      global ft12
      logic = NeuroPathLogic()
      ftone = [0,0,0]
      fttwo = [0,0,0]
      fss = [0,0,0]
      markupNode = self.ROISelector.currentNode()
      sphere = vtk.vtkSphereSource()
      sphere.SetRadius(10)
      sphere.SetThetaResolution(30)
      sphere.SetPhiResolution(30)
      Mapper = vtk.vtkPolyDataMapper()
      Mapper.SetInputConnection(sphere.GetOutputPort())
      Actor = vtk.vtkActor()
      Actor.SetMapper(Mapper)
      Actor.GetProperty().SetColor(0,1,0)
      #Actor.GetProperty().SetOpacity(0.9)
      #renderer.AddActor(Actor)
      clip = vtk.vtkClipPolyData()
      clip.SetValue(0);
      clip.GenerateClippedOutputOn();
      clip.SetInputConnection(sphere.GetOutputPort())
      plane = vtk.vtkPlane()
      plane.SetNormal(0.0, 1.0, 0.0)
      plane.SetOrigin(0.0, 10.0, 0.0)
      clip.SetClipFunction(plane)
      polyDataMapper = vtk.vtkPolyDataMapper()
      polyDataMapper.SetInputConnection(clip.GetOutputPort()) 
      actor3 = vtk.vtkActor()
      actor3.SetMapper(polyDataMapper)
      actor3.GetProperty().SetColor(0,1,0)
      renderer.AddActor(actor3)
      cylinder = vtk.vtkCylinderSource()
      cylinder.SetRadius(5)
      cylinder.SetHeight(10)
      cylinder.SetResolution(100)
      cylinder.CappingOff()
      Mapper2 = vtk.vtkPolyDataMapper()
      Mapper2.SetInputConnection(cylinder.GetOutputPort())
      Actor2 = vtk.vtkActor()
      Actor2.SetMapper(Mapper2)
      Actor2.GetProperty().SetColor(0,0,1)
      #Actor2.GetProperty().SetOpacity(0.9)
      renderer.AddActor(Actor2)
      Transform = vtk.vtkTransform()
      Transform.PostMultiply()
      Actor2.SetUserTransform(Transform)
      markupNode.GetNthFiducialPosition(0,ftone)
      markupNode.GetNthFiducialPosition(1,fttwo)
      markupNode.GetNthFiducialPosition(2,fss)
      R_sphere =  self.SliderSphere.value
      R_cylinder = self.SliderCylinder.value
      H_cylinder = self.SliderCylinder_2.value
      ft1 = np.array(ftone)
      ft2 = np.array(fttwo)
      fs = np.array(fss)
      ft12  = ft1-ft2
      Y_axis = np.array([0,1,0])
      C_Cent = ((ft1+ft2)/2)
      sphere.SetCenter(fs)
      cylinder.SetCenter(C_Cent)
      cylinder.SetRadius(R_cylinder)
      cylinder.SetHeight(H_cylinder)
      sphere.SetRadius(R_sphere)
      Transform.Translate(-C_Cent[0],-C_Cent[1],-C_Cent[2])
      Transform.RotateWXYZ(-1*np.degrees(logic.py_ang(ft12,Y_axis)),np.cross(ft12,Y_axis))
      Transform.Translate(C_Cent[0],C_Cent[1],C_Cent[2])
  def cleanup(self):
    pass
  def onSliderChange(self):
    global R_sphere,R_cylinder,H_cylinder
    R_sphere =  self.SliderSphere.value
    R_cylinder = self.SliderCylinder.value
    H_cylinder = self.SliderCylinder_2.value
    logic.run_7()
  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()
 
  def onApplyButton(self):
     
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)
  def onApplyButton_7(self):#Compute
     if self.applyButton_7.isChecked():
        logic.run_7()
#
# NeuroPathLogic
#
 
class NeuroPathLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
 
  def run_7(self):#Run the computation
    ft1 = np.array(ftone)
    ft2 = np.array(fttwo)
    ft12  = ft1-ft2
    print(fttwo)
    markupNode.GetNthFiducialPosition(0,ftone)
    markupNode.GetNthFiducialPosition(1,fttwo)
    markupNode.GetNthFiducialPosition(2,fss)
    ft1 = np.array(ftone)
    ft2 = np.array(fttwo)
    fs = np.array(fss)
    C_Cent = ((ft1+ft2)/2)
    cylinder.SetCenter(C_Cent)
    ft12  = ft1-ft2
    plane.SetNormal(ft12)
    plane.SetOrigin(ft1)
    Y_axis = np.array([0,1,0])
    sphere.SetCenter(fs)
    cylinder.SetRadius(R_cylinder)
    cylinder.SetHeight(H_cylinder)
    sphere.SetRadius(R_sphere)
    Transform = vtk.vtkTransform()
    Transform.PostMultiply()
    Actor2.SetUserTransform(Transform)
    Transform.Translate(-C_Cent[0],-C_Cent[1],-C_Cent[2])
    Transform.RotateWXYZ(-1*np.degrees(logic.py_ang(ft12,Y_axis)),np.cross(ft12,Y_axis))
    Transform.Translate(C_Cent[0],C_Cent[1],C_Cent[2])
    print(cylinder.GetCenter())
 
  def py_ang(self,v1, v2):
   """ Returns the angle in radians between vectors 'v1' and 'v2'    """
   cosang = np.dot(v1, v2)
   sinang = la.norm(np.cross(v1, v2))
   return np.arctan2(sinang, cosang)
 
 
class NeuroPathTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
 
  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)
 
  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_NeuroPath1()
 
  def test_NeuroPath1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """
 
    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )
 
    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')
 
    volumeNode = slicer.util.getNode(pattern="FA")
    logic = NeuroPathLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
