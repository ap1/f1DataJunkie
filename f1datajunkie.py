import timingSheetAnalysis as tsa
import tur2011_data as data
import json, csv

carData=tsa.initEnhancedHistoryDataByCar(data.history)

def stopTimeToLapByCar(carData,lap):
	stopData=carData
	stopTimeToLap=0
	for stop in stopData:
		if (lap > stop["lap"]):
			stopTimeToLap=stop["totalStopTime"]
		else: break
	return stopTimeToLap


#augment the history data
for carNum in carData:

	# add in pitstop data
	carData[carNum]['stops']=tsa.stopsAnalysis(data.stops,carNum)
	carData[carNum]['stoppingLaps']=[]
	for stop in carData[carNum]['stops']:
		carData[carNum]['stoppingLaps'].append(stop['lap'])
	print carData[carNum]['stoppingLaps']
	print carData[carNum]['stops']
	carData[carNum]["stopCorrectedLapTimes"]=[]
	
	# add in race position data
	carData[carNum]['positions']=[]

	for lap in data.chart:
		if carNum in lap:
			carData[carNum]['positions'].append(lap.index(carNum))
	print carData[carNum]['positions']

	carData[carNum]['timeToPosInFront']=[]
	carData[carNum]['timeToPosBehind']=[]
	
	for lap in data.chart[1:]:
		lapCount=int(lap[0].split()[1])
		if carNum in lap:
			# add in time to cars in positions one ahead and one behind
			carPos=lap.index(carNum)
			currentElapsedTime=carData[carNum]["calcElapsedTimes"][lapCount-1]
			if carPos==1:
				carBehindNum=tsa.posByCarLap(data.chart,lapCount,carPos+1)
				carBehindElapsedTime=carData[carBehindNum]["calcElapsedTimes"][lapCount-1]
				carData[carNum]['timeToPosInFront'].append(0)
				carData[carNum]['timeToPosBehind'].append(tsa.formatTime(carBehindElapsedTime-currentElapsedTime))
			elif carPos==len(lap)-1:
				carInFrontNum=tsa.posByCarLap(data.chart,lapCount,carPos-1)
				carInFrontElapsedTime=carData[carInFrontNum]["calcElapsedTimes"][lapCount-1]
				carData[carNum]['timeToPosInFront'].append(tsa.formatTime(currentElapsedTime-carInFrontElapsedTime))
				carData[carNum]['timeToPosBehind'].append(0)
			else:
				carInFrontNum=tsa.posByCarLap(data.chart,lapCount,carPos-1)
				carInFrontElapsedTime=carData[carInFrontNum]["calcElapsedTimes"][lapCount-1]
				carData[carNum]['timeToPosInFront'].append(tsa.formatTime(currentElapsedTime-carInFrontElapsedTime))
				carBehindNum=tsa.posByCarLap(data.chart,lapCount,carPos+1)
				carBehindElapsedTime=carData[carBehindNum]["calcElapsedTimes"][lapCount-1]
				carData[carNum]['timeToPosBehind'].append(tsa.formatTime(carBehindElapsedTime-currentElapsedTime))

	print carNum,carData[carNum]['timeToPosInFront']
	print carNum,carData[carNum]['timeToPosBehind']
	
	
	#experimental - is stop corrected laptime useful?
	lapCount=1
	offset=0
	for lapTime in carData[carNum]["lapTimes"]:
		carData[carNum]["stopCorrectedLapTimes"].append(tsa.formatTime(lapTime-offset))
		if lapCount in carData[carNum]['stoppingLaps']:
			print "stopping lap"
			stop=carData[carNum]['stoppingLaps'].index(lapCount)
			offset=carData[carNum]['stops'][stop]["stopTime"]
		else:
			offset=0
		lapCount=lapCount+1
	#print carData[carNum]["stopCorrectedLapTimes"]

for carNum in carData:
	carData[carNum]['tyres']=data.tyres[carNum]

#need to do a race stats routine	
maxLaps=int(data.chart[-1][0].split()[1])

race='tur_2011'

