import json
from time import sleep
from typing import Protocol

if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

class MainWindow(Protocol):...
class ExperimentWorker:
    def __init__(self, parent: MainWindow, steps: list) -> None:
        super().__init__()
        self.parent = parent
        self.steps = steps
        self.running = True

    def execute_step(self, step: dict) -> None:
        """Execute a single step for both motors."""
        action = step["action"]
        if action == "ramp":
            self.ramp(
                step["MUT"]["property"],
                step["MUT"]["start"],
                step["MUT"]["end"],
                step["load_motor"]["property"],
                step["load_motor"]["start"],
                step["load_motor"]["end"],
                step["duration"],
            )
        elif action == "hold":
            self.hold(
                step["MUT"]["property"],
                step["MUT"]["value"],
                step["load_motor"]["property"],
                step["load_motor"]["value"],
                step["duration"],
            )

    def ramp(
        self,
        mut_property: str,
        mut_start: int,
        mut_end: int,
        load_property: str,
        load_start: int,
        load_end: int,
        duration: float,
    ) -> None:
        """Ramp both motors' properties simultaneously."""
        steps = 100
        step_duration = duration / steps
        mut_step_size = (mut_end - mut_start) / steps
        load_step_size = (load_end - load_start) / steps

        mut_current_value = mut_start
        load_current_value = load_start
        for _ in range(steps):
            if not self.running:
                return
            if mut_property == "current":
                self.parent.change_MUT_current(float(mut_current_value))  # Send MUT current demand
            if load_property == "rpm":
                self.parent.change_load_rpm(int(load_current_value))  # Send load motor RPM demand
            mut_current_value += mut_step_size
            load_current_value += load_step_size
            sleep(step_duration)

    def hold(
        self,
        mut_property: str,
        mut_value: int,
        load_property: str,
        load_value: int,
        duration: float,
    ) -> None:
        """Hold both motors' properties at specific values."""
        if not self.running:
            return
        if mut_property == "current":
            self.parent.change_MUT_current(mut_value)  # Send MUT current demand
        if load_property == "rpm":
            self.parent.change_load_rpm(load_value)  # Send load motor RPM demand
        sleep(duration)

    def run(self) -> None:
        """Run the experiment steps."""
        print("Experiment started")
        for step in self.steps:
            print(f"Executing step: {step}")
            if not self.running:
                break
            self.execute_step(step)
        self.parent.change_MUT_current(0)  # Send MUT current demand
        self.parent.change_load_rpm(0)  # Send load motor RPM demand
        return 


class TestAutomator:
    def __init__(self, parent: MainWindow, stop=False) -> None:
        self.parent = parent

    def start_experiment(self, experiment_file: str) -> None:
        """Execute an experiment defined in a JSON file."""
        with open(experiment_file, "r") as file:
            experiment = json.load(file)

        steps = experiment["steps"]
        worker = ExperimentWorker(self.parent, steps)
        worker.run()
        return

    def _on_experiment_finished(self):
        """Handle experiment completion."""
        print("Experiment finished successfully.")

    def _on_experiment_error(self, error_message: str):
        """Handle experiment errors."""
        print(f"Experiment failed with error: {error_message}")


if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    class DummyDyno():
        def change_MUT_current(self, value: float) -> None:
            print(f"Setting MUT current to {value}")
        def change_load_rpm(self, value: int) -> None:
            print(f"Setting load motor RPM to {value}")
    dyno = DummyDyno()
    automator = TestAutomator(dyno)

    # Example: Execute an experiment from a JSON file
    automator.start_experiment("VDyno/experiments/experiment2.json")
