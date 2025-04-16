import csv
from datetime import datetime
import os
from time import sleep

class FileSaver:
    def __init__(self, parent):
        """
        Initialize the FileSaver with three sets of data.
        :param data1: Dictionary
        :param data2: Dictionary
        :param data3: Dictionary
        """
        self.parent = parent
        self.data1 = parent.MUT.status
        self.data2 = parent.load_motor.status
        self.data3 = parent.torque_transducer.status
        self.file = None
        self.writer = None

    def open(self):
        """
        Create a .csv file with the current date and time as the name and prepare it for recording.
        """
        # Ensure the folder exists
        folder_path = "data_output/results"
        os.makedirs(folder_path, exist_ok=True)

        # Create the file in the specified folder
        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.csv")
        file_path = os.path.join(folder_path, filename)
        self.file = open(file_path, mode='w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        
        # Write the header row (keys from all dictionaries)
        headers = list(self.data1.keys()) + list(self.data2.keys()) + list(self.data3.keys())
        self.writer.writerow(headers)

    def record(self, stop:bool=False):
        """
        Write the current state of the three dictionaries to the file as a new line.
        """
        if stop:
                print("Stopping recording...")
                return  # Exit the method if stop is True
        
        self.data1 = self.parent.MUT.status
        self.data2 = self.parent.load_motor.status
        self.data3 = self.parent.torque_transducer.status
        if not self.writer:
            raise ValueError("File is not open. Call 'open' before recording.")
        
        # Write only the values from the dictionaries
        row = list(self.data1.values()) + list(self.data2.values()) + list(self.data3.values())
        self.writer.writerow(row)
        sleep(1/40)

    def close(self):
        """
        Close the .csv file.
        """
        print("Closing file...")
        if self.file:
            self.file.close()
            self.file = None
            self.writer = None

if __name__ == "__main__":
    # Example dictionaries
    data1 = {"Name": "Alice", "Age": 30}
    data2 = {"City": "New York", "Country": "USA"}
    data3 = {"Job": "Engineer", "Salary": 100000}

    # Create an instance of FileSaver
    file_saver = FileSaver(data1, data2, data3)

    # Open the file (creates a .csv file with headers in the specified folder)
    file_saver.open()

    # Record the current state of the dictionaries (writes values as a row)
    file_saver.record()

    # Modify the dictionaries to simulate new data
    data1["Name"] = "Bob"
    data1["Age"] = 25
    data2["City"] = "Los Angeles"
    data2["Country"] = "USA"
    data3["Job"] = "Designer"
    data3["Salary"] = 80000

    # Record the updated state of the dictionaries
    file_saver.record()

    # Close the file
    file_saver.close()

