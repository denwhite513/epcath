#Params Class
'''
Last Modified: 10/10/19
Description: Params Class to set and get parameters from user via Widgets (GUI)

@author: cindiewu
'''

import Simulation
import os

#from https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Basics.html
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import Button, Layout




##################################### HELPER METHODS #####################################

def test():
    p = Params(101)
    return p


##################################### CLASS DEFINITION #####################################
class Params():
    
    def __init__(self):

        ############# VERIFY THE FOLLOWING VALUES BEFORE RUNNING (A-E) ##############

        ###### A. Information regarding the scheduling parameters ######

        self.daysInPeriod = 260          # integer: Number of days in period

        #minuteResolution = 5        # the resolution in terms of minutes you want to model
        self.totalTimeRoom = 10.58*60    # total time available in a room per day (min)
        self.closeCap = 10.0*60          # time cap for closing a room (min)
        self.turnover = 0                # estimated time for room turnover (min)
        self.labStartTime = (8,0)        # time of morning that the lab starts operating (8.0 = 8:00 AM, 8.5 = 8:30 AM, etc)
        self.labEndTime = (18,0)         # time of evening that the lab technically ends operating

        self.secondShiftStart = (13,0)   # earliest time that the second shift is allowed to start


        self.numCathRooms = 5            # number of Cath rooms available per day
        self.numEPRooms = 4              # number of EP rooms available per day
        self.numMiddleRooms = 2

        self.numRestrictedCath = 5       # default to no reserved rooms for emergencies
        self.numRestrictedEP = 4         # default to no reserved rooms for emergencies
        self.restrictWeeks = True        # whether or not to restrict the same week procedures to the number of restricted rooms
        self.restrictDays = True         # whether or not to restrict the same day procedures to the number of restricted rooms
        self.restrictEmergencies = False # whether or not to restrict the emergency procedures to the number of restricted rooms

        ###### B. Information regarding the order of information in the PROCEDURE data sheet ######

        self.numEntries = 16             # number of columns in data sheet
        self.iDay = 0                    # index: Day of period
        self.iWeek = 1                   # index: Week of period
        self.iLab = 2                    # index: Lab key (Cath - 0, EP - 1)
        self.iProcTime = 3               # index: Procedure time (minutes)
        self.iSchedHorizon = 4           # index: Scheduling horizon key
        self.iRoom = 5                   # index: Room constraint (Cath only - 0, EP only - 1, either - 2)
        self.iPreTime = 6                # index: The amount of pre-procedure holding time needed (hours)
        self.iPostTime = 7               # index: The amount of post-procedure holding time needed (hours)
        self.iProcType = 8               # index: Procedure type key
        self.iProvider = 9               # index: Provider key
        self.iPreProcHBCleanTime = 10    # index: The number of hours it took to clean the HB after pre-procedure prep (hours)
        self.iPostProcHBCleanTime = 11   # index: The number of hours it took to clean the HB after post-procedure recovery (hours)   
        self.iHistoricalOrder = 12       # index: The order in which the procedure started historically in its own lab
        self.iProcTimeMinusTO = 13       # index: Procedure time minus post procedure room turnover time (minutes) - used for Holding Bay placement
        self.iPostProcTOTime = 14        # index: Post procedure room turnover time (minutes)
        self.ID = 15             # index: The procedure ID

        ############## The keys used in the data file

        self.cathID = 0.0
        self.epID = 1.0
        self.middleID = 3.0
        self.fullShiftID = 1
        self.halfShiftID = 0.5
        self.quarterShiftID = 0.25
        self.roomConstraint = {0.0:'Cath', 1.0:'EP', 2.0:'either', 3.0:'middle'}


        ###### C. Information regarding the order of information in the SHIFTS data sheet ######

        self.numShiftEntries = 7        # number of columns in data sheet
        self.iDayS = 0                   # index: Day of period
        self.iShiftLength = 1          # index: Total procedure time for that provider for that day (hours) 
        self.iNumProcedures = 2    # index: Total number of procedure time for that provider for that day (hours) 
        self.iShiftType = 3       # index: Type of shift (Quarter - 0.25, Half - 0.5, Full - 1) 
        self.iLabS = 4            # index: Lab key (Cath - 0, EP - 1)
        self.iProviderS = 5       # index: Provider key must match key from PROCEDURE data
        self.iRoomS = 6           # index: Room constraint (Cath only - 0, EP only - 1, either - 2)


        ###### D. Information regarding constraint policies ######

        # UNCOMMENT the middle room holding bay policy you want to implement

        # SPECIFY the number of rooms that allow crossover shifts in each lab
        self.cathCrossOverRooms = 5
        self.epCrossOverRooms = 4

        # UNCOMMENT the flexibility restriction policy you want to implement
        # key: 0 - Cath Only, 1 - EP Only, 2 - Flexible
        self.restrictRooms = True        # will restrict shifts to labs based on their room assignment
        #restrictRooms = False       # will implement a "lab preference" shift scheduling

        # SPECIFY any value changes to the shift room parameter
        # format: (shiftTypeToChange, desiredRoomValue)
        # e.g. [(.25, 2.0),(0.5,2.0)] changes all quarter and half shifts to flexible
        self.roomValueChanges = []

        # UNCOMMENT the procedure sorting policy you want to implement
        self.sortProcs = True            # will sort procedures before placing them
        #self.sortProcs = False          # will place procedures according to the order in the input data file 

        self.sortIndex = self.iProcTime       # will sort procedures within shifts based on the procedure time
        #self.sortIndex = self.iPostTime       # will sort based on holding bay recovery time
        self.sortDescend = True          # longest procedures first
        #sortDescend = False         # shortest procedures first

        # UNCOMMENT the post procedure time policy you want to implement
        # Information for holding bays
        #postProcRandom = True       # will draw the post procedure time from a random distribution with a specified mean and std deviation
        self.postProcRandom = False      # will use the post procedure time specified in the input data
        #desiredMean = 3.0           # in hours
        #desiredStDev= 0.25          # in hours

        # Set the number of hours for holding bay time so that patients with a value less than this will not 
        # use the HB at all. This is to filter out unrealistically short HB values

        self.MinHBTime = 0.1

        # SET the number of hours in the day after which the holding bays should close:
        self.HBCloseTime = 40           #For now, set to something large enough but just report up to desired (24-hours) close time.

        # SPECIFY the resolution for holding bay times
        #resolution = 1.0            # in minutes   
        self.resolution = 5.0           # in minutes

        #Modify the holding bay cleaning time - pre
        #preProcHBCleanTimeRandom = False    
        self.preProcHBCleanTimeRandom = True    #Choose this to change HB cleaning time
        self.desiredPreCleanMean = 0.1
        self.desiredPreCleanStDev = 0.05

        #Modify the holding bay cleaning time - post
        #postProcHBCleanTimeRandom = False   
        self.postProcHBCleanTimeRandom = True    #Choose this to change HB cleaning time
        self.desiredPostCleanMean = 0.1
        self.desiredPostCleanStDev = 0.05


        # Convert pre proc time to hours
        self.ConvertPreProcToHours = False
        #ConvertPreProcToHours = True

        # Cap the amount of time a patient can spend in a pre-procedure room
        #CapHBPreProc = False
        self.CapHBPreProc = True
        self.HBPreProcCap = 7   

        # Multiply the amount of Post Procedure time each patient needs
        self.multPostProcTime = False
        #multPostProcTime = True
        self.PostProcMult = 1

        # UNCOMMENT holding bay policies to implement for Middle Room procedures
        #schedMRinHB = True      # will schedule MR procs into the holding bay
        self.schedMRinHB = False

        self.middleRoomPreRandom = True  # will set middle room pre time to a random number given a desired mean/stdev
        #middleRoomPreRandom = False
        self.desiredPreMeanMR = .5
        self.desiredPreStDevMR = 0.1

        self.middleRoomPostRandom = True # will set middle room post time to a random number given a desired mean/stdev
        #middleRoomPostRandom = False
        self.desiredPostMeanMR =  0.5
        self.desiredPostStDevMR = 0.1

        # UNCOMMENT to CHANGE a provider's procedures for a given day pair
        self.ChangeProviderDays=False
        #ChangeProviderDays=True
        self.providerChanges = {16:(3,4),8:(0,4)} #Dict of triplets - (provider key, day from, day to)

        # UNCOMMENT to SWAP a provider's procedures for a given day pair
        self.SwapProviderDays = False    
        #SwapProviderDays = True    
        self.providerSwaps = {16:(3,4)} #List of triplets - (provider key, day from, day to)


        ###### E. Information regarding the name/location of the data file ######

        # UNCOMMENT the working directory, or add a new one
        #os.chdir("/Users/nicseo/Desktop/MIT/Junior/Fall/UROP/Scheduling Optimization/Script")
        #os.chdir("/Users/dscheinker/Documents/EP_CATH/Simulation_Model_and_Data/")
        os.chdir("/home/matrix/")

        # UNCOMMENT both the PROCEDURE data set and the corresponding SHiFT data set 
        # or add a new pair

        ###############These include both primetime and non-primetime  procedures

        #These files contain only historical procedure data
        self.procDataFile= 'InputData/CathFlatEPFlatShiftsJuly2015.csv'
        self.shiftDataFile = 'InputData/ShiftsFlatFlatJuly2015.csv'    

        #These files contain historical procedure data with two additional high volume  EP providers modeled
        #procDataFile= 'InputData/CathFlatEPGrow2ShiftsJuly2015.csv'
        #shiftDataFile = 'InputData/ShiftsFlatGrow2July2015.csv'

        #These files contain historical procedure data for the Cath lab only for comparison
        #procDataFile= 'InputData/CathOnlyShiftsJuly2015.csv'
        #shiftDataFile = 'InputData/ShiftsCathOnlyJuly2015.csv'

        #These files contain data for testing something new
        #procDataFile= 'InputData/TestProcs.csv'
        #shiftDataFile = 'InputData/TestShifts.csv'    


        ###### information regarding the name/location of the output data ######

        # please name the workbook to save the primary output to
        self.readWorkbook = "OutputData/testRead.csv"
        self.processWorkbook = "OutputData/testProcess.csv"

        # please name the workbook to save the holding bay output to
        self.holdingBayWorkbook = "OutputData/holdingBayOccupancy.csv" 
        
        #Instructions widget
        self.wLbl1=widgets.Label(value="SET THE FOLLOWING PARAMETERS, THEN CLICK GO!", layout=Layout(width='50%', height='80%'))
        self.wLbl2=widgets.Label(value="REQUIRED PARAMETERS:", layout=Layout(width='50%', height='80%'))

        #Procedure Placement Priority? sortProcs, sortIndex, sortDescend
        # Longest procedures First [sortProcs=True, sortIndex=iProcTime, sortDescend=True]
        # Shortest procedures First [sortProcs=True, sortIndex=iProcTime, sortDescend=False]
        # Longest holding bay recovery time procedures First [sortProcs=True, sortIndex=iPostTime, sortDescend=True]
        # Historical order of procedures by day [sortProcs=True, sortIndex=iHistoricalOrder, sortDescend=False]
        # Historical order of procedures by room - (to be implemented)
        self.wSortPriority=widgets.Dropdown(
            options=['historical', 'longest procedures first', 'shortest procedures first', 'longest recovery time first', 'shortest recovery time first'],
            value='historical',
            description='Procedure placement priority: ',
            disabled=False,
            style = {'description_width': 'initial'},
            layout=Layout(width='50%', height='auto')
        )

        #Label: Optional Parameters
        self.wLblOptional=widgets.Label(value="OPTIONAL PARAMETERS (YOU MAY ACCEPT THE DEFAULT VALUES):", layout=Layout(width='50%', height='80%'))
        
        #Procedures and Shifts Data Files
        self.wFiles=widgets.Dropdown(
            options=['historical', 'two additional high-volume EP providers', 'CATH lab only', 'test'],
            value='historical',
            description='Case volume scenario to analyze: ',
            disabled=False,
            style = {'description_width': 'initial'},
            layout=Layout(width='50%', height='auto')
        )

        #Mean Holding Bay Cleaning Time
        self.wMeanHBCleanTime = widgets.FloatText(
            value=0.1,
            min=0.01,
            max=1,
            description='Mean Holding Bay Cleaning Time (hours): ',
            disabled=False,
            style = {'description_width': 'initial'},
            layout=Layout(width='50%', height='auto')
        )

        #Resolution: Duration (minutes) of each timeblock
        self.wRes = widgets.FloatText(
            value=5.0,
            min=1.0,
            max=10.0,
            description='Resolution (minutes): ',
            disabled=False,
            style = {'description_width': 'initial'},            
            layout=Layout(width='50%', height='auto')
        )


        
        # number of Cath rooms available per day
        self.wNumCathRooms = widgets.IntSlider(
            value=5,
            min=1,
            max=10,
            step=1,
            description='Number of Cath Rooms',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            style = {'description_width': '150px'},
            layout=Layout(width='50%', height='auto'),
            readout=True,
            readout_format='d'
        )
        

        #Button widget
        self.button = widgets.Button(description="Go!")
        self.output = widgets.Output()
        
        #Group all widgets
        self.wAllWidgets = widgets.VBox([
                self.wLbl1, self.wLbl2,
                self.wSortPriority,
                self.wLblOptional,
                self.wFiles,
                self.wMeanHBCleanTime,
                self.wRes,
                self.wNumCathRooms], 
            layout=Layout(height='100%'))
        
    #call this to display GUIs to set parameters
    def setParams(self):
        #Display all widgets
        display(self.wAllWidgets)
        display(self.button, self.output)
        #define actions upon button click
        def on_button_clicked(b):
            #close widgets
            self.wAllWidgets.close()
            self.button.close()

            # update local parameters based on user entries via GUI
            self.getSortPriorityVars()
            self.getScenarioFileNames()
            self.desiredPreCleanMean = self.wMeanHBCleanTime.value
            self.desiredPostCleanMean = self.wMeanHBCleanTime.value
            self.resolution = self.wRes.value
            self.numCathRooms = self.wNumCathRooms.value    
            
            #run the simulation
            with self.output:
                print("...running simulation now... please wait... ")
                Simulation.RunSimulation(self)

        self.button.on_click(on_button_clicked)
    
        
    def getSortPriorityVars(self):
        if self.wSortPriority.value == 'longest procedures first':
            self.sortProcs=True
            self.sortIndex=self.iProcTime
            self.sortDescend=True
        elif self.wSortPriority.value == 'shortest procedures first':
            self.sortProcs=True
            self.sortIndex=self.iProcTime
            self.sortDescend=False
        elif self.wSortPriority.value == 'longest recovery time first':
            self.sortProcs=True
            self.sortIndex=self.iPostTime
            self.sortDescend=True  
        elif self.wSortPriority.value == 'shortest recovery time first':
            self.sortProcs=True
            self.sortIndex=self.iPostTime
            self.sortDescend=False             
        elif self.wSortPriority.value == 'historical':
            self.sortProcs=True
            self.sortIndex=self.iHistoricalOrder
            self.sortDescend=False               
        else: #default to historical if nothing selected (impossible)
            self.sortProcs=True
            self.sortIndex=self.iHistoricalOrder
            self.sortDescend=True
    
    def getScenarioFileNames(self):
        if self.wFiles.value == 'historical':
            self.procDataFile= 'InputData/CathFlatEPFlatShiftsJuly2015.csv'
            self.shiftDataFile = 'InputData/ShiftsFlatFlatJuly2015.csv'
        elif self.wFiles.value == 'two additional high-volume EP providers':
            self.procDataFile= 'InputData/CathFlatEPGrow2ShiftsJuly2015.csv'
            self.shiftDataFile = 'InputData/ShiftsFlatGrow2July2015.csv'
        elif self.wFiles.value == 'CATH lab only':
            self.procDataFile= 'InputData/CathOnlyShiftsJuly2015.csv'
            self.shiftDataFile = 'InputData/ShiftsCathOnlyJuly2015.csv'            
        elif self.wFiles.value == 'test':
            self.procDataFile= 'InputData/TestProcs.csv'
            self.shiftDataFile = 'InputData/TestShifts.csv'               
        else: #default to historical if nothing selected (impossible)
            self.procDataFile= 'InputData/CathFlatEPFlatShiftsJuly2015.csv'
            self.shiftDataFile = 'InputData/ShiftsFlatFlatJuly2015.csv'

    