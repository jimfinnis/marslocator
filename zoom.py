""" QtImageViewer.py: PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

"""

import os.path

from PySide2.QtCore import Qt, QRectF, Signal, QPoint
from PySide2.QtGui import QImage, QPixmap, QPainterPath, QKeyEvent, QWheelEvent
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QFileDialog

__author__ = "Marcel Goldschen-Ohm <marcel.goldschen@gmail.com>"
__version__ = '0.9.0'


class QtImageViewer(QGraphicsView):
    """ PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.

    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)

    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    Keys:
        Backspace: Zoom out (i.e. remove last zoom box).
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    leftMouseButtonPressed = Signal(float, float)
    rightMouseButtonPressed = Signal(float, float)
    leftMouseButtonReleased = Signal(float, float)
    rightMouseButtonReleased = Signal(float, float)
    leftMouseButtonDoubleClicked = Signal(float, float)
    rightMouseButtonDoubleClicked = Signal(float, float)
    midMouseButtonPressed = Signal(float, float)
    midMouseButtonReleased = Signal(float, float)
    imageUpdated = Signal()

    def __init__(self, parent):
        QGraphicsView.__init__(self, parent)

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is dealt with elsewhere (if at all)
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = Qt.KeepAspectRatio
        # if this is true, we keep the aspect ratio the same as we zoom in and out with selection dragging
        self.fixedAspect = True
        self.wheelZoomFactor = 1.3      # how fast the wheel zooms in and out

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True
        self.zoomFactor = 1  # initial zoom
        self.aspect = 1  # will be set to the aspect ratio of the image

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def clearImage(self):
        """ Removes the current image pixmap from the scene if it exists.
        """
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.aspect = pixmap.width() / pixmap.height()
        self.setSceneRect(QRectF(pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    def loadImageFromFile(self, fileName=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(fileName) == 0:
            if QT_VERSION_STR[0] == '4':
                fileName = QFileDialog.getOpenFileName(self, "Open image file.")
            elif QT_VERSION_STR[0] == '5':
                fileName, dummy = QFileDialog.getOpenFileName(self, "Open image file.")
        if len(fileName) and os.path.isfile(fileName):
            image = QImage(fileName)
            self.setImage(image)

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], Qt.IgnoreAspectRatio)  # Show zoomed rect (ignore aspect ratio).
            sfull = max(self.sceneRect().width(), self.sceneRect().height())
            r = self.zoomStack[-1]
            ssub = max(r.width(), r.height())
            self.zoomFactor = sfull / ssub
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).
            self.zoomFactor = 1
        self.imageUpdated.emit()  # Signal that the image has been updated.

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.updateViewer()

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            if self.canPan:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MiddleButton:
            self.midMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    if self.fixedAspect:
                        # which is larger, width or height? Use the longest one, combined with the aspect ratio of the image
                        # to determine the new selectionBBox
                        if selectionBBox.height() > selectionBBox.width():
                            selectionBBox = QRectF(selectionBBox.x(), selectionBBox.y(),
                                                   selectionBBox.height() * self.aspect, selectionBBox.height())
                        else:
                            selectionBBox = QRectF(selectionBBox.x(), selectionBBox.y(), selectionBBox.width(),
                                                   selectionBBox.width() / self.aspect)
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
            self.setDragMode(QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MiddleButton:
            self.midMouseButtonReleased.emit(scenePos.x(), scenePos.y())

    def zoomBy(self, pos, factor):
        if len(self.zoomStack) == 0:
            self.zoomStack.append(self.sceneRect())
        viewBBox = self.zoomStack[-1]

        # TODO not sure how to get this to zoom in on pos rather than center.
        center = viewBBox.center()
        newWidth = viewBBox.width() * factor
        newHeight = viewBBox.height() * factor
        newBBox = QRectF(center.x() - newWidth / 2, center.y() - newHeight / 2, newWidth, newHeight)
        print("newbbox", newBBox)
        self.zoomStack.append(newBBox)
        self.updateViewer()

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mouseDoubleClickEvent(self, event)

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key_Backspace:
            if len(self.zoomStack) > 0:
                self.zoomStack = self.zoomStack[:-1]
                self.updateViewer()
            e.accept()
        super().keyPressEvent(e)

    def wheelEvent(self, e: QWheelEvent):
        super().wheelEvent(e)
        if e.angleDelta().y() > 0:
            self.zoomBy(e.pos(), 1 / self.wheelZoomFactor)
        else:
            self.zoomBy(e.pos(), self.wheelZoomFactor)
