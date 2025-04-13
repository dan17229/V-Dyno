from VDyno.view.main_window import init_UI
from VDyno.presenter.data_handler import Presenter
from VDyno.model.model import Motor, TorqueTransducer
from VDyno.model.can_handler import CANHandler

def main() -> None:
    view = init_UI()
    try:
        server = CANHandler()
        MUT = Motor(server, 1)
        load_motor = Motor(server, 2)
        transducer = TorqueTransducer(server)
        presenter = Presenter(server, MUT, load_motor, transducer, view)
        presenter.run()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()