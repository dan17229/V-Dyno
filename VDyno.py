from VDyno.view.main_window import create_UI
#from VDyno.presenter.data_handler import Presenter
from VDyno.presenter.dummy_presenter import Presenter
#from VDyno.model.dyno import Dyno
from VDyno.model.dummy_dyno import Dyno


def main() -> None:
    model = Dyno()
    view = create_UI()
    presenter = Presenter(model, view)
    presenter.run()


if __name__ == "__main__":
    main()
