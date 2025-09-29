import sys
import struct
import zipfile
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QListWidget, QMessageBox, QFrame
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

class ArcZipConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dotarc - LCETools")
        self.setGeometry(100, 100, 850, 450)

        self.zip_file_path = None
        self.arc_file_path = None
        self.arc_file_data = None
        self.arc_entries = []

        self.init_ui()

    def init_ui(self):
        # --- Main widget and layout ---
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        self.setCentralWidget(main_widget)

        # --- ZIP to ARC Panel ---
        zip_to_arc_frame = self.create_ui_frame()
        zip_to_arc_layout = QVBoxLayout(zip_to_arc_frame)
        
        title1 = QLabel("ZIP → ARC")
        title1.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        zip_to_arc_layout.addWidget(title1, 0, Qt.AlignmentFlag.AlignHCenter)

        self.btn_select_zip = QPushButton("Select ZIP file...")
        self.btn_select_zip.clicked.connect(self.select_zip_file)
        zip_to_arc_layout.addWidget(self.btn_select_zip)

        self.lbl_zip_path = QLabel("No file seleted...")
        self.lbl_zip_path.setWordWrap(True)
        self.lbl_zip_path.setStyleSheet("color: #555;")
        zip_to_arc_layout.addWidget(self.lbl_zip_path)

        self.btn_convert_to_arc = QPushButton("Convert to ARC")
        self.btn_convert_to_arc.clicked.connect(self.convert_zip_to_arc)
        self.btn_convert_to_arc.setEnabled(False)
        self.btn_convert_to_arc.setStyleSheet("background-color: #2a9d8f; color: white; padding: 5px;")
        zip_to_arc_layout.addWidget(self.btn_convert_to_arc)
        zip_to_arc_layout.addStretch()

        # --- ARC to ZIP Panel ---
        arc_to_zip_frame = self.create_ui_frame()
        arc_to_zip_layout = QVBoxLayout(arc_to_zip_frame)

        title2 = QLabel("ARC → ZIP")
        title2.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        arc_to_zip_layout.addWidget(title2, 0, Qt.AlignmentFlag.AlignHCenter)
        
        self.btn_select_arc = QPushButton("Select ARC file...")
        self.btn_select_arc.clicked.connect(self.select_arc_file)
        arc_to_zip_layout.addWidget(self.btn_select_arc)

        self.lbl_arc_path = QLabel("No file selected...")
        self.lbl_arc_path.setWordWrap(True)
        self.lbl_arc_path.setStyleSheet("color: #555;")
        arc_to_zip_layout.addWidget(self.lbl_arc_path)
        
        arc_to_zip_layout.addWidget(QLabel("Archive Content:"))
        self.list_arc_contents = QListWidget()
        arc_to_zip_layout.addWidget(self.list_arc_contents)

        self.btn_convert_to_zip = QPushButton("Conver to ZIP")
        self.btn_convert_to_zip.clicked.connect(self.convert_arc_to_zip)
        self.btn_convert_to_zip.setEnabled(False)
        self.btn_convert_to_zip.setStyleSheet("background-color: #2a9d8f; color: white; padding: 5px;")
        arc_to_zip_layout.addWidget(self.btn_convert_to_zip)
        
        # --- Add panels to main layout ---
        main_layout.addWidget(zip_to_arc_frame)
        main_layout.addWidget(arc_to_zip_frame)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QPushButton { padding: 5px; border-radius: 4px; border: 1px solid #ccc; background-color: #e0e0e0; }
            QPushButton:hover { background-color: #d0d0d0; }
            QLabel { font-size: 10pt; }
            QListWidget { border: 1px solid #ccc; border-radius: 4px; }
        """)

    def create_ui_frame(self):
        """Helper function to create a styled QFrame."""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        frame.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
        return frame

    # --- ZIP to ARC Methods ---
    def select_zip_file(self):
        """Opens a file dialog to select a ZIP file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select ZIP file", "", "ZIP Files (*.zip)")
        if file_path:
            self.zip_file_path = file_path
            self.lbl_zip_path.setText(f"Selected: {file_path}")
            self.btn_convert_to_arc.setEnabled(True)

    def convert_zip_to_arc(self):
        """Handles the logic for converting the selected ZIP file to ARC format."""
        if not self.zip_file_path:
            QMessageBox.warning(self, "ERROR", "First you need to select ZIP archive!.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save ARC file", "", "Minecraft Archive Files (*.arc)")
        if not save_path:
            return
            
        try:
            with zipfile.ZipFile(self.zip_file_path, "r") as arc_zip_file:
                filelist = [info for info in arc_zip_file.infolist() if not info.is_dir()]
                entry_count = len(filelist)
                
                header_size = 4 + sum(2 + len(info.filename.replace("/", "\\").encode("utf-8")) + 8 for info in filelist)
                
                write_buffer = bytearray(struct.pack(">i", entry_count))
                
                temp_file_offset = header_size
                for zipInfo in filelist:
                    filename_bytes = zipInfo.filename.replace("/", "\\").encode("utf-8")
                    strlen = len(filename_bytes)
                    header_entry = struct.pack(f">h{strlen}sii", strlen, filename_bytes, temp_file_offset, zipInfo.file_size)
                    write_buffer.extend(header_entry)
                    temp_file_offset += zipInfo.file_size
                
                for zipInfo in filelist:
                    write_buffer.extend(arc_zip_file.read(zipInfo.filename))

                with open(save_path, "wb") as arc_file:
                    arc_file.write(write_buffer)
            
            QMessageBox.information(self, "Success!", f"file saved to - {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Convert Error", f"Error occured: {e}")

    # --- ARC to ZIP Methods ---
    def select_arc_file(self):
        """Opens a file dialog to select an ARC file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select ARC file", "", "Minecraft Archive (*.arc)")
        if file_path:
            self.arc_file_path = file_path
            self.lbl_arc_path.setText(f"Selected: {file_path}")
            self.read_arc_and_display()

    def read_arc_and_display(self):
        """Reads the selected ARC file, parses its header, and displays contents in a list."""
        self.list_arc_contents.clear()
        self.arc_entries.clear()
        self.btn_convert_to_zip.setEnabled(False)
        try:
            with open(self.arc_file_path, "rb") as archive:
                self.arc_file_data = archive.read()
            
            entry_count = struct.unpack(">i", self.arc_file_data[:4])[0]
            offset = 4
            
            for _ in range(entry_count):
                strlen = struct.unpack_from(">h", self.arc_file_data, offset=offset)[0]
                offset += 2
                
                path_bytes, file_offset, file_size = struct.unpack_from(f">{strlen}sii", self.arc_file_data, offset=offset)
                filepath = path_bytes.decode("utf-8")
                offset += strlen + 8
                
                self.arc_entries.append({'path': filepath, 'offset': file_offset, 'size': file_size})
                self.list_arc_contents.addItem(f"{filepath} ({file_size} байт)")

            if self.arc_entries:
                self.btn_convert_to_zip.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "error while reading file", f"failed to read ARC file: {e}")
            self.arc_file_data = None

    def convert_arc_to_zip(self):
        """Handles the logic for converting the loaded ARC data back to a ZIP file."""
        if not self.arc_entries or not self.arc_file_data:
            QMessageBox.warning(self, "ERROR", "No data for convertation.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save to ZIP file", "", "ZIP Files (*.zip)")
        if not save_path:
            return

        try:
            with zipfile.ZipFile(save_path, "w", compression=zipfile.ZIP_DEFLATED) as arc_zip_file:
                for entry in self.arc_entries:
                    file_data = self.arc_file_data[entry['offset'] : entry['offset'] + entry['size']]
                    arc_zip_file.writestr(entry['path'], file_data)
            QMessageBox.information(self, "Success!", f"Archive saved to: {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Convertation Error", f"Error occured: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter = ArcZipConverter()
    converter.show()
    sys.exit(app.exec())
