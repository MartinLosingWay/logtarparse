import sys
import os
import tarfile
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFileDialog, QTreeWidget, 
                            QTreeWidgetItem, QLabel, QMessageBox, QLineEdit,
                            QTextEdit, QSplitter)
from PyQt6.QtCore import Qt

class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Explorer with Tar.gz Support")
        self.setGeometry(100, 100, 1000, 800)
        
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
        
        # Search controls
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter keyword to search (e.g., 'time')")
        self.search_input.returnPressed.connect(self.search_contents)
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_contents)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Splitter for tree and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # File tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File Name", "Size", "Type"])
        self.tree.itemDoubleClicked.connect(self.handle_file_click)
        splitter.addWidget(self.tree)
        
        # Content display
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        self.content_label = QLabel("File Content")
        content_layout.addWidget(self.content_label)
        
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        content_layout.addWidget(self.content_display)
        
        splitter.addWidget(content_widget)
        layout.addWidget(splitter)
        
        # Memory usage label
        self.memory_label = QLabel("Memory Usage: 0 MB")
        layout.addWidget(self.memory_label)
        
        # Initialize variables
        self.current_directory = ""
        self.file_contents = {}
        self.total_memory_usage = 0
        self.current_search_results = []

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
        self.content_display.clear()
        self.current_search_results = []
        
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
                self.display_content(current_path, content)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error reading file: {str(e)}")

    def handle_tar_file(self, item):
        current_path = self.get_full_path(item)
        try:
            with tarfile.open(current_path, 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.isfile():
                        content = tar.extractfile(member).read()
                        file_path = f"{current_path}/{member.name}"
                        self.file_contents[file_path] = content
                        self.total_memory_usage += len(content)
                self.update_memory_label()
                self.display_content(current_path, None, is_tar=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error reading tar file: {str(e)}")

    def display_content(self, file_path, content=None, is_tar=False):
        if is_tar:
            self.content_label.setText(f"Tar.gz Archive: {os.path.basename(file_path)}")
            self.content_display.clear()
            for path, content in self.file_contents.items():
                if path.startswith(file_path):
                    self.content_display.append(f"\nFile: {os.path.basename(path)}")
                    self.content_display.append("-" * 50)
                    self.content_display.append(content.decode('utf-8', errors='ignore'))
        else:
            self.content_label.setText(f"File: {os.path.basename(file_path)}")
            self.content_display.clear()
            self.content_display.append(content.decode('utf-8', errors='ignore'))

    def search_contents(self):
        keyword = self.search_input.text().strip().lower()
        if not keyword:
            QMessageBox.warning(self, "Search", "Please enter a search keyword")
            return

        self.current_search_results = []
        self.content_display.clear()
        self.content_label.setText(f"Search Results for: '{keyword}'")
        
        for file_path, content in self.file_contents.items():
            try:
                text = content.decode('utf-8', errors='ignore')
                if keyword in text.lower():
                    self.current_search_results.append((file_path, text))
                    self.content_display.append(f"\nFile: {os.path.basename(file_path)}")
                    self.content_display.append("-" * 50)
                    
                    # Find and highlight all occurrences
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if keyword in line.lower():
                            self.content_display.append(f"Line {i+1}: {line}")
                    
                    self.content_display.append("\n")
            except Exception as e:
                continue

        if not self.current_search_results:
            self.content_display.append("No matches found.")

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