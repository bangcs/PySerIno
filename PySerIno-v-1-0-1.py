#Program ini berlisensi CC-BY-SA
#Nama program PySerIno
#Dikoding oleh Febri CS

import tkinter as tk
from tkinter import ttk
import serial
import threading
import csv
from datetime import datetime


class SerialMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PySerIno")
        width = 16 *35
        height = 9 *35

        root.geometry(f"{width}x{height}")
        # Buat objek Serial
        self.serial_port = None

        # Buat UI
        self.create_ui()

        # Mengaitkan metode khusus untuk menangani penutupan jendela
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Menyimpan file dalam format csv
        self.csv_file = None
        self.csv_writer = None

    def create_ui(self):

        # Label untuk status koneksi
        self.connection_status_label = tk.Label(self.root, text="Status: Tidak Terkoneksi", pady=10)
        self.connection_status_label.place(x=200, y=32)

        # Entry untuk memasukkan nama port
        self.port_entry_label = tk.Label(self.root, text="Nama Port:")
        self.port_entry_label.place(x=16, y=64)
        self.port_entry = tk.Entry(self.root)
        self.port_entry.place(x=16, y=80)

        # Button untuk mengelola koneksi serial
        self.connection_button = tk.Button(self.root, text="Buka Koneksi", command=self.toggle_serial_connection)
        self.connection_button.place(x=16, y=112) # Meletakkan tombol di sebelah kiri

        # Button untuk memulai dan menghentikan penyimpanan data ke file CSV
        self.save_button = tk.Button(self.root, text="Simpan Data CSV", command=self.toggle_csv_logging)
        self.save_button.place(x=16, y=160) # Meletakkan tombol di sebelah kanan

        # Text untuk menampilkan data serial
        self.serial_data_text = tk.Text(self.root, height=10, width=40, state=tk.DISABLED)
        self.serial_data_text.place(x=200, y=64)

        # Thread untuk membaca data serial
        self.serial_thread = None
        self.is_serial_reading = False



    def toggle_csv_logging(self):
        if not self.csv_file:
            # Mulai menyimpan data ke file CSV
            filename = f"serial_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            self.csv_file = open(filename, mode='w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(["Timestamp", "Suhu (Celsius)", "Arus (miliAmper)"])
            self.save_button.config(text="Hentikan Simpan CSV")

        else:
            # Hentikan penyimpanan data ke file CSV
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None
            self.save_button.config(text="Simpan Data CSV")

    def toggle_serial_connection(self):
        if self.serial_port is None:
            # Buka koneksi serial
            try:
                port_name = self.port_entry.get()
                self.serial_port = serial.Serial(port_name, 9600, timeout=1)  # Sesuaikan dengan baudrate yang sesuai
                self.connection_status_label.config(text="Status: Terkoneksi")
                self.connection_button.config(text="Tutup Koneksi")

                # Mulai thread untuk membaca data serial
                self.is_serial_reading = True
                self.serial_thread = threading.Thread(target=self.read_serial_data)
                self.serial_thread.start()

            except serial.SerialException as e:
                self.connection_status_label.config(text=f"Error: Arduino tidak ditemukan")

        else:
            # Tutup koneksi serial
            try:
                self.is_serial_reading = False
                self.serial_port.close()
                self.serial_port = None
                self.connection_status_label.config(text="Status: Tidak Terkoneksi")
                self.connection_button.config(text="Buka Koneksi")
            except :
                pass

    def read_serial_data(self):
        while self.is_serial_reading:
            try:
                data = self.serial_port.readline().decode("ascii")
                if data:
                    self.update_serial_data(data)
            except UnicodeDecodeError:
                pass  # Skip karakter yang tidak dapat di-decode
            except TypeError:
                pass

    def update_serial_data(self, data):
        # Pisahkan data menjadi dua bagian: suhu dan arus
        # bagian ini adalah variabel data yang dapat diubah - ubah 
        suhu, current = data.strip().split(",")

        # Format pesan dan tampilkan di Text
        formatted_message = f"Arus: {current} mA \nSuhu: {suhu}\u00b0C \n"

        self.serial_data_text.config(state=tk.NORMAL)
        self.serial_data_text.insert(tk.END, formatted_message)
        self.serial_data_text.config(state=tk.DISABLED)
        self.serial_data_text.see(tk.END)  # Auto-scroll ke akhir teks

        if self.csv_writer:
            suhu, current = data.strip().split(",")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.csv_writer.writerow([timestamp, suhu, current])


    def on_close(self):
        # Metode ini akan dipanggil saat jendela ditutup
        if self.serial_port:
            self.toggle_serial_connection()  # Tutup koneksi serial sebelum menutup jendela

        if self.csv_file:
            self.csv_file.close()

        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitorApp(root)
    root.mainloop()
