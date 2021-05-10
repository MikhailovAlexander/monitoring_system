import tkinter as tk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")


class RepPlot(tk.Frame):
    """widget for report plot showing"""
    def __init__(self, root, tb_rows):
        super().__init__(root)
        dates = [row[1] for row in tb_rows]
        all_obj = [row[2] for row in tb_rows]
        find_obj = [row[3] for row in tb_rows]
        tr_obj = [row[5] for row in tb_rows]
        wr_obj = [row[7] for row in tb_rows]
        er_obj = [row[9] for row in tb_rows]
        figure = Figure(figsize=(5, 4), dpi=100)
        plot1 = figure.add_subplot(311)
        plot1.set(title="Проверенные объекты", ylabel="Количество объектов")
        plot1.plot(dates, all_obj, dates, find_obj)
        plot1.legend(["Проверенно", "Выявлено"], loc=5, fontsize=6)
        plot2 = figure.add_subplot(313)
        plot2.set(title="Выявленные объекты", ylabel="Количество объектов")
        plot2.plot(dates, tr_obj, dates, wr_obj, dates, er_obj)
        plot2.legend(["Тривиальные", "Предупреждения", "Ошибки"], loc=5,
                     fontsize=6)
        canvas = FigureCanvasTkAgg(figure, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