def output_battlemapAndProximity(carData):
	f=open('../generatedFiles/'+race+'_battlemap.js','wb')
	fdt=[]

	f2=open('../generatedFiles/'+race+'proximity.csv','wb')
	writer = csv.writer(f2)
	writer.writerow(["lap","car","pos","timeToPosInFront","timeToPosBehind","timeToTrackInFront","timeToTrackBehind","pitstop"])

	#for d in ['1','2','3','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19','20','21','22','23','24','25']:
	for carNum in ['1','2','3','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19','20','21','22','23','24','25']:
		fdd=[]
		for lap in range(1,maxLaps+1):
			fdl={}
			fdl['lap']=lap
			if carNum in carData and lap<=len(carData[carNum]["lapTimes"]):
				fdl['ttf']=carData[carNum]['timeToPosInFront'][lap-1]
				fdl['ttb']=carData[carNum]['timeToPosBehind'][lap-1]
				car=carData[carNum]
				proximity=[lap, carNum,tsa.posOfCarNumAtCarLap(data.chart,lap,carNum),car['timeToPosInFront'][lap-1],-car['timeToPosBehind'][lap-1],car['timeToTrackCarInFront'][lap-1]]
				if len(car['timeToTrackCarBehind'])>=lap:
					proximity.append(-car['timeToTrackCarBehind'][lap-1])
				else: proximity.append(0)
				if lap in carData[carNum]['stoppingLaps']: proximity.append(1)
				else: proximity.append(0)
				writer.writerow(proximity)
			else:
				fdl['ttf']=0
				fdl['ttb']=0
			fdd.append(fdl)
		
		fdt.append(fdd)
	#json.dump(fdt,f)
	f.write('var battleTimes='+json.dumps(fdt))
	f.close()

def output_elapsedTime(carData):
	f3=open('../generatedFiles/'+race+'elapsedtimes.csv','wb')
	writer2 = csv.writer(f3)
	writer2.writerow(['lap','VET','WEB','HAM','BUT','ALO','MAS','SCH','ROS','HEI','PET','BAR','MAL','SUT','RES','KOB','PER','BUE','ALG','TRU','KOV','KAR','LIU','GLO','AMB'])
	for lap in range(1,maxLaps+1):
		elt=[lap]
		for carNum in ['1','2','3','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19','20','21','22','23','24','25']:
			if carNum in carData and lap<=len(carData[carNum]["calcElapsedTimes"]):
				elt.append(carData[carNum]["calcElapsedTimes"][lap-1])
			else: elt.append('')
		writer2.writerow(elt)
		
def output_raceHistoryChart(data,carData):
	#race history chart
	f=open('../generatedFiles/'+race+'demoHistory.csv','wb')
	writer = csv.writer(f)
	writer.writerow(["lap","car","calcElapsedTime","calcTimeToLeader","carlapAsRaceLap"])
	winnerNum=data.history[-1][1][0]
	winnerAvLapTime=carData[winnerNum]["avLapTime"]
	tenthPlacedAvLapTime=carData["16"]["avLapTime"]
	print "Winner",winnerNum,"AvLap",winnerAvLapTime,tenthPlacedAvLapTime
	for carNum in carData:
		print carNum,carData[carNum]["avLapTime"]
		for lap in range(0,len(carData[carNum]["calcElapsedTimes"])):
			#writer.writerow([lap+1,carNum,carData[carNum]["calcElapsedTimes"][lap],carData[carNum]["calcTimeToLeader"][lap],f1dj.formatTime((tenthPlacedAvLapTime*(lap+1))-carData[carNum]["calcElapsedTimes"][lap])])
			writer.writerow([lap+1,carNum,carData[carNum]["calcElapsedTimes"][lap],carData[carNum]["calcTimeToLeader"][lap],carData[carNum]["carlapAsRacelap"][lap]])

