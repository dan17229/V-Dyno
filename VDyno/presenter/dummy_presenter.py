from random import randint

class Presenter():
    def __init__(self, dyno, view) -> None:
        self.data1 = 0
        self.data2 = 0
        self.data3 = 0
        self.dyno = dyno
        self.view = view
        self.MUT_key = "rpm"
        self.load_motor_key = "brake_current"
        self.transducer_key = "torque"

    @property
    def MUT_speed(self) -> int:
        self.data1 = self.data1 + randint(-10, 10)
        return self.data1

    @property
    def load_speed(self) -> int:
        self.data2 = self.data2 + randint(-10, 10)
        return self.data2

    @property
    def TT_value(self) -> int:
        self.data3 = self.data3 + randint(-10, 10)
        return self.data3

    def plot_MUT_changed(self, index: int) -> None:
        print(f"Selected MUT plot: {index}")
        self.data1 = 0

    def plot_load_changed(self, index: int) -> None:
        print(f"Selected load plot: {index}")
        self.data2 = 0

    def plot_TT_changed(self, index: int) -> None:
        print(f"Selected TT plot: {index}")
        self.data3 = 0

    def openCANBus(self) -> None:
        print("Opening CAN bus...")

    def closeCANBus(self) -> None:
        print("Closing CAN bus...")

    def command_MUT_rpm(self) -> None:
        self.dyno.MUT.set_rpm(self.view.get_rpm())

    def command_load_brake_current(self) -> None:
        self.dyno.load_motor.set_brake_current(self.view.get_brake_current())

    def update_MUT_plot(self) -> None:
        status = self.dyno.MUT.status
        value = status[self.MUT_key]
        self.view.update_MUT_plot(value)

    def update_load_motor_plot(self) -> None:
        status = self.dyno.load_motor.status
        value = status[self.load_motor_key]
        self.view.update_load_motor_plot(value)

    def update_transducer_plot(self) -> None:
        status = self.dyno.torque_transducer.status
        value = status[self.transducer_key]
        self.view.update_transducer_plot(value)

    def run(self) -> None:
        self.view.init_UI(self)
        self.update_status()