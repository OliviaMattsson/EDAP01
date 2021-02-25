Monte Carlo Localizaion:
- Less memory needed
- Can represent multi-modal distributions and can globally localize a robot. Markov, that we used, cannot since it is based on Kalman filtering. 
- More accurate
- Easy to implement.

Monte Carlo calculates the probability for each position. At start, when nothing is known, the distribution is even since the uncertainty is high. As the robot moves between positions, the distribution model is refined. 




Observation (sensor model):
- getNrOfReadings
- getOri (prob of producing the reading in state i)
- getOr (get whole vector with prob for producing reading, None if no reading)
- getOrXY (prob for rX,rY when in position x,y)

State model:
// To change robot values to observation model and vice versa
- robotStateToXYH 
- xyhToRobotState
- robotStateToXY
- sensorStateToXY
- xyToSensorState
- robotStateToSensorState
- getDimensions

Transition model:
- getNrOfStates 
- getTij (probability of go from state i to j)
- getTxyhToXYH (probability of going from xyh to XYH)
- getT (gets the matrix)
- getT_transp (transposed matrix)