def output_stintLapTimes(carData):
	f=open('../generatedFiles/'+race+'stintLapTimes.csv','wb')
	writer = csv.writer(f)
	writer.writerow(["stint","lap","car","lapTime","fuelCorrectedLaptime","calcElapsedTime","calcTimeToLeader"])
	for carNum in carData:
		prevLapTime=0
		stint=1
		for lap in range(0,len(carData[carNum]["calcElapsedTimes"])):
			rows=[]
			#this is a huge kludge; identify stint by stops
			#print carData[carNum]["lapTimes"][lap], prevLapTime,prevLapTime-12.0
			#if carData[carNum]["lapTimes"][lap] > (prevLapTime-12.0):
			if lap not in carData[carNum]['stoppingLaps']:
				rows.append([stint,lap+1,carNum,carData[carNum]["lapTimes"][lap],carData[carNum]["fuelCorrectedLapTimes"][lap],carData[carNum]["calcElapsedTimes"][lap],carData[carNum]["calcTimeToLeader"][lap]])
			else:
				writer.writerows(rows)
				stint=stint+1
				print "new stint", stint,lap+1,carNum
				rows=[[stint,lap+1,carNum,carData[carNum]["lapTimes"][lap],carData[carNum]["fuelCorrectedLapTimes"][lap],carData[carNum]["calcElapsedTimes"][lap],carData[carNum]["calcTimeToLeader"][lap]]]
			prevLapTime=carData[carNum]["lapTimes"][lap]
			writer.writerows(rows)


#output and quali outputs
def startTimeInSeconds(clockTime):
  t=clockTime.split(':')
  return 3600*int(t[0])+60*int(t[1])+int(t[2])

def output_practiceAndQuali(sessiondata,sessionName):
	driverQuali={}
	sectors={}
	sep=','
	
	fname=sessionName
	timing=sessiondata
	f=open('../generatedFiles/'+race+fname+'.csv','wb')
	writer = csv.writer(f)
	earlyStart='99:99:99'
	for driver in timing:
		driverNum= str(driver[0])
		if len(driver)>2:
			if earlyStart>driver[3]: earlyStart=driver[3]
	earlyStartTime=startTimeInSeconds(earlyStart)
	for driver in timing:
		driverNum= str(driver[0])
		if len(driver)>2:
			clockTime=driver[3]
		else:
			clockTime='0:0:0'
		driverQuali[driverNum]={'times':[],'driverName':driver[1],'driverNum':driverNum, 'startTime':'','clockStartTime':clockTime}
		dsTime=startTimeInSeconds(driverQuali[driverNum]['clockStartTime'])
		driverQuali[driverNum]['startTime']= "%.1f" % (dsTime-earlyStartTime)
		driverQuali[driverNum]['times'].append({'time':driverQuali[driverNum]['startTime'],'elapsed':driverQuali[driverNum]['startTime']})
		for pair in tsa.pairs(driver[4:]):
			t=pair[1].split(':')
			tm=60*int(t[0])+float(t[1])
			timing={'time':"%.3f" % tm, 'elapsed':"%.3f" %( float(driverQuali[driverNum]['times'][-1]['elapsed'])+tm)}
			driverQuali[driverNum]['times'].append(timing)

	print driverQuali

	#header=sep.join(['Name','DriverNum','Lap','Time','Elapsed'])
	writer.writerow(['Name','DriverNum','Lap','Time','Elapsed'])
	#f.write(header+'\n')
	for driver in driverQuali:
		lc=1
		core=[driverQuali[driver]['driverName'],driverQuali[driver]['driverNum']]
		for lap in driverQuali[driver]['times']:
			txt=[]
			for c in core: txt.append(c)
			txt.append(str(lc))
			txt.append(lap['time'])
			txt.append(lap['elapsed'])
			lc=lc+1
			#f.write(sep.join(txt)+'\n')
			writer.writerow(txt)
	f.close()

	f=open('../generatedFiles/'+race+fname+'.js','wb')
	#txt='var data=['
	txt=[]
	for driver in ['1','2','3','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19','20','21','22','23','24','25']:
		#txt=txt+'['
		txt.append([])
		for lap in driverQuali[driver]['times']:
			txt[-1].append(float(lap['time']))
			#txt=txt+lap['time']+','
		#txt=txt.rstrip(',')+'], '
	#txt=txt.rstrip(',')+'];'
	print txt
	f.write('var data=['+','.join(map(str, txt))+'];')
	f.close()
#-----




output_battlemapAndProximity(carData)
output_elapsedTime(carData)
output_raceHistoryChart(data,carData)
output_stintLapTimes(carData)
output_practiceAndQuali(data.fp1times,"p1")
output_practiceAndQuali(data.fp2times,"p2")
output_practiceAndQuali(data.fp3times,"p3")
output_practiceAndQuali(data.qualitimes,"quali")