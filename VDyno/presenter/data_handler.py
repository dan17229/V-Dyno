from __future__ import annotations
from typing import Protocol
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThreadPool, QRunnable
from PyQt6.QtWidgets import QApplication
import os
import sys
import traceback
from time import sleep

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from VDyno.model.dyno import Dyno
from VDyno.presenter.test_automator import TestAutomator


class View(Protocol):
    def init_ui(self, presenter: Presenter) -> None: ...


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    stop = pyqtSignal()


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            print("Error in worker thread: %s" % e)
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

    def stop(self):
        """Stop the worker thread."""
        pass  # Implement stop!!!!!!


class InfiniteWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self._args = args
        self._kwargs = kwargs
        self.signals = WorkerSignals()

        self.running = True  # Add a running flag

    @pyqtSlot()
    def run(self):
        """Run the worker function."""
        while self.running:  # Check the running flag
            try:
                self.fn(*self._args, **self._kwargs)
            except Exception as e:
                print(f"Error in worker thread: {e}")
                traceback.print_exc()
                exctype, value = sys.exc_info()[:2]
                self.signals.error.emit((exctype, value, traceback.format_exc()))

    def stop(self):
        """Stop the worker thread."""
        self.running = False


class Presenter:
    def __init__(self, dyno: Dyno, view: View) -> None:
        self.dyno = dyno
        self.view = view
        self.motor_keys = [
            "Status_RPM_V",
            "Status_TotalCurrent_V",
            "Status_DutyCycle_V",
        ]
        self.transducer_keys = ["TorqueValue"]
        self.MUT_key = 0
        self.load_motor_key = 0
        self.transducer_key = 0
        self.threadpool = QThreadPool()
        self.workers = []  # Keep track of all Worker instances

    def command_MUT_rpm(self) -> None:
        self.dyno.MUT.set_rpm(self.view.get_rpm())

    def command_load_brake_current(self) -> None:
        self.dyno.load_motor.set_brake_current(self.view.get_brake_current())

    def plot_MUT_changed(self, key: int) -> None:
        self.MUT_key = key

    def plot_load_changed(self, key: int) -> None:
        self.load_motor_key = key

    def plot_TT_changed(self, key: int) -> None:
        self.transducer_key = key

    def object_updater(self, monitor_object: object) -> None:
        monitor_object.update_status()
        sleep(1 / 40)

    def update_plots(self) -> None:
        self.view.update_MUT_plot(
            self.dyno.MUT.status[self.motor_keys[self.MUT_key] + "1"]
        )
        self.view.update_load_motor_plot(
            self.dyno.load_motor.status[self.motor_keys[self.load_motor_key] + "2"]
        )
        self.view.update_transducer_plot(
            self.dyno.torque_transducer.status[
                self.transducer_keys[self.transducer_key]
            ]
        )
        sleep(1 / 20)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def start_monitor_thread(self):
        """Start monitoring threads."""
        # Create workers
        MUT_worker = InfiniteWorker(self.object_updater, self.dyno.MUT)
        load_worker = InfiniteWorker(self.object_updater, self.dyno.load_motor)
        TT_worker = InfiniteWorker(self.object_updater, self.dyno.torque_transducer)

        # Keep track of workers
        self.workers.extend([MUT_worker, load_worker, TT_worker])

        # Start workers
        self.threadpool.start(MUT_worker)
        self.threadpool.start(load_worker)
        self.threadpool.start(TT_worker)

    def start_control_thread(self) -> None:
        """Start the control thread."""
        # Create a worker for the control thread
        control_worker = Worker(self.dyno.control_loop)
        self.workers.append(control_worker)
        self.threadpool.start(control_worker)

    def start_plots(self) -> None:
        """Update the plots in a separate thread."""
        while True:
            self.update_plots()

    def start_experiment(self, filename: str) -> None:
        """Start an experiment in a separate thread."""
        automator = TestAutomator(self.dyno)
        experiment_worker = InfiniteWorker(automator.start_experiment, filename)
        self.workers.append(experiment_worker)
        self.threadpool.start(experiment_worker)
        print("Thread setup complete")

    def get_experiment_list(self) -> list[str]:
        experiments_dir = os.path.join(os.path.dirname(__file__), "../experiments")
        if not os.path.exists(experiments_dir):
            return []
        return [
            f
            for f in os.listdir(experiments_dir)
            if os.path.isfile(os.path.join(experiments_dir, f))
        ]

    def stop_all_threads(self) -> None:
        """Stop all running threads."""
        # Stop all workers
        for worker in self.workers:
            worker.stop()

        # Clear the worker list
        self.workers.clear()
        print("All threads stopped.")

    def run(self) -> None:
        print("Starting Thread")
        self.start_monitor_thread()
        QApplication.instance().aboutToQuit.connect(self.stop_all_threads)
        print("Running the presenter")
        self.view.init_UI(self)
