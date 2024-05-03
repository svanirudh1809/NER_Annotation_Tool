# Main window
import sys
import os
import json
import random
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor

from resources.mainWindow import Ui_MainWindow
from resources.tagNameWidget import tagNameWidget
from resources.tagSetterWidget import tagSetterWidget


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Full window
        self.showMaximized()
        self.setWindowTitle("NER Annotator")
        self.modeSwitch.hide()  # BETA

        # Global variables
        self.rowTag, self.colTag = 0, 0
        # Original data
        self.jsonData = {}
        self.tags, self.text, self.ents = [], [], []
        # Data about to be saved
        self.tempData = {}
        self.tempTags, self.tempText, self.tempEnts = [], [], []
        self.iter = 0  # Position of text object
        self.colors = [(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)) for
                       _ in range(32)]  # Random colors
        self.selectionColor = None
        self.selectedTag = None

        # Reset everything
        self.reset()

        # Open JSON
        self.openJsonButton.clicked.connect(self.onOpenJson)

        # Save JSON
        self.saveJsonButton.clicked.connect(self.onSaveJson)

        # Go to next text object on clicking save / skip (Next)
        self.nextButton.clicked.connect(lambda x: self.onClickNext(key="next"))
        self.prevButton.clicked.connect(lambda x: self.onClickNext(key="prev"))

        # Add tag
        self.toolButton.clicked.connect(self.onAddTag)

        # Identify selection
        self.textSelector.mouseReleaseEvent = self.onSelection

        # Select / Deselect
        self.selectButton.clicked.connect(lambda x: self.toggleSelection(key="select"))
        self.deselectButton.clicked.connect(lambda x: self.toggleSelection(key="deselect"))
        self.selectButton.click()

        # Hide Select/Deselect buttons
        self.selectButton.hide()
        self.deselectButton.hide()

        # Get Index button
        self.getIndexButton.clicked.connect(self.getTextObject)

        # Remove Overlaps
        self.removeOverlapButton.clicked.connect(self.removeOverlaps)

        # Remove Duplicates
        self.removeDuplicatesButton.clicked.connect(self.removeDuplicates)

    def reset(self):
        self.rowTag, self.colTag = 0, 0
        self.iter = 0
        self.textSelector.clear()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.colors = [(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)) for
                       _ in range(32)]
        self.selectionColor = None
        self.selectedTag = None

        i = len(self.tempTags) - 1
        while i >= 0:
            tag = self.gridLayout_4.itemAt(i).widget()
            self.gridLayout_4.removeWidget(tag)
            tag.deleteLater()
            i -= 1

    def onOpenJson(self):
        """
        Open QFileDialog to get the JSON file
        :return: None
        """
        root = os.getcwd()
        fname = QtWidgets.QFileDialog.getOpenFileName(self,
                                                      "Open annotations JSON",
                                                      root,
                                                      ("JSON file (*.json)"))
        # Open the json file
        if fname[0]:
            with open(fname[0], "r") as fp:
                self.jsonData = json.load(fp)
            fp.close()

        # Load the file
        if self.jsonData:
            self.setWindowTitle(fname[0])  # Set window title as fname
            self.tags = self.jsonData["classes"]
            self.text = [text[0] for text in self.jsonData["annotations"]]
            self.ents = [ents[1]['entities'] for ents in self.jsonData["annotations"]]

            # Reset
            self.reset()

            # Get all temp references
            self.tempTags = self.tags.copy()
            self.tempText = self.text.copy()
            self.tempEnts = self.ents.copy()

            # Show all tags present
            for tag in self.tags:
                self.showTags((9, 187, 152), tag)
                self.colTag += 1
                if self.colTag > 4:
                    self.rowTag += 1
                    self.colTag = 0

            # Load first text
            self.progressBar.setMaximum(len(self.text))  # Set Maximum value
            self.loadText(self.text, self.ents, 0)

    def onSaveJson(self):
        """
        Open a QFileDialog to save the edited JSON
        :return: None
        """
        root = os.getcwd()
        fname = QtWidgets.QFileDialog.getSaveFileName(self,
                                                      "Save annotations as JSON",
                                                      root,
                                                      ("JSON file (*.json)"))

        # Save json data
        if fname[0]:
            with open(fname[0], "w") as fp:
                self.tempData["classes"] = self.tempTags
                self.tempData["annotations"] = [[self.tempText[i], {"entities": self.tempEnts[i]}] for i in
                                                range(len(self.tempText))]
                json.dump(self.tempData, fp, indent=0)
            fp.close()

    def onClickNext(self, key="prev"):
        if key == "prev":
            if 0 < self.iter <= len(self.text):
                self.iter -= 1  # Decrement value
                self.loadText(self.tempText, self.tempEnts, self.iter)

                # Uncheck everything
                self.uncheck()
        else:
            if self.iter < len(self.text) - 1:
                self.iter += 1  # Increment value
                self.loadText(self.tempText, self.tempEnts, self.iter)

                # Uncheck everything
                self.uncheck()

    def onAddTag(self):
        """
        Open a dialog box to choose name
        This adds on the UI and saves in JSON as well
        :return: None
        """
        # Show Dialog
        widget = tagSetterWidget()
        widget.show()
        result = widget.exec_()
        if result:
            name = widget.lineEdit.text()
            self.showTags((9, 187, 152), name)
            self.colTag += 1
            if self.colTag > 4:
                self.rowTag += 1
                self.colTag = 0
            self.tempTags.append(name)

    def onSelection(self, e):
        """
        Gives the tag on to the selected text and adds the label to that text
        :return: None
        """
        if self.selectButton.isChecked():
            # Set cursor selection
            cursor = self.textSelector.textCursor()
            selectionStart = cursor.selectionStart()
            selectionEnd = cursor.selectionEnd()
            self.highlighter(selectionStart, selectionEnd, self.selectionColor)

            # Add entity
            if selectionEnd > selectionStart:
                if self.selectedTag != None:
                    for i in self.tempEnts[self.iter]:
                        if i[0] <= selectionStart < selectionEnd <= i[1]:
                            self.highlighter(i[0], i[1], self.selectionColor)
                            self.tempEnts[self.iter].remove(i)
                            selectionStart, selectionEnd = i[0], i[1]
                            break
                    self.tempEnts[self.iter].append([selectionStart, selectionEnd, self.selectedTag])

                try:
                    pe = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress,
                                           QtCore.QPointF(self.textSelector.width(), self.textSelector.height()),
                                           QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
                    self.textSelector.mousePressEvent(pe)

                    re = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,
                                           QtCore.QPointF(self.textSelector.width(), self.textSelector.height()),
                                           QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
                    self.textSelector.mouseReleaseEvent(re)
                except Exception as e:
                    print(e)

        elif self.deselectButton.isChecked():
            # Set cursor selection
            cursor = self.textSelector.textCursor()
            selectionStart = cursor.selectionStart()
            selectionEnd = cursor.selectionEnd()

            # Delete entity
            if selectionEnd > selectionStart:
                for i in self.tempEnts[self.iter]:
                    if i[0] <= selectionStart < selectionEnd <= i[1]:
                        self.highlighter(i[0], i[1])
                        self.tempEnts[self.iter].remove(i)
                        break

            try:
                pe = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress,
                                       QtCore.QPointF(self.textSelector.width(), self.textSelector.height()),
                                       QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
                self.textSelector.mousePressEvent(pe)

                re = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,
                                       QtCore.QPointF(self.textSelector.width(), self.textSelector.height()),
                                       QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
                self.textSelector.mouseReleaseEvent(re)
            except Exception as e:
                print(e)

    def getTextObject(self):
        """
        Loads the given index value onto the textSelector
        :return:
        """
        self.iter = int(self.getIndex.text()) - 1
        self.loadText(self.tempText, self.tempEnts, self.iter)

    def removeOverlaps(self):
        """
        Corrections: Removes overlaps (if any)
        Only keeps the top label (i.e, the maximum area covered label)
        :return:
        """
        for k in range(len(self.tempText)):
            self.iter = k
            self.loadText(self.tempText, self.tempEnts, self.iter)
            for i in self.tempEnts[k]:
                for j in self.tempEnts[k]:
                    if (i != j) and (i[0] <= j[0] < j[1] <= i[1]):
                        self.tempEnts[k].remove(j)
                        print(k, j)

    def removeDuplicates(self):
        """
        Corrections: Removes the duplicate text fields
        :return:
        """
        seen = set()
        ind = 0
        for t in self.tempText:
            self.iter = ind
            self.loadText(self.tempText, self.tempEnts, self.iter)
            if t in seen:
                self.tempText.remove(t)
                self.tempEnts.pop(ind)
            else:
                seen.add(t)
            ind += 1
        self.progressBar.setMaximum(len(self.text))  # Set Maximum value

    def loadText(self, text, ents, i):
        """
        Secondary Function : Load the text on the text field
        :param text: list of texts extracted from the json file
        :param ents: dict of entities of each tag
        :param i: count of text
        :return: None
        """
        m = len(text)
        assert len(text) == len(ents)

        # Load text object
        self.textSelector.setText(text[i])

        # Label all entities
        for label in ents[i]:
            tag_ind = self.tempTags.index(label[2])
            tag = self.gridLayout_4.itemAt(tag_ind).widget()
            start = label[0]
            end = label[1]
            self.highlighter(start, end, tag.get_color())

        # Set progress bar value
        self.progressBar.setValue(i + 1)

    def showTags(self, color, name):
        """
        Secondary Function: shows tags present in the jsonData
        :param color: tuple -> rgb values
        :param name: string -> name
        :return: None
        """
        tag = tagNameWidget(self)
        tag.setObjectName(name)
        tag.set_color(self.colors.pop())
        tag.set_name(name)
        self.gridLayout_4.addWidget(tag, self.rowTag, self.colTag)

    def highlighter(self, selection_start, selection_end, color="transparent"):
        """
        Secondary Function : Color the selected text
        :param selection_start: starting index
        :param selection_end: ending index
        :param color: color of the tag
        :return: None
        """
        cursor = self.textSelector.textCursor()
        cursor.setPosition(selection_start)
        cursor.setPosition(selection_end, QTextCursor.KeepAnchor)
        fmt = QTextCharFormat()
        if isinstance(color, str):
            fmt.setBackground(QColor("transparent"))
        elif isinstance(color, tuple) or isinstance(color, list):
            if len(color) == 3:
                fmt.setBackground(
                    QColor(color[0], color[1], color[2])
                )
                fmt.setForeground(
                    QColor(24, 24, 24)
                )
        cursor.setCharFormat(fmt)

    def uncheck(self):
        """
        Secondary: Unchecks select, deselect, tags
        :return:
        """
        # self.selectButton.setChecked(False)
        self.deselectButton.setChecked(False)

        i = len(self.tempTags) - 1
        while i >= 0:
            tag = self.gridLayout_4.itemAt(i).widget()
            tag.tagName.setChecked(False)
            i -= 1
        selectorValue = "QTextEdit{selection-background-color: rgb(215, 255, 35);" \
                        "selection-color: rgb(24, 24, 24);" \
                        "background-color: rgb(22, 22, 23);" \
                        "border-radius: 10px;" \
                        "font: 14pt 'Comic Sans MS';" \
                        "color: rgb(246, 255, 61);" \
                        "padding: 15px;}"
        self.textSelector.setStyleSheet(selectorValue)

    def toggleSelection(self, key="select"):
        """
        If one gets selected -> other gets deselected
        :param key: select / deselect
        :return: None
        """
        if key == "select":
            if self.deselectButton.isChecked():
                self.deselectButton.setChecked(False)
        else:
            if self.selectButton.isChecked():
                self.selectButton.setChecked(False)
            else:
                self.selectButton.setChecked(True)

    def keyPressEvent(self, e):
        """
        Key Press event to listen if Ctrl is clicked -> Then click Deselect
        :param e:
        :return:
        """
        if e.key() == 16777249:
            self.deselectButton.click()

    def keyReleaseEvent(self, e):
        """
        Key press event to record key release event -> Click again to deselect
        :param e:
        :return:
        """
        if e.key() == 16777249:
            self.deselectButton.click()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
