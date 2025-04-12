import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QListWidget, QLabel,
    QPushButton, QHBoxLayout, QVBoxLayout, QSplitter,
    QLineEdit, QFileDialog, QMessageBox, QSizePolicy,QCheckBox,QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

list_scale = 1
image_scale = 4
class ImageViewer(QWidget):
    """
    Dual-panel image viewer that supports displaying different images 
    in left and right panels simultaneously, with features including 
    image lists and slideshow functionality.
    """
    def __init__(self):
        super().__init__()
        # Image file path lists for both panels
        self.image_files_left = []
        self.image_files_right = []
        # Current image directories for both panels
        self.current_dir_left = ""
        self.current_dir_right = ""
        # Current image indices for both panels
        self.current_image_left_index = 0
        self.current_image_right_index = 0

        # Slideshow timer
        self.slideshow_timer = QTimer()
        self.slideshow_active = False
        self.setup_ui()

    def setup_ui(self):
        # Main horizontal layout [a, b]

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Top control panel
        top_widget = QWidget()
        top_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.top_controls = QHBoxLayout(top_widget)

        # Path input field
        self.show_list_checkbox = QCheckBox("Show Lists")
        self.show_list_checkbox.setChecked(True)
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter image folder path")
        self.load_left_button = QPushButton("Load Left")
        self.load_right_button = QPushButton("Load Right")
        self.next_image_button = QPushButton("Next")
        self.slideshow_button = QPushButton("Start Slideshow")
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Dual View", "Left View", "Right View"])
        self.interval_input = QLineEdit("1000")
        self.interval_input.setPlaceholderText("Interval (ms)")
        self.interval_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.interval_input.setFixedWidth(80)

        self.top_controls.addWidget(self.path_input, 2)
        self.top_controls.addWidget(self.show_list_checkbox)
        self.top_controls.addWidget(self.load_left_button)
        self.top_controls.addWidget(self.load_right_button)
        self.top_controls.addWidget(self.next_image_button)
        self.top_controls.addWidget(self.slideshow_button)
        self.top_controls.addWidget(self.interval_input)
        self.top_controls.addWidget(self.view_mode_combo)
        main_layout.addLayout(self.top_controls, 1) 
    
        bottom_widget = QWidget()
        bottom_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bottom_controls = QHBoxLayout(bottom_widget)
        self.list_panel = QVBoxLayout()
        self.left_list = QListWidget()
        self.right_list = QListWidget()
        self.list_panel.addWidget(self.left_list, 1)  # a1
        self.list_panel.addWidget(self.right_list, 1) # a2
        self.bottom_controls.addLayout(self.list_panel, 0.2)
    
        self.left_image_label = QLabel("SELECT LEFT IMAGE")
        self.left_image_label.setStyleSheet("border: 2px solid #005387; background: white;")
        self.left_image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.right_image_label = QLabel("SELECT RIGHT IMAGE")
        self.right_image_label.setStyleSheet("border: 2px solid #005387; background: white;")
        self.right_image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.left_image_label.setAlignment(Qt.AlignCenter)
        
        self.right_image_label.setAlignment(Qt.AlignCenter)
        self.bottom_controls.addWidget(self.left_image_label, 1) 
        self.bottom_controls.addWidget(self.right_image_label, 1)
        self.bottom_controls.setStretch(0, list_scale)
        self.bottom_controls.setStretch(1, image_scale)
        self.bottom_controls.setStretch(2, image_scale)
     
        main_layout.addWidget(top_widget)  
        main_layout.addWidget(bottom_widget) 
        main_layout.setStretch(0, 1) 
        main_layout.setStretch(1, 4)

        self.connectsignals()

        self.setWindowTitle("Packing Result Preview")
        self.resize(1200, 800)
        self.setStyleSheet("""
            QWidget { 
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton { 
                background: #005387;
                color: white; 
                padding: 8px 12px;
                border-radius: 4px;
                min-width: 90px;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QListWidget {
                background: #f5f5f5;
                border: 1px solid #ddd;
            }
        """)

    def connectsignals(self):
        self.show_list_checkbox.clicked.connect(self.update_ui_visibility)

        self.view_mode_combo.currentTextChanged.connect(self.update_ui_visibility)

        self.next_image_button.clicked.connect(self.show_next_image)

        self.load_left_button.clicked.connect(lambda: self.load_images("left"))
        self.load_right_button.clicked.connect(lambda: self.load_images("right"))
        
        
        self.slideshow_button.clicked.connect(self.toggle_slideshow)
        self.slideshow_timer.timeout.connect(self.show_next_image)

        self.left_list.currentRowChanged.connect(lambda: self.on_list_selected("left"))
        self.right_list.currentRowChanged.connect(lambda: self.on_list_selected("right"))

    def on_list_selected(self, side):
        if side == "left":
            self.current_image_left_index = self.left_list.currentRow()
        else:
            self.current_image_right_index = self.right_list.currentRow()
        self.update_display(side)  

    def update_ui_visibility(self):
        show_lists = self.show_list_checkbox.isChecked()
        current_mode = self.view_mode_combo.currentText()

        self.bottom_controls.setStretch(0, 0)
        self.bottom_controls.setStretch(1, 0)
        self.bottom_controls.setStretch(2, 0)

        if show_lists:
            self.bottom_controls.setStretch(0, list_scale)
            if current_mode == "Dual View":
                self.bottom_controls.setStretch(1, image_scale)
                self.bottom_controls.setStretch(2, image_scale)
                self.left_image_label.show()
                self.right_image_label.show()
            else:
                if current_mode == "Left View":
                    self.bottom_controls.setStretch(1, image_scale*2)
                    self.bottom_controls.setStretch(2, 0)
                    self.left_image_label.show()
                    self.right_image_label.hide()
                else:  # Right View
                    self.bottom_controls.setStretch(1, 0)
                    self.bottom_controls.setStretch(2, image_scale*2)
                    self.left_image_label.hide()
                    self.right_image_label.show()
        else:
            self.bottom_controls.setStretch(0, 0)
            if current_mode == "Dual View":
                self.bottom_controls.setStretch(1, image_scale)
                self.bottom_controls.setStretch(2, image_scale)
                self.left_image_label.show()
                self.right_image_label.show()
            else:
                if current_mode == "Left View":
                    self.bottom_controls.setStretch(1, image_scale*2)
                    self.bottom_controls.setStretch(2, 0)
                    self.left_image_label.show()
                    self.right_image_label.hide()
                else:  # Right View
                    self.bottom_controls.setStretch(1, 0)
                    self.bottom_controls.setStretch(2, image_scale*2)
                    self.left_image_label.hide()
                    self.right_image_label.show()
                    
        self.left_list.setVisible(show_lists and current_mode in ["Dual View", "Left View"])
        self.right_list.setVisible(show_lists and current_mode in ["Dual View", "Right View"])

        self.load_left_button.setVisible(current_mode in ["Dual View", "Left View"])
        self.load_right_button.setVisible(current_mode in ["Dual View", "Right View"])

        self.updateGeometry()
        self.update()
        

    def show_next_image(self):
        if self.image_files_left:
            self.current_image_left_index = (self.current_image_left_index + 1) % len(self.image_files_left)
            self.left_list.setCurrentRow(self.current_image_left_index)
            self.update_display("left")
            
        if self.image_files_right:
            self.current_image_right_index = (self.current_image_right_index + 1) % len(self.image_files_right)
            self.right_list.setCurrentRow(self.current_image_right_index)
            if self.image_files_right == self.image_files_left:
                self.current_image_right_index = self.current_image_left_index
            self.update_display("right")
                
            
    
    def display_selected_image(self):
        if self.left_list.count() > 0:
            self.current_image_left_index = self.left_list.currentRow()
            self.update_display(self.image_files_left)

        if self.right_list.count() > 0:
            self.current_image_right_index = self.right_list.currentRow()
            self.update_display(self.image_files_right)


    def update_display(self, side):
        try:
            if side == "left":
                target_label = self.left_image_label
                current_index = self.current_image_left_index
                image_list = self.image_files_left
            else:
                target_label = self.right_image_label
                current_index = self.current_image_right_index
                image_list = self.image_files_right

            if not image_list:
                return
                
            current_image_path = image_list[current_index]

            if not os.path.exists(current_image_path):
                target_label.setText("picture is not exists") 
                return
                
            pixmap = QPixmap(current_image_path)
            if pixmap.isNull():
                target_label.setText("cant load image")
                return
                
            original_size = target_label.size()
            scaled_pixmap = pixmap.scaled(
                original_size,  
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            target_label.setFixedSize(original_size)
            target_label.setPixmap(scaled_pixmap)
            target_label.setAlignment(Qt.AlignCenter)
            
            if side == "left":
                self.left_list.setCurrentRow(current_index)
            else:
                self.right_list.setCurrentRow(current_index)

            self.update_window_title(current_image_path)
            
        except Exception as e:
            error_msg = f"display pic error:{str(e)}"
            QMessageBox.critical(self, "error", error_msg)
            target_label.setText("display pic error")
            
    def update_window_title(self, image_path):
        try:
            filename = os.path.basename(image_path)
            filesize = os.path.getsize(image_path) / 1024  # KB
            pixmap = QPixmap(image_path)
            dimensions = f"{pixmap.width()}x{pixmap.height()}"
            
            title = f"Packing Result Preview - {filename} ({dimensions}, {filesize:.1f}KB)"
            self.setWindowTitle(title)
        except:
            self.setWindowTitle("Packing Result Preview")

    def load_images(self, side="left"):
        """Load images into specified panel"""
        path = self.path_input.text().strip()
        if not path:
            path = self.get_default_directory()
            
        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", "Path does not exist!")
            return
            
        try:
            # Supported image formats
            image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
            
            if os.path.isdir(path):
                # Get all supported image files
                image_files = []
                for filename in os.listdir(path):
                    if filename.lower().endswith(image_extensions):
                        full_path = os.path.join(path, filename)
                        image_files.append(full_path)
                
                if not image_files:
                    QMessageBox.warning(self, "Warning", "No supported image files found!")
                    return
                    
                # Sort by filename
                image_files.sort(key=lambda x: os.path.basename(x).lower())
                
            elif os.path.isfile(path):
                if not path.lower().endswith(image_extensions):
                    QMessageBox.warning(self, "Error", "Unsupported file format!")
                    return
                image_files = [path]
            else:
                QMessageBox.warning(self, "Error", "Invalid path!")
                return

            # Update panel data and UI
            target_list = self.left_list if side == "left" else self.right_list
            
            if side == "left":
                self.image_files_left = image_files
                self.current_dir_left = os.path.dirname(image_files[0])
                self.current_image_left_index = 0

            if side == "right":
                self.image_files_right = image_files
                self.current_dir_right = os.path.dirname(image_files[0])
                self.current_image_right_index = 0
            
            # Update list display
            target_list.clear()
            for img_path in image_files:
                target_list.addItem(os.path.basename(img_path))
            
            target_list.setCurrentRow(0)
            self.update_display(side)
            
        except Exception as e:
            QMessageBox.critical(self, "error", f"load pic file：{str(e)}")
        

    def get_default_directory(self):
        default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "png")
        
        if not os.path.exists(default_dir):
            try:
                os.makedirs(default_dir)
            except Exception as e:
                QMessageBox.warning(self, "warning", f"mkdir failed：{str(e)}")
                return ""
        
        return default_dir


    def toggle_slideshow(self):
        if not self.slideshow_active:
            try:
                interval = int(self.interval_input.text())
                if interval < 100:  # 设置最小间隔为100ms
                    interval = 100
                    self.interval_input.setText("100")
                self.slideshow_timer.start(interval)
                self.slideshow_active = True
                self.slideshow_button.setText("stop")
            except ValueError:
                QMessageBox.warning(self, "warning", "inter>=100")
                self.interval_input.setText("1000")
        else:
            self.slideshow_timer.stop()
            self.slideshow_active = False
            self.slideshow_button.setText("start")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()

    sys.exit(app.exec_())