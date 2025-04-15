from VDyno.view.main_window import create_UI
from VDyno.presenter.data_handler import Presenter
from VDyno.model.dyno import Dyno


def main() -> None:
    view, app = create_UI()
    model = Dyno()
    presenter = Presenter(model, view, app)
    presenter.run()


if __name__ == "__main__":
    main()
