from PyQt5.QtCore import Qt, QStringListModel
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon, QKeySequence
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QShortcut, QMessageBox, QMainWindow, QSplitter, QAction, \
    qApp, QFileDialog, QHBoxLayout, QVBoxLayout, QDesktopWidget, QGridLayout, QWidget, QPushButton, QFrame, QCheckBox,\
    QTableWidget, QGroupBox, QTabWidget, QComboBox, QRadioButton, QListWidget, QListWidgetItem, QScrollBar, QTextEdit
import os, sys
from ImgViewer import ImageViewer


VALID_FORMAT = ('.BMP', '.GIF', '.JPG', '.JPEG', '.PNG', '.PBM', '.PGM', '.PPM', '.TIFF', '.XBM')  # Image formats supported by Qt


def getImages(folder):
    # Get the names and paths of all the images in a directory.
    image_list = []
    if os.path.isdir(folder):
        for file in os.listdir(folder):
            if file.upper().endswith(VALID_FORMAT):
                im_path = os.path.join(folder, file)
                image_obj = {'name': file, 'path': im_path }
                image_list.append(image_obj)
    return image_list


def resource_path(relative_path):
    if getattr(sys, 'frozen', False): #是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class QImageViewer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multiple Label Annotation Tool")
        self.resize(1200, 768)
        self.classes_txt_path = resource_path(os.path.join("icons", "classes.txt"))
        self.classes_txt = open(self.classes_txt_path, 'r')
        self.classes = self.classes_txt.readlines()

        # 窗口居中显示
        self.center()
        self.init_ui()
        self.image_viewer = ImageViewer(self.img_viewer)
        self.__connectEvents()

        self.current_save_folder = os.getcwd()

    def init_ui(self):

        self.img_number = 0

        # function button
        self.btn_open_pic = QPushButton("  Open Images")
        # self.btn_open_pic.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_open_pic.setEnabled(True)
        self.btn_open_pic.setIcon(QIcon(resource_path(os.path.join("icons", "images.png"))))
        self.btn_open_pic.setIconSize(QtCore.QSize(50, 50))
        self.btn_open_pic.setToolTip('Open one image.')

        self.btn_open_folder = QPushButton("  Open Folder")
        self.btn_open_folder.setEnabled(True)
        self.btn_open_folder.setIcon(QIcon(resource_path(os.path.join("icons", "folder.png"))))
        self.btn_open_folder.setIconSize(QtCore.QSize(50, 50))
        self.btn_open_folder.setShortcut('o')
        self.btn_open_folder.setToolTip('Open all the images in folder(O).')

        self.btn_previous = QPushButton("  Previous")
        self.btn_previous.setEnabled(True)
        self.btn_previous.setIcon(QIcon(resource_path(os.path.join("icons", "arrow-left.png"))))
        self.btn_previous.setIconSize(QtCore.QSize(50, 50))
        self.btn_previous.setShortcut('a')
        self.btn_previous.setToolTip('Open previous image (a).')

        self.btn_next = QPushButton("  Next")
        self.btn_next.setEnabled(True)
        self.btn_next.setIcon(QIcon(resource_path(os.path.join("icons", "arrow-right.png"))))
        self.btn_next.setIconSize(QtCore.QSize(50, 50))
        self.btn_next.setShortcut('d')
        self.btn_next.setToolTip('Open next image (d).')

        self.btn_save = QPushButton("  Save")
        self.btn_save.setEnabled(True)
        self.btn_save.setIcon(QIcon(resource_path(os.path.join("icons", "floppy.png"))))
        self.btn_save.setIconSize(QtCore.QSize(50, 50))
        self.btn_save.setShortcut('Ctrl+S')
        self.btn_save.setToolTip('Save label (Ctrl+S).')

        self.btn_change_save_folder = QPushButton("  Change Save folder")
        self.btn_change_save_folder.setEnabled(True)
        self.btn_change_save_folder.setIcon(QIcon(resource_path(os.path.join("icons", "folder-open.png"))))
        self.btn_change_save_folder.setIconSize(QtCore.QSize(50, 50))

        self.list_widget = QListWidget(self)

        # scroll bar
        scroll_bar_v = QScrollBar(self)
        scroll_bar_h = QScrollBar(self)

        # setting vertical scroll bar to it
        self.list_widget.setVerticalScrollBar(scroll_bar_v)
        self.list_widget.setVerticalScrollBar(scroll_bar_h)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.btn_open_pic)
        left_layout.addWidget(self.btn_open_folder)
        left_layout.addWidget(self.btn_previous)
        left_layout.addWidget(self.btn_next)
        left_layout.addWidget(self.btn_save)
        left_layout.addWidget(self.btn_change_save_folder)
        left_layout.addWidget(self.list_widget)

        left_layout.setStretch(0, 10)
        left_layout.setStretch(1, 10)
        left_layout.setStretch(2, 10)
        left_layout.setStretch(3, 10)
        left_layout.setStretch(4, 10)
        left_layout.setStretch(5, 10)
        left_layout.setStretch(6, 40)
        self.left_widget = QWidget()
        self.left_widget.setLayout(left_layout)

        self.right_widget = QTabWidget(self)
        # self.right_widget.tabBar().setObjectName("mainTab")
        right_layout = QHBoxLayout()
        right_layout.setSpacing(10)

        pix = QPixmap(resource_path(os.path.join("icons", "pfb4yyzdufx5jalgiyxx.jpg")))
        self.img_viewer = QLabel(self)
        self.img_viewer.setPixmap(pix)
        self.img_viewer.setScaledContents(True)
        self.img_viewer.setAlignment(Qt.AlignCenter)

        groupBox = QGroupBox('Pedestrian Attributes', self)

        check_items, combo_items = self.parse_class()
        # print(check_items, combo_items)

        self.checkboxes_classes = {}
        self.comboboxes_classes = {}
        self.comboboxes_labels = {}

        groupLayout = QVBoxLayout()
        i = 0
        for check_item in check_items:
            self.checkboxes_classes[check_item] = QCheckBox("   " + check_item)
            groupLayout.addWidget(self.checkboxes_classes[check_item], 2)
            # groupLayout.setStretch(i, 2)
            # i = i + 1

        for combo_item in combo_items:
            self.comboboxes_labels[combo_item] = QLabel(combo_item)
            self.comboboxes_classes[combo_item] = QComboBox()
            combo_classes = combo_items[combo_item].split(',')
            for cls in combo_classes:
                self.comboboxes_classes[combo_item].addItem(cls)
            groupLayout.addWidget(self.comboboxes_labels[combo_item], 2)
            # groupLayout.setStretch(i, 2)
            # i = i + 1
            groupLayout.addWidget(self.comboboxes_classes[combo_item], 2)
            # groupLayout.setStretch(i, 2)
            # i = i + 1

        groupLayout.setSpacing(5)

        groupBox.setLayout(groupLayout)

        right_layout.addWidget(self.img_viewer)
        right_layout.addWidget(groupBox)
        right_layout.setStretch(0, 70)
        right_layout.setStretch(1, 30)

        self.right_widget.setLayout(right_layout)

        main_layout = QHBoxLayout()
        vertical_splitter = QSplitter(Qt.Horizontal, frameShape=QFrame.StyledPanel,frameShadow=QFrame.Plain)

        vertical_splitter.addWidget(self.left_widget)
        # main_layout.addWidget(vertical_splitter)
        vertical_splitter.addWidget(self.right_widget)
        vertical_splitter.setSizes([100, 1100])
        main_layout.addWidget(vertical_splitter)
        # main_layout.setStretch(0, 15)

        # main_layout.setStretch(2, 80)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def __connectEvents(self):
        self.btn_open_folder.clicked.connect(self.selectDir)
        self.btn_open_pic.clicked.connect(self.selectImg)
        self.list_widget.itemClicked.connect(self.item_click)
        self.btn_next.clicked.connect(self.nextImg)
        self.btn_previous.clicked.connect(self.prevImg)
        self.btn_change_save_folder.clicked.connect(self.changeSaveFolder)
        self.btn_save.clicked.connect(self.saveLabel)

    def center(self):
        '''
        获取桌面长宽
        获取窗口长宽
        移动
        '''
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def changeSaveFolder(self):
        ''' Select a directory, make list of images in it and display the first image in the list. '''
        # open 'select folder' dialog box
        self.folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not self.folder:
            QtWidgets.QMessageBox.warning(self, 'No Folder Selected', 'Please select a valid Folder')
            return

        self.current_save_folder = self.folder

    def selectImg(self):
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "All Files(*)")

        self.image_viewer.loadImage(imgName)

    def selectDir(self):
        ''' Select a directory, make list of images in it and display the first image in the list. '''
        # open 'select folder' dialog box
        self.folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not self.folder:
            QtWidgets.QMessageBox.warning(self, 'No Folder Selected', 'Please select a valid Folder')
            return

        self.current_save_folder = self.folder

        self.images = {}
        self.images = getImages(self.folder)
        self.img_number = len(self.images)

        self.items = []
        self.list_widget.clear()
        self.items = [QtWidgets.QListWidgetItem(log['path']) for log in self.images]
        for item in self.items:
            self.list_widget.addItem(item)

        # load first image
        self.cntr = 0
        if self.img_number > 0:
            self.image_viewer.loadImage(self.images[self.cntr]['path'])
            self.items[self.cntr].setSelected(True)

            img_path = self.images[self.cntr]['path']
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            out_path = os.path.join(self.current_save_folder, base_name + '.txt')
            if os.path.exists(out_path):
                self.set_anno_label(out_path)
            else:
                self.anno_clear()
        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'No more Images!')

    def item_click(self, item):
        self.cntr = self.items.index(item)
        self.image_viewer.loadImage(self.images[self.cntr]['path'])

        img_path = self.images[self.cntr]['path']
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        out_path = os.path.join(self.current_save_folder, base_name + '.txt')
        if os.path.exists(out_path):
            self.set_anno_label(out_path)
        else:
            self.anno_clear()

    def set_anno_label(self, path):

        if os.path.exists(path):
            f_label = open(path, 'r')
            label_dict = eval(f_label.read())
            for label in label_dict:
                if label in self.checkboxes_classes:
                    label_anno = label_dict[label]
                    if label_anno == 'True':
                        self.checkboxes_classes[label].setChecked(True)
                    else:
                        self.checkboxes_classes[label].setChecked(False)
                elif label in self.comboboxes_classes:
                    label_anno = label_dict[label]
                    self.comboboxes_classes[label].setCurrentText(label_anno)

    def anno_clear(self):
        for label in self.checkboxes_classes:
            self.checkboxes_classes[label].setChecked(False)
        for label in self.comboboxes_classes:
            self.comboboxes_classes[label].setCurrentIndex(0)

    def nextImg(self):
        if self.img_number > 0:
            if self.cntr < self.img_number - 1:
                self.cntr += 1
                self.image_viewer.loadImage(self.images[self.cntr]['path'])
                self.items[self.cntr].setSelected(True)

                img_path = self.images[self.cntr]['path']
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                out_path = os.path.join(self.current_save_folder, base_name + '.txt')
                if os.path.exists(out_path):
                    self.set_anno_label(out_path)
                else:
                    self.anno_clear()
            else:
                QtWidgets.QMessageBox.warning(self, 'Sorry', 'No more Images!')
        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'No more Images!')

    def prevImg(self):
        if self.img_number > 0:
            if self.cntr > 0:
                self.cntr -= 1
                self.image_viewer.loadImage(self.images[self.cntr]['path'])
                self.items[self.cntr].setSelected(True)

                img_path = self.images[self.cntr]['path']
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                out_path = os.path.join(self.current_save_folder, base_name + '.txt')
                if os.path.exists(out_path):
                    self.set_anno_label(out_path)
                else:
                    self.anno_clear()
            else:
                QtWidgets.QMessageBox.warning(self, 'Sorry', 'No previous Image!')
        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'No previous Image!')

    def saveLabel(self):
        if self.img_number > 0:
            img_path = self.images[self.cntr]['path']
            label_to_save = self.get_label()

            base_name = os.path.splitext(os.path.basename(img_path))[0]
            out_path = os.path.join(self.current_save_folder, base_name + '.txt')
            fout = open(out_path, 'w')
            fout.write(str(label_to_save))
            fout.close()
        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'No Images to save!')

    def parse_class(self):

        # print(self.classes)
        checkbox_list = {}
        combobox_list = {}

        for line in self.classes:
            if line is not None:
                label = line.split(':')[0]
                classes = line.split(':')[1]
                if len(classes.split(',')) == 2:
                    checkbox_list[label] = classes
                elif len(classes.split(',')) > 2:
                    combobox_list[label] = classes

        return checkbox_list, combobox_list

    def get_label(self):
        labels = {}
        if self.img_number > 1:

            for item in self.checkboxes_classes:
                if self.checkboxes_classes[item].isChecked():
                    is_checked = True
                else:
                    is_checked = False

                label = list(map(str, [item, is_checked]))
                labels[item] = str(is_checked)
                # print(label)
            for item in self.comboboxes_classes:
                classname = self.comboboxes_classes[item].currentText()
                label = list(map(str, [item, classname]))
                # labels.append(label)
                labels[item] = str(classname)
                # print(label)

        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'No more Images!')

        return labels


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建启动界面，支持png透明图片
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap(resource_path(os.path.join("icons", "splash.png"))))
    splash.show()
    splash.setFont(QtGui.QFont("microsoft yahei", 15))
    # 可以显示启动信息
    splash.showMessage('正在加载...', Qt.AlignCenter|Qt.AlignBottom, Qt.black)
    # 关闭启动画面
    splash.close()

    app.setStyle('Fusion')
    imageViewer = QImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())