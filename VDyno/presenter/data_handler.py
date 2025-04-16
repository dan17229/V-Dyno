from __future__ import annotations
from typing import Protocol
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThreadPool, QRunnable, QTimer
from PyQt6.QtWidgets import QApplication
import os
import sys
import traceback
from time import sleep

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from VDyno.model.dyno import Dyno
from VDyno.presenter.test_automator import TestAutomator
from VDyno.presenter.file_saver import FileSaver

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
        self._args = args
        self._kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        #.kwargs["progress_callback"] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self._args, **self._kwargs)
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
        print("Stopping worker thread...")
        if "stop" in self._kwargs:
            self._kwargs["stop"] = True


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
            if "stop" in self._kwargs:
                self._kwargs["stop"] = True
            self.running = False  # Set the running flag to False
            # If the function supports a stop mechanism, pass the stop flag


class Presenter:
    def __init__(self, dyno: Dyno, view: View, app: QApplication) -> None:
        self.dyno = dyno
        self.view = view
        self.app = app
        self.motor_keys = [
            "Status_RPM_V",
            "Status_TotalCurrent_V",
            "Status_DutyCycle_V",
        ]
        self.transducer_keys = ["TorqueValue"]
        self.MUT_key = 0
        self.load_motor_key = 0
        self.transducer_key = 0
        self.desired_MUT_current = 0
        self.desired_load_rpm = 0
        self.threadpool = QThreadPool()
        self.workers = []  # Keep track of all Worker instances
        self.timer = QTimer()  # Create a QTimer for periodic updates
        self.timer.timeout.connect(self.update_plots)  # Connect the timer to the update method

    def control_motors(self, blank=False, stop = False) -> None:
        if stop is True:
            return
        self.dyno.MUT.set_current(self.desired_MUT_current)
        self.dyno.load_motor.set_rpm(self.desired_load_rpm)
        sleep(1 / 40)  # Sleep for a short duration to avoid busy waiting

    def plot_MUT_changed(self, key: int) -> None:
        self.MUT_key = key

    def plot_load_changed(self, key: int) -> None:
        self.load_motor_key = key

    def plot_TT_changed(self, key: int) -> None:
        self.transducer_key = key

    def object_updater(self, monitor_object: object,stop=False) -> None:
        if stop is True:
            return
        monitor_object.update_status()
        sleep(1 / 40)

    def update_plots(self) -> None:
        """Update the plots with the latest data."""
        self.view.live_plot.update()

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def start_monitor_thread(self):
        """Start monitoring threads."""
        # Create workers
        MUT_worker = InfiniteWorker(self.object_updater, self.dyno.MUT)
        load_worker = InfiniteWorker(self.object_updater, self.dyno.load_motor)
        TT_worker = InfiniteWorker(self.object_updater, self.dyno.torque_transducer)
        control_worker = InfiniteWorker(self.control_motors)

        # Keep track of workers
        self.workers.extend([MUT_worker, load_worker, TT_worker, control_worker])

        # Start workers
        self.threadpool.start(MUT_worker)
        self.threadpool.start(load_worker)
        self.threadpool.start(TT_worker)
        self.threadpool.start(control_worker)

    def start_control_thread(self) -> None:
        """Start the control thread."""
        # Create a worker for the control thread
        control_worker = Worker(self.dyno.control_loop)
        self.workers.append(control_worker)
        self.threadpool.start(control_worker)

    def start_record_thread(self) -> None:
        """Start the recording thread."""
        print("Starting recording thread...")
        recording = FileSaver(self.dyno)
        recording.open()
        record_worker = InfiniteWorker(recording.record)
        self.workers.append(record_worker)
        self.threadpool.start(record_worker)
        print(self.workers)

    def start_plots(self) -> None:
        """Start updating the plots."""
        self.timer.start(1000 // 30)  # Update at 30 FPS (1000 ms / 30)

    def start_experiment(self) -> None:
        """Start an experiment in a separate thread."""
        filename = f"VDyno/experiments/{self.view.selected_experiment}"
        automator = TestAutomator(self.view)
        experiment_worker = Worker(automator.start_experiment, filename)
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
        print("Stopping all threads...")
        for worker in self.workers:
            worker.stop()

        # Clear the worker list
        self.workers.clear()
        print("All threads stopped.")

    def run(self) -> None:
        print("Starting Thread")
        self.start_monitor_thread()
        self.app.aboutToQuit.connect(self.stop_all_threads)
        print("Running the presenter")
        self.view.init_UI(self)
