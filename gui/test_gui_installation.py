# test_gui_installation.py
import sys
import platform
print(f"Python version: {sys.version}") 
print(f"Platform: {platform.system()}") 
print("=" * 50)


# Test 1: tkinter
try:
    import tkinter as tk
    print("✓ tkinter imported successfully")


# Test basic tkinter functionality
    root = tk.Tk()
    root.title("tkinter Test")
    root.geometry("300x100")
    tk.Label(root, text="tkinter is working!").pack(pady=20)


# Don't show the window in test, just destroy it
    root.update()
    root.destroy()
    print("✓ tkinter basic functionality works")
except ImportError as e:
    print(f"✗ tkinter import failed: {e}")
except Exception as e:
    print(f"✗ tkinter error: {e}")


# Test 2: PySide6
try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton 
    from PySide6.QtCore import Qt
    print("✓ PySide6 imported successfully")


# Test basic PySide6 functionality
    app = QApplication.instance() 
    if app is None:
        app = QApplication(sys.argv)
    window = QMainWindow() 
    window.setWindowTitle("PySide6 Test") 
    window.resize(300, 100)
    label = QLabel("PySide6 is working!", window) 
    label.setAlignment(Qt.AlignCenter) 
    window.setCentralWidget(label)
    print("✓ PySide6 basic functionality works")



# Clean up
    window.close()
    if hasattr(app, 'quit'):
        app.quit()
except ImportError as e:
    print(f"✗ PySide6 import failed: {e}")
except Exception as e:
    print(f"✗ PySide6 error: {e}")

print("\n🎉 GUI environment setup complete!")



