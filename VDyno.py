from VDyno.view.main_window import MainWindow
from VDyno.model.CAN_server import CANServer
from VDyno.view.data_handler import DataHandler

def main() -> None:
    model = CANServer()
    view = MainWindow()
    presenter = DataHandler(model, view)
    presenter.run()


if __name__ == "__main__":
    main()