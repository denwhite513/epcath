'''
Adapted from @nicseo code 11/20/14

Last Modified: 7/5/2020

@author: cindiewu
'''

import math
from ShiftSchedule import *
from Utilities import *

##################################### HELPER METHODS #####################################

def test():
    s = Schedule(15)
    s.scheduleProcedure(120,(8,0))
    return s


##################################### SCHEDULE CLASS #####################################


class Schedule():

    def __init__(self,minuteRes,labStart,labEnd):
        '''
        Each Schedule object belongs to a given room day. There should only be one procedure at a given time.
        '''
        self.binsPerHour = 60.0/minuteRes
        self.fractionPerHour = minuteRes/60.0
        self.minuteRes = minuteRes
        self.timeSlots = {timeFormattedFromMinutes(m*self.minuteRes):[] for m in range(int(self.binsPerHour*24))}

        self.labStartTime = labStart
        self.labEndTime = labEnd

        # summary stat counters
        self.primeTimeMinutes = 0
        self.overflowMinutes = 0

    def getTotalPrimeTimeMinutes(self):
        '''
        Get the room day's total procedure minutes overall.
        
        Input: None
        Returns: total procedure minutes scheduled
        '''
        return self.primeTimeMinutes
        

    def roundBinUp(self,time):
        '''
        Given a time, round the time to the next bin up. For example, if the time is (8,29) with
        15 minute bins, this will return (8,30).
        Input: time (in the form (hours,minutes) to round)
        Returns: the rounded time tuple
        '''
        hours = time[0]
        minutes = time[1]
        minutesRounded = self.minuteRes*math.ceil(minutes/float(self.minuteRes))
        if minutesRounded == 60.0:
            return (hours+1,0)
        return (hours,int(minutesRounded))

    def roundBinDown(self,time):
        '''
        Given a time, round the time to the next bin down. For example, if the time is (8,20) with
        15 minute bins, this will return (8,15).
        Input: time (in the form (hours,minutes) to round)
        Returns: the rounded time tuple
        '''
        hours = time[0]
        minutes = time[1]
        minutesRounded = self.minuteRes*math.floor(minutes/float(self.minuteRes))
        if minutesRounded == 60.0:
            return (hours+1,0)
        return (hours,int(minutesRounded))

    ##################################### SCHEDULING METHODS #####################################

    def getProcedureAtTime(self,time):
        '''
        Get the procedure that is scheduled during the given time slot.
        Input:  time slot to query is a tuple in the form (hours,minutes)
                where (0,0) corresponds to 12 AM and (24,0) corresponds to 12 PM
        Returns: the procedure scheduled or None if there is no scheduled procedure
        '''
        return self.timeSlots[time]

    def getNextOpenTimeSlot(self,startTime):
        '''
        Get the next open time slot after the specified start time.
        Input:  startTime (a tuple in the form (hours,minutes) to specify when to start
                looking for an open slot. For example, if you specify (8,0), this will
                return the next time slot open after 8 AM)
        Returns: a tuple in the form (hours,minutes) denoting the next open time slot
                 or None if there is no open time slot for the rest of the day
        
        '''
        potentialSlots = [x for x in self.timeSlots.keys()
                          if x[0]>=startTime[0] and x[1]>=startTime[1]]
        potentialSlots.sort(key=lambda x:minutesFromTimeFormatted(x))
        for slot in potentialSlots:
            if len(self.timeSlots[slot]) == 0:
                return slot
        return (24,0)
        
    def scheduleProcedure(self,procedure,procTime,startTime):
        '''
        Schedules the given procedure at the next open time slot after a given start time.
        Input:  procedure to be scheduled,
                procTime (in minutes),
                startTime (time to start scheduling after in the form (hour,minute))
        Returns: None
        '''
        procTime = int(procTime)
        nextOpen = self.getNextOpenTimeSlot(startTime)
        procTimeFormatted = timeFormattedFromMinutes(procTime)
        
        procStart = nextOpen
        procEnd = timeFormattedFromMinutes((nextOpen[0]+procTimeFormatted[0])*60+nextOpen[1]+procTimeFormatted[1])
        procEnd = self.roundBinUp(procEnd)
        procDuration = timeFormattedFromMinutes((procEnd[0]-procStart[0])*60+procEnd[1]-procStart[1])
        numBins = int((procDuration[0]*self.binsPerHour) + (procDuration[1]/self.minuteRes))

        minutes = minutesFromTimeFormatted(procStart)-self.minuteRes
        for b in range(numBins):
            minutes += self.minuteRes
            currentBin = timeFormattedFromMinutes(minutes)
            if currentBin == (24,0):
                break
            if currentBin in self.timeSlots: #Cindie Edit/Check this
                self.timeSlots[currentBin].append(procedure)

        # procedure completely during prime time
        
        if isEarlier(procEnd,self.labEndTime):
            self.primeTimeMinutes += procTime
        else:
            self.overflowMinutes += procTime
        
        #print procStart,procEnd,numBins
        
