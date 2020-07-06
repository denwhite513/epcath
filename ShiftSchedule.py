'''
Adapted from @nicseo code 11/20/14

Last Modified: 7/5/2020

@author: cindiewu
'''

from Schedule import *
from Utilities import *

cathID = 0.0
epID = 1.0
middleID = 2.0
fullShiftID = 1
halfShiftID = 0.5
quarterShiftID = 0.25
labStartTime = (8,0)


def test():
    s = ShiftSchedule(2,2,(13,0))
    s.placeProvider(1.0,0,"A",0.5,1.0,1.0)
    s.placeProvider(1.0,0,"B",0.5,2.0,1.0)
    
    s.placeProvider(0.0,0,"C",0.5,2.0,0.0)
    s.placeProvider(0.0,0,"D",0.5,2.0,0.0)
    return s

class ShiftSchedule():
    '''
    Each ShiftSchedule object belongs to a given day
    '''

    def __init__(self,numCathRooms,numEPRooms,secondShiftStart):
        cathRooms = {(cathID,room):[] for room in range(numCathRooms)}
        epRooms = {(epID,room):[] for room in range(numEPRooms)}
        self.rooms = dict(cathRooms.items()+epRooms.items())
        self.numCathRooms = numCathRooms
        self.numEPRooms = numEPRooms
        self.numRooms = {cathID: numCathRooms, epID:numEPRooms}
        self.secondShiftStart = secondShiftStart
        
        cathStarts = {(cathID,room):labStartTime for room in range(numCathRooms)}
        epStarts = {(epID,room):labStartTime for room in range(numEPRooms)}
        self.nextShiftStartTimes = dict(cathStarts.items()+epStarts.items())

    def findEarliestRoom(self,lab):
        '''
        Determines the room that has the earliest end time in actual shift time length.
        Input: the lab to query
        Returns: (lab,room) of the room whose total shifts end earliest
        '''
        earliestTime = (24,0)
        earliestRoom = (None,None)

        if lab == cathID:
            for c in range(self.numCathRooms):
                end = self.lastShiftEndTime(cathID,c)
                if isEarlier(end,earliestTime):
                    earliestTime = end
                    earliestRoom = (cathID,c)
        else:
            for e in range(self.numEPRooms):
                end = self.lastShiftEndTime(epID,e)
                if isEarlier(end,earliestTime):
                    earliestTime = end
                    earliestRoom = (epID,e)
        return earliestRoom
            
        
    def lastShiftEndTime(self,lab,room):
        '''
        Get the time the historical time of the last shift in the room ends.
        Input: lab, room to query
        Returns: the end time for the last shift in the room
        '''
            
        shifts = self.rooms[(lab,room)]

        # special case: first shift is half day but ends early
        firstShift = shifts[0]
        isHalf = True if firstShift[1]==halfShiftID else False
        firstEnd = add(labStartTime,timeFormattedFromHours(firstShift[2]))
        endsEarly = isEarlier(firstEnd,self.secondShiftStart)
        if isHalf and endsEarly and lab==cathID:
            end = self.secondShiftStart
            for shift in shifts[1:]:
                end = add(end,timeFormattedFromHours(shift[2]))
            return end
        
        # otherwise, simply add shift lengths up
        end = labStartTime
        for shift in shifts:
            end = add(end,timeFormattedFromHours(shift[2]))
        return end

        
    def isSecondHalfShift(self,provider):
        '''
        Determines whether or not a provider's shift is during the second half of
        the day.
        Input: provider (key to query)
        Returns: True, if there are 0.5 shifts before the provider's shift
                 False, otherwise
        '''
        assignment = self.getProviderRoomAssignment(provider)
        if assignment is None:
            return False
        return assignment[3]==halfShiftID
        
        
    def shiftsLeftInRoom(self,lab,room):
        '''
        Given a lab room, get the number of (or fraction of) FULL day shifts
        left in the day. For example, if a room has one half day, and one singleton
        scheduled, this would return 0.25.
        Input: lab,room to query
        Returns: the number of whole day shifts that are open to be scheduled
                 that day. For example, if the day is completely open,
                 this would return 1.0.
        '''
        shifts = self.rooms[(lab,room)]
        timeLeft = 1.0
        for shift in shifts:
            timeLeft -= shift[1]
        return timeLeft

    def numShiftsInRoom(self,lab,room):
        '''
        Get the number of shifts scheduled into a given lab room.
        Input: lab, room to query
        Returns: a tuple containing the number of full day, half day,
                 and single procedure shifts during that day
        '''

        shifts = self.rooms[(lab,room)]
        full, half, single = (0,0,0)
        for provider in shifts:
            shift = provider[1]
            if shift==fullShiftID:
                full += 1
            elif shift==halfShiftID:
                half += 1
            else:
                single += quarterShiftID
        return (full,half,single)


    def shiftsLeftInLab(self,lab):
        '''
        Given a lab, get the number of shifts open to be scheduled during this day.
        Input: lab to query (0.0=Cath, 1.0=EP)
        Returns: The number of (or fraction of) FULL day shifts open to be
                 scheduled.
        '''
        openShifts = 0.0
        if lab == cathID:        
          for c in range(self.numCathRooms):
            openShifts += self.shiftsLeftInRoom(lab,c)
        elif lab == epID:
          for e in range(self.numEPRooms):
            openShifts += self.shiftsLeftInRoom(lab,e)
        return openShifts
    
        
    def numShiftsInLab(self,lab):
        '''
        Given a lab, get the number of shifts scheduled into this day.
        Input: lab to query (0.0=Cath, 1.0=EP)
        Returns: a tuple containing the number of full day, half day,
                 and single procedure shifts during that day
        '''
        numShifts = (0.0,0.0,0.0)
        if lab == cathID:
            for c in range(self.numCathRooms):
                numShifts = [sum(x) for x in zip(numShifts, self.numShiftsInRoom(cathID,c))]
        elif lab == epID:
            for e in range(self.numEPRooms):
                numShifts = [sum(x) for x in zip(numShifts, self.numShiftsInRoom(epID,e))]
        return numShifts

    def numShiftsInDay(self):
        '''
        Get the number of shifts scheduled into this day.
        Input: None
        Returns: a tuple containing the number of full day, half day,
                 and single procedure shifts during that day
        '''
        numShifts = (0.0,0.0,0.0)
        for c in range(self.numCathRooms):
            numShifts = [sum(x) for x in zip(numShifts, self.numShiftsInRoom(cathID,c))]
        for e in range(self.numEPRooms):
            numShifts = [sum(x) for x in zip(numShifts, self.numShiftsInRoom(epID,e))]
        return numShifts

    def shiftsLeftInDay(self):
        '''
        Get the number of shifts open to scheduled during this day.
        Input: None
        Returns: The number of (or fraction of) FULL day shifts open to be
                 scheduled.
        '''     
        return self.shiftsLeftInLab(0.0) + self.shiftsLeftInLab(1.0) 

    def maxOpenRoomInLab(self, lab):
        '''
        Gives the maximum size shift for which time is available in a room in the lab in this day.
        Input: Lab
        Returns: The highest number of shifts that can fit into a room with fewer than 1 shifts scheduled.
        If all rooms are full, returns 0.
        '''
        maxOpen = 0
        for r in range(self.numRooms[lab]):
            if self.shiftsLeftInRoom(lab,r) > maxOpen:
                maxOpen = self.shiftsLeftInRoom(lab,r)
        return maxOpen


    def nextOpenRoomInLab(self, lab, ShiftLength):
        '''
        Gives the lowest number of a room with a shift of ShiftLength available.
        
        Input: Lab
        Returns: The lowest number of a room with fewer than 1 shifts scheduled in this day.
        If non of the rooms have this much time available, the function returns -1
        Note: If you call this function wihtout having checked that such a room rexists, it may throw -1     
        Note: Calling this function with ShiftLength = 0 will return the first room that is not full
        '''
        if lab == cathID:
            if self.shiftsLeftInLab(cathID) > 0:
                for c in range(self.numCathRooms):
                    if self.shiftsLeftInRoom(cathID,c) >= ShiftLength:
                        return c
        elif lab == epID:
            if self.shiftsLeftInLab(epID) > 0:
                for e in range(self.numEPRooms):
                    if self.shiftsLeftInRoom(epID,e) >= ShiftLength:
                        return e
        return -1




    def getProviderRoomAssignment(self,providerKey):
        '''
        Get the room that the provider is working in, their shift length, and the
        time of day their shift starts.
        Input: providerKey to query
        Returns: a tuple containing the
                    (lab,
                    room number,
                    shift length, and
                    the length of shifts scheduled BEFORE them)
                 For example, Cath physician 8 working a quarter day shift in room 3
                 after another provider's half day shift would return (0.0,8,0.25,0.5)
                 Returns None if the provider is not scheduled into the day.
        '''
        for c in range(self.numCathRooms):
            room = self.rooms[(cathID,c)]
            previousShifts = 0.0
            for shift in room:
                if shift[0]==providerKey:
                    return (cathID,c,shift[1],previousShifts)
                previousShifts += shift[1]
        for e in range(self.numEPRooms):
            room = self.rooms[(epID,e)]
            previousShifts = 0.0
            for shift in room:
                if shift[0]==providerKey:
                    return (epID,e,shift[1],previousShifts)
                previousShifts += shift[1]
        return None

    def getProvidersAndShiftsInRoom(self,lab,room):
        '''
        Given a lab room, get the provider keys and corresponding shift lengths
        scheduled into that room.
        Input: lab,room to query
        Returns: a list of tuples that contain the provider key and shift length
        '''
        return [x for x in self.rooms[(lab,room)]]

    def getProviderStartTime(self,lab,room,provider):
        shifts = self.rooms[(lab,room)]
        start = None
        for shift in shifts:
            if shift[0]==provider:
                start = shift[3]
        return start

    def placeProvider(self,lab,room,providerKey,shiftType,shiftLength,originalLab):
        '''
        Given a lab, room, provider (key), and their shift length,
        place the provider into the shift schedule. This assumes the
        shift fits into the room.
        Input:  lab (0.0 Cath or 1.0 EP),
                room (0 - number of Cath rooms or 0- number of EP rooms),
                provider key,
                shift type (0.25: one procedure only, 0.5: half day, 1.0: full day)
                historical shift length in hours
                start time of shift
        Return: None
        '''
        shifts = self.rooms[(lab,room)]
        shifts.append((providerKey,shiftType,shiftLength,self.nextShiftStartTimes[(lab,room)],originalLab))
        self.updateNextShiftStart(lab,room,shiftLength)

    def updateNextShiftStart(self,lab,room,shiftLength):
        shiftStart = self.nextShiftStartTimes[(lab,room)]
        shiftLength =  timeFormattedFromHours(shiftLength)
        newTime = add(shiftStart,shiftLength)
        self.nextShiftStartTimes[(lab,room)] = self.secondShiftStart if isEarlier(newTime,self.secondShiftStart) and lab==cathID else newTime

        

