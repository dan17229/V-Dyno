import json
from time import sleep

if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from VDyno.model.dyno import Dyno


class ExperimentWorker:
    def __init__(self, dyno: Dyno, steps: list) -> None:
        super().__init__()
        self.dyno = dyno
        self.steps = steps
        self.running = True

    def execute_step(self, motor, step: dict) -> None:
        """Execute a single step for a motor."""
        action = step["action"]
        if action == "ramp":
            self.ramp(
                motor, step["property"], step["start"], step["end"], step["duration"]
            )
        elif action == "hold":
            self.hold(motor, step["property"], step["value"], step["duration"])

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
            sleep(step_duration)

    def hold(self, motor, property: str, value: int, duration: float) -> None:
        """Hold the motor property at a specific value for the given duration."""
        if not self.running:
            return
        if property == "rpm":
            motor.set_rpm(value)
        elif property == "brake current":
            motor.set_brake_current(value)
        sleep(duration)

    def run(self) -> None:
        """Run the experiment steps."""
        print("Experiment started")
        for step in self.steps:
            print(f"Executing step: {step}")
            if not self.running:
                break
            motor = self.dyno.MUT if step["motor"] == "MUT" else self.dyno.load_motor
            self.execute_step(motor, step)


class TestAutomator:
    def __init__(self, dyno: Dyno) -> None:
        self.dyno = dyno

    def start_experiment(self, experiment_file: str) -> None:
        """Execute an experiment defined in a JSON file."""
        with open(experiment_file, "r") as file:
            experiment = json.load(file)

        steps = experiment["steps"]
        worker = ExperimentWorker(self.dyno, steps)
        worker.run()

    def _on_experiment_finished(self):
        """Handle experiment completion."""
        print("Experiment finished successfully.")

    def _on_experiment_error(self, error_message: str):
        """Handle experiment errors."""
        print(f"Experiment failed with error: {error_message}")


if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    dyno = Dyno()
    automator = TestAutomator(dyno)

    # Example: Execute an experiment from a JSON file
    automator.start_experiment("VDyno/experiments/experiment.json")
