import json
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
        import os
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from VDyno.model.dyno import Dyno

class ExperimentWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, dyno: Dyno, steps: list) -> None:
        super().__init__()
        self.dyno = dyno
        self.steps = steps
        self.running = True

    def execute_step(self, motor, step: dict) -> None:
        """Execute a single step for a motor."""
        action = step["action"]
        try:
            if action == "ramp":
                self.ramp(motor, step["property"], step["start"], step["end"], step["duration"])
            elif action == "hold":
                self.hold(motor, step["property"], step["value"], step["duration"])
        except Exception as e:
            self.error.emit(str(e))

    def ramp(self, motor, property: str, start: int, end: int, duration: float) -> None:
        """Ramp the motor property from start to end over the given duration."""
        steps = 100
        step_duration = duration / steps
        step_size = (end - start) / steps  # Calculate the step size as a float

        current_value = start
        for _ in range(steps):
            if not self.running:
                return
            if property == "rpm":
                motor.set_rpm(int(current_value))
            elif property == "brake current":
                motor.set_brake_current(int(current_value))
            current_value += step_size
            QThread.msleep(int(step_duration * 1000))  # Convert to milliseconds

    def hold(self, motor, property: str, value: int, duration: float) -> None:
        """Hold the motor property at a specific value for the given duration."""
        if not self.running:
            return
        if property == "rpm":
            motor.set_rpm(value)
        elif property == "brake current":
            motor.set_brake_current(value)
        QThread.msleep(int(duration * 1000))  # Convert to milliseconds

    def run(self) -> None:
        """Run the experiment steps."""
        print("Experiment started")
        try:
            for step in self.steps:
                print(f"Executing step: {step}")
                if not self.running:
                    break
                motor = self.dyno.MUT if step["motor"] == "MUT" else self.dyno.load_motor
                self.execute_step(motor, step)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class TestAutomator:
    def __init__(self, dyno: Dyno) -> None:
        self.dyno = dyno

    def setup_thread(self, steps: dict) -> None:
        """Setup the thread for running the experiment."""
        self._thread = QThread()
        self.worker = ExperimentWorker(self.dyno, steps)
        self.worker.moveToThread(self._thread)
        self._thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_experiment_finished)
        self.worker.error.connect(self._on_experiment_error)
        QApplication.instance().aboutToQuit.connect(self._thread.quit)

    def start_experiment(self, experiment_file: str) -> None:
        """Execute an experiment defined in a JSON file."""
        with open(experiment_file, 'r') as file:
            experiment = json.load(file)

        steps = experiment["steps"]
        self.setup_thread(steps)
        # Run the worker in a separate thread
        self._thread.start()

    def _on_experiment_finished(self):
        """Handle experiment completion."""
        print("Experiment finished successfully.")
        QApplication.instance().quit()

    def _on_experiment_error(self, error_message: str):
        """Handle experiment errors."""
        print(f"Experiment failed with error: {error_message}")


if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    dyno = Dyno()
    dummy_application = QApplication([])  # Dummy QApplication for testing 
    automator = TestAutomator(dyno)

    # Example: Execute an experiment from a JSON file
    automator.start_experiment("VDyno/experiments/experiment.json")
    dummy_application.exec()  # Start the event loop for testing