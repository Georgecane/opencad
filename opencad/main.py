#      /$$$$$$                                 /$$$$$$   /$$$$$$  /$$$$$$$
#     /$$__  $$                               /$$__  $$ /$$__  $$| $$__  $$
#    | $$  \ $$  /$$$$$$   /$$$$$$  /$$$$$$$ | $$  \__/| $$  \ $$| $$  \ $$
#    | $$  | $$ /$$__  $$ /$$__  $$| $$__  $$| $$      | $$$$$$$$| $$  | $$
#    | $$  | $$| $$  \ $$| $$$$$$$$| $$  \ $$| $$      | $$__  $$| $$  | $$
#    | $$  | $$| $$  | $$| $$_____/| $$  | $$| $$    $$| $$  | $$| $$  | $$
#    |  $$$$$$/| $$$$$$$/|  $$$$$$$| $$  | $$|  $$$$$$/| $$  | $$| $$$$$$$/
#     \______/ | $$____/  \_______/|__/  |__/ \______/ |__/  |__/|_______/
#              | $$
#              | $$
#              |__/

import logging
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from opencad.ui.main_window import MainWindow

def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    app = QApplication(sys.argv)
    app.setApplicationName("OpenCAD")
    app.setOrganizationName("OpenCAD")
    app.setStyle("Fusion")
    try:
        window = MainWindow()
    except Exception as exc:
        logging.exception("OpenCAD startup failed")
        QMessageBox.critical(None, "OpenCAD startup failed", str(exc))
        return 1
    window.show()
    return app.exec()
