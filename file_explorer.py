import sys
import os
import tarfile
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFileDialog, QTreeWidget, 
                            QTreeWidgetItem, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Explorer with Tar.gz Support")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Top controls
        controls_layout = QHBoxLayout()
        self.select_button = QPushButton("Select Directory")
        self.select_button.clicked.connect(self.select_directory)
        controls_layout.addWidget(self.select_button)
        
        self.status_label = QLabel("No directory selected")
        controls_layout.addWidget(self.status_label)
        layout.addLayout(controls_layout)
        
        # File tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File Name", "Size", "Type"])
        self.tree.itemDoubleClicked.connect(self.handle_file_click)
        layout.addWidget(self.tree)
        
        # Memory usage label
        self.memory_label = QLabel("Memory Usage: 0 MB")
        layout.addWidget(self.memory_label)
        
        # Initialize variables
        self.current_directory = ""
        self.file_contents = {}
        self.total_memory_usage = 0

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.current_directory = directory
            self.status_label.setText(f"Selected: {directory}")
            self.scan_directory(directory)

    def scan_directory(self, directory):
        self.tree.clear()
        self.file_contents.clear()
        self.total_memory_usage = 0
        
        root = QTreeWidgetItem(self.tree)
        root.setText(0, os.path.basename(directory))
        self.scan_directory_recursive(directory, root)
        self.tree.expandAll()
        self.update_memory_label()

    def scan_directory_recursive(self, directory, parent_item):
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    dir_item = QTreeWidgetItem(parent_item)
                    dir_item.setText(0, item)
                    dir_item.setText(2, "Directory")
                    self.scan_directory_recursive(full_path, dir_item)
                else:
                    file_item = QTreeWidgetItem(parent_item)
                    file_item.setText(0, item)
                    file_size = os.path.getsize(full_path)
                    file_item.setText(1, f"{file_size / 1024:.2f} KB")
                    
                    if item.endswith('.tar.gz'):
                        file_item.setText(2, "Tar.gz Archive")
                    else:
                        file_item.setText(2, "File")
        except PermissionError:
            QMessageBox.warning(self, "Permission Error", 
                              f"Permission denied while accessing {directory}")

    def handle_file_click(self, item, column):
        if item.text(2) == "Tar.gz Archive":
            self.handle_tar_file(item)
        else:
            self.handle_regular_file(item)

    def handle_regular_file(self, item):
        current_path = self.get_full_path(item)
        try:
            with open(current_path, 'rb') as f:
                content = f.read()
                self.file_contents[current_path] = content
                self.total_memory_usage += len(content)
                self.update_memory_label()
                QMessageBox.information(self, "File Content", 
                                      f"File content loaded into memory: {len(content)} bytes")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error reading file: {str(e)}")

    def handle_tar_file(self, item):
        current_path = self.get_full_path(item)
        try:
            with tarfile.open(current_path, 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.isfile():
                        content = tar.extractfile(member).read()
                        self.file_contents[f"{current_path}/{member.name}"] = content
                        self.total_memory_usage += len(content)
                self.update_memory_label()
                QMessageBox.information(self, "Tar Content", 
                                      "Tar.gz contents loaded into memory")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error reading tar file: {str(e)}")

    def get_full_path(self, item):
        path_parts = []
        while item is not None:
            path_parts.insert(0, item.text(0))
            item = item.parent()
        return os.path.join(self.current_directory, *path_parts[1:])

    def update_memory_label(self):
        memory_mb = self.total_memory_usage / (1024 * 1024)
        self.memory_label.setText(f"Memory Usage: {memory_mb:.2f} MB")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileExplorer()
    window.show()
    sys.exit(app.exec()) 