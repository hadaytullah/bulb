#from scenario import Scenario
import numpy as np
import matplotlib.pyplot as plt

class Home:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        
        #self.scenario = Scenario()
        
        #self.room = np.zeros((self.width,self.height))
        #self.environment = np.zeros((self.width,self.height))
        self.bulbs = np.zeros((self.width,self.height))
        self.luminosity = np.zeros((self.width,self.height))
        self.presence = np.zeros((self.width,self.height))
    
    def create_plot(self, location, title, data, plot_cmap='gray_r', plot_interpolation='nearest', plot_vmin=0, plot_vmax=1, plot_animated=False):

        plot = self.fig.add_subplot(location)
        plot.set_title(title, y=1.08)
        plot.xaxis.tick_top()
        #presence_plot_x, presence_plot_y = np.meshgrid(np.arange(self.width), np.arange(self.height))
        plt.gca().invert_yaxis()
        #presence_plot.scatter(presence_plot_x, presence_plot_y, c=self.presence, cmap='gray_r', marker='+')
        #presence_plot.grid(color='g', linestyle='-', linewidth=1)
        #presence_draw_array = np.where(self.presence<1, 1, 0)
        plot.set_xticks(np.arange(self.width)+0.5)
        plot.set_yticks(np.arange(self.height)+0.5)
        plot.set_yticklabels([])
        plot.set_xticklabels([])
        image = plt.imshow(data, cmap=plot_cmap, interpolation=plot_interpolation, vmin=plot_vmin, vmax=plot_vmax, animated=plot_animated)
        plt.grid()
        return image

    def init_figures(self):

        self.fig = plt.figure(figsize=(1, 4))#, dpi=80, facecolor='w', edgecolor='k')
        #self.fig.set_size_inches(200,200)
        self.create_plot(location=141, title='Presence', data=self.presence, plot_cmap='gray_r', plot_interpolation='nearest', plot_vmin=0, plot_vmax=1)

#        presence_plot = self.create_plot(141, 'Presence', self.presence)
#        presence_plot = self.fig.add_subplot(141)
#        presence_plot.set_title("Presence", y=1.08)
#        presence_plot.xaxis.tick_top()
#        #presence_plot_x, presence_plot_y = np.meshgrid(np.arange(self.width), np.arange(self.height))
#        plt.gca().invert_yaxis()
#        #presence_plot.scatter(presence_plot_x, presence_plot_y, c=self.presence, cmap='gray_r', marker='+')
#        #presence_plot.grid(color='g', linestyle='-', linewidth=1)
#        #presence_draw_array = np.where(self.presence<1, 1, 0)
#        presence_plot.set_xticks(np.arange(self.width)+0.5)
#        presence_plot.set_yticks(np.arange(self.height)+0.5)
#        presence_plot.set_yticklabels([])
#        presence_plot.set_xticklabels([])
#
#        plt.imshow(self.presence, cmap='gray_r', interpolation='nearest', vmin=0, vmax=1)
#        #plt.xticks(np.arange(0,self.width,0.5))#[1, 2, 3, 4, 5])
#        #plt.yticks(np.arange(0,self.height,0.5))
#
#        #plt.scatter(x, y)
#        plt.grid()
#
        self.create_plot(location=142, title='Faulty Bulbs', data=self.bulbs, plot_cmap='Reds_r', plot_interpolation='nearest', plot_vmin=-1, plot_vmax=0)

#        bulbs_faulty_plot = self.fig.add_subplot(142)
#        #bulbs_faulty_plot.title.set_text("Faulty Bulbs")
#        bulbs_faulty_plot.set_title("Faulty Bulbs", y=1.08)
#        bulbs_faulty_plot.xaxis.tick_top()
#        plt.gca().invert_yaxis()
#        plt.imshow(self.bulbs, cmap='Reds_r', interpolation='nearest', vmin=-1, vmax=0)
#
        #bulbs_faulty_x, bulbs_faulty_y = np.meshgrid(np.arange(self.width), np.arange(self.height))

        #data = [x.ravel(), y.ravel()]
        #bulbs_faulty_plot.scatter(bulbs_faulty_x, bulbs_faulty_y, c=self.bulbs)
        #plt.title(figure_title, y=1.08)

        self.im = self.create_plot(location=143, title='Turned ON Bulbs', data=self.bulbs, plot_cmap='Blues', plot_interpolation='nearest', plot_vmin=0, plot_vmax=1, plot_animated=True)

#        bulbs_on_plot = self.fig.add_subplot(143)
#        bulbs_on_plot.set_title("Turned ON Bulbs", y=1.08)
#        bulbs_on_plot.xaxis.tick_top()
#        #bulbs_on_x, bulbs_on_y = np.meshgrid(np.arange(self.width), np.arange(self.height))
#        plt.gca().invert_yaxis()
#        #self.im = bulbs_on_plot.scatter(bulbs_on_x, bulbs_on_y, c=self.bulbs, animated=True)
#        self.im = plt.imshow(self.bulbs, cmap='Blues', interpolation='nearest', animated=True, vmin=0, vmax=1)

        self.luminosity_im = self.create_plot(location=144, title='Luminosity', data=self.bulbs, plot_cmap='inferno', plot_interpolation='bilinear', plot_vmin=0, plot_vmax=1, plot_animated=True)

#        luminosity_plot = self.fig.add_subplot(144)
#        luminosity_plot.set_title("Luminosity", y=1.08)
#        luminosity_plot.xaxis.tick_top()
#        self.luminosity_im = plt.imshow(self.bulbs, cmap='inferno', interpolation='bilinear', animated=True, vmin=0, vmax=1)

    def control(self):
        pass
