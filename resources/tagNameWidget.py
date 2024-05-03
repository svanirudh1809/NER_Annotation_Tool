# Tag Name Widget (Custom widget)
import sys
from PyQt5 import QtCore, QtWidgets
from .tagNameWidgetUI import Ui_Form


class tagNameWidget(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.setupUi(self)
        # uic.loadUi("tagNameWidget.ui", self)

        # Show without borders
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # Remove on clicking button
        self.removeTag.clicked.connect(lambda x: self.close_())

        # Set selection color if checked
        self.tagName.clicked.connect(self.set_selection_color)

        self.color = None

    def set_color(self, color):
        """
        Sets background color and foreground color to the tag
        :param color: tuple -> rgb values
        :return: None
        """
        # Tag Color
        self.color = color
        tagValue = "QToolButton{background-color: rgb(" + \
                   str(color[0]) + ", " + str(color[1]) + ", " + str(color[2]) + \
                   ");" \
                   "font: 11pt 'Comic Sans MS';}" \
                   "QToolButton::Hover{" \
                   "background-color: rgb(" + \
                   str(color[0]) + ", " + str(color[1]) + ", " + str(color[2]) + ", " + str(200) + \
                   ");" \
                   "}" \
                   "QToolButton::Checked{" \
                   "background-color: rgb(" + \
                   str(color[0]) + ", " + str(color[1]) + ", " + str(color[2]) + ", " + str(200) + \
                   ");" \
                   "border-style: inset;" \
                   "}"
        self.tagName.setStyleSheet(tagValue)

    def get_color(self):
        """
        Gets the color associated with the object
        :return: rgb value
        """
        return self.color

    def set_name(self, name):
        """
        Sets name to the tag
        :param name: string -> name
        :return: None
        """
        self.tagName.setText(name)

    def get_name(self):
        """
        Gets the name of the tag
        :return: name of the tag
        """
        return self.tagName.text()

    def set_selection_color(self):
        if self.tagName.isChecked():

            # Uncheck other tags
            i = len(self.parent.tempTags) - 1
            while i >= 0:
                tag = self.parent.gridLayout_4.itemAt(i).widget()
                tag.tagName.setChecked(False)
                i -= 1

            # Check this tag
            self.tagName.setChecked(True)

            color = self.get_color()
            selectorValue = "QTextEdit{selection-background-color: rgb(" + \
                            str(color[0]) + ", " + str(color[1]) + ", " + str(color[2]) + \
                            ");" \
                            "selection-color: rgb(24, 24, 24);" \
                            "background-color: rgb(22, 22, 23);" \
                            "border-radius: 10px;" \
                            "font: 14pt 'Comic Sans MS';" \
                            "color: rgb(246, 255, 61);" \
                            "padding: 15px;}"
            self.parent.textSelector.setStyleSheet(selectorValue)
            self.parent.selectionColor = color
            self.parent.selectedTag = self.get_name()
        else:
            selectorValue = "QTextEdit{selection-background-color: rgb(215, 255, 35);" \
                            "selection-color: rgb(24, 24, 24);" \
                            "background-color: rgb(22, 22, 23);" \
                            "border-radius: 10px;" \
                            "font: 14pt 'Comic Sans MS';" \
                            "color: rgb(246, 255, 61);" \
                            "padding: 15px;}"
            self.parent.textSelector.setStyleSheet(selectorValue)
            self.parent.selectedTag = None

    def close_(self):
        """
        Extension of the close() function
        :return: None
        """
        self.parent.colTag -= 1  # Adjust the value of the parent column number
        self.parent.tempTags.remove(self.get_name())

        # Remove ents of all texts
        temp = []
        for ent in self.parent.tempEnts:
            temp.append([])
            for i in range(len(ent)):
                if ent[i][2] != self.get_name():
                    temp[-1].append(ent[i])
        self.parent.tempEnts = temp.copy()

        self.parent.gridLayout_4.removeWidget(self)
        self.deleteLater()


# Main
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = tagNameWidget()
    widget.show()
    app.exec()
