

import numpy as np

import numpy.core._methods 
import numpy.lib.format
import vtk
import pandas as pd
import nrrd
from allensdk.api.queries.rma_api import RmaApi
import os
import matplotlib.pyplot as plt
import collections
import csv
import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter import *





class Window(Frame):
        

        def __init__(self, master):
            rma = RmaApi()

            self.structgraph = pd.DataFrame(
            rma.model_query('Structure',
                            criteria='[graph_id$eq1]',
                            num_rows='all'))
            volume = 'App_File/annotation_25.nrrd'

            self.readdata, header= nrrd.read(volume)

            Frame.__init__(self, master)                 
            self.master = master
            self.init_window()

            

            
        def init_window(self):
            # changing the title of our master widget      
            self.master.title("McMullan group Labeler")

            # allowing the widget to take the full space of the root window
            self.pack(fill=BOTH, expand=1)

            # creating a button instance
            Loadbutton = Button(self, text="Load File", command=self.fileopen)

            # placing the button on my window
            Loadbutton.place(x=10, y=30)
            
            Frequenciebutton = Button(self, text="Get Frequencies", command=self.GetFrequencies)
            
            Frequenciebutton.place(x=10, y=70)
            
            Graphbutton = Button(self, text="Graph Frequencies", command=self.GraphFrequencies)
            
            Graphbutton.place(x=10, y=110)
            
            labelbutton = Button(self, text="Add labels to coordinates", command=self.Append)
            
            labelbutton.place(x=10, y=150)
            
            quickview = Button(self, text="quickview your coordinates", command=lambda: dimensionvisual)
            
    
        
            
            scrollbar = Scrollbar(self) 
            scrollbar.pack(side = RIGHT, fill = Y ) 
            
            self.mylist = Listbox(self, yscrollcommand = scrollbar.set )
            self.mylist.pack( side = BOTTOM, fill = BOTH ) 
        

            
        def fileopen(self):
            self.Coord = askopenfilename() 
            
            
            Tk().withdraw()
            self.my_data= np.genfromtxt(self.Coord, delimiter=',', dtype=int)

            self.my_data=self.my_data[1::,:]
            ones=np.ones((np.shape(self.my_data)), dtype=int)
            self.my_data=np.round(self.my_data)

            self.my_data=(self.my_data* ones)

            
            datalist=[]   
            for i in (range(len(self.my_data))):
                datalist.append(self.readdata[tuple(self.my_data[i])])    
            self.full_search=[]
            self.name=[]

            for i in range(len(datalist)):
                try: 
                    self.name.append(self.structgraph.loc[self.structgraph['id']==datalist[i]]['safe_name'].iloc[0])
                    self.full_search.append(self.structgraph.loc[self.structgraph['id']==datalist[i]].iloc[0])
                except IndexError:
                    self.name.append('not in the brain')
                    self.full_search.append('not in the brain')
            thetime=datetime.datetime.now().strftime("%A.%f")
            

            self.labels, self.values = zip(*collections.Counter(self.name).items())
            path=os.path.abspath(self.Coord)
            os.makedirs(path+"_output"+thetime)
            path=(os.path.abspath(path+"_output"+thetime))
            self.path= path+"\\" 
        
        def generate3d(self):
            



            spheres = [ vtk.vtkSphereSource() for _ in (range(len(self.my_data)))]


            colors = vtk.vtkNamedColors()
            appendFilter=vtk.vtkAppendPolyData()
            # Create a sphere

            for i in (range(len(self.my_data))):
                spheres[i].SetCenter(i, i, i)
                spheres[i].SetRadius(10)
                spheres[i].Update()
                appendFilter.AddInputData(spheres[i].GetOutput())

                appendFilter.Update()
                

            appendFilter.Update()
            writer=vtk.vtkPolyDataWriter()
            writer.SetInputData(appendFilter.GetOutput())
            writer.SetFileName('abc.vtk')
            writer.Update()
            
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(appendFilter.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(colors.GetColor3d("Cornsilk"))

            renderer = vtk.vtkRenderer()
            renderWindow = vtk.vtkRenderWindow()
            renderWindow.SetWindowName("Sphere")
            renderWindow.AddRenderer(renderer)
            renderWindowInteractor = vtk.vtkRenderWindowInteractor()
            renderWindowInteractor.SetRenderWindow(renderWindow)

            renderer.AddActor(actor)
            renderer.SetBackground(colors.GetColor3d("LightBlue"))

            renderWindow.Render()
            renderWindowInteractor.Start()

            self.mylist.insert(END, self.path+'my_data.nrrd')


            
        def Append(self):
            self.namearray=np.asarray(self.name)
            fullsearcharray=np.asarray(self.full_search)

            appendeddata=np.column_stack((self.my_data, self.namearray))

            with open(self.path+"Appended.csv", 'w') as csvfile: 
                fieldnames=['x', 'y', 'z', 'region']
                writer=csv.DictWriter(csvfile, fieldnames)
                writer.writeheader()
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerows(appendeddata)

            self.mylist.insert(END, 'Data Appended')
        
        def GetFrequencies(self):
            labelvalues=(self.labels, self.values)

            with open(self.path+"Frequencies.csv", 'w') as csvfile:
                fieldnames=['region ', 'frequency']
                writer = csv.DictWriter(csvfile, fieldnames)
                writer.writeheader()
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerows(np.array(labelvalues).T.tolist())
                self.mylist.insert(END, 'Frequencies saved')
                self.mylist.insert(END, fieldnames)

        def GraphFrequencies(self):
            indexes= np.arange(len(self.labels))
            ymax=(np.arange(0, (np.amax(self.values)), np.sqrt(np.amax(self.values))))
            plt.bar(indexes, self.values)
            plt.yticks(ymax)
            plt.xticks(indexes, self.labels, rotation='vertical')
            plt.autoscale(enable=True, axis='both', tight=None)
            plt.savefig(self.path+"\graph.png", bbox_inches='tight')
            plt.show()
            self.mylist.insert(END, 'Graph saved')


        def Rootquit(self):
            
            self.master.destroy
            app.quit

        
        

if __name__ == '__main__':
    root = Tk()
    #size of the window
    root.geometry("400x600")
    app =  Window(root)
    root.protocol("WM_DELETE_WINDOW", app.quit)
    root.mainloop()  
