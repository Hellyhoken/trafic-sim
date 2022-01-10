from random import random, randint
import pygame as pg

pg.init()

size = width, height = 1200, 300

screen = pg.display.set_mode(size)

class Car:
  def __init__(self, lane,vel,pos):
    self.identity = "car"
    self.prevlane = lane
    self.lane = lane
    self.lanecool = 25
    self.pos = pos
    self.vel = vel
    self.maxvel = 3
    self.color = (randint(0,255),randint(50,255),randint(0,255))

  def loop(self):
    self.acc()
    self.human()
    self.drive()
  
  def acc(self):
    if self.vel < self.maxvel:
      self.vel += 0.1
  
  def brake(self, front):
    if self.vel >= (front.pos - (self.pos + 8)):
      self.vel = (front.pos - (self.pos + 8)) - 0.1
    if self.vel < 0:
        self.vel = 0

  def human(self):
    if random() < 0.3:
      self.vel -= 0.15

  def drive(self):
    self.pos += self.vel

  def lane_swap_obstacle(self, front, lanes):
    if front.identity == "obs":
      front_other_lane = get_front_other_lane(self, get_adj_lanes(self.lane, lanes),lanes)
      if front_other_lane.pos > self.pos + 8 and (front_other_lane.pos-self.pos)*2 > front.pos-self.pos:
        lanes[front_other_lane.lane].append(self)
        lanes[self.lane].remove(self)
        self.lane = front_other_lane.lane
        self.lanecool = 25
        return True
    return False

  def lane_swap_car(self, front, lanes):
    front_other_lane = get_front_other_lane(self, get_adj_lanes(self.lane, lanes),lanes)
    dist_good_swap = front.pos - self.pos < front_other_lane.pos - self.pos
    if self.vel + 6 >= front.pos - self.pos and dist_good_swap:
      lanes[front_other_lane.lane].append(self)
      lanes[self.lane].remove(self)
      self.lane = front_other_lane.lane
      self.lanecool = 25

class Obstacle:
  def __init__(self, pos, lane):
    self.identity = "obs"
    self.pos = pos
    self.lane = lane

def get_adj_lanes(lane, lanes):
  if lane == 0:
    return [lanes[1]]
  if lane == 1:
    return [lanes[0],lanes[2]]
  if lane == 2:
    return [lanes[1]]

#find which car is in front in the lane with the most space
def get_front_other_lane(self, adj_lanes,lanes):
  x = 0
  fronts = []
  for i in adj_lanes:
    fronts.append(front_in_lane(self, i,lanes))
  if len(fronts) > 1:
    return max_dist(self, fronts)
  else:
    return fronts[0] 

#determine the index of the car in front
def front_in_lane(self, lane,lanes):
  x = 0
  while lane[x].pos < self.pos:
    x += 1
    if x == len(lane):
        return Car(lanes.index(lane),0,1200)
  return lane[x]

def max_dist(self, fronts):
  for i in fronts:
    if i.pos - self.pos < 0:
      return i
  if fronts[0].pos > fronts[1].pos:
    return fronts[0]
  else:
    return fronts[1]
   
def create_cars(amount):
  lst = []
  for i in range(amount):
    new_car = Car(i%3,3,0)
    lst.append(new_car)
  return lst

def create_obs():
  return Obstacle(700, 2)

def start_car(lanes,car_lst):
  if len(car_lst) > 0 and lanes[car_lst[-1].lane][0].pos > 8:
    car = car_lst.pop(0)
    lanes[car.lane].append(car)
  return lanes, car_lst

def stop_car(car,car_lst):
    car_lst.append(car)

def lane_loop(lanes, car_lst):
  for i in lanes:
    for j in i:
      if j.identity == "car":
       if i.index(j) != len(i)-1 and j.lanecool < 0:
           if j.lane_swap_obstacle(i[i.index(j)+1], lanes):
               continue
           j.lane_swap_car(i[i.index(j)+1], lanes)
       j.lanecool -= 1
  return lanes

def drive_loop(lanes, car_lst):
  for i in lanes:
    for j in i:
      if j.identity == "car":
       if i.index(j) != len(i)-1:
           j.brake(i[i.index(j)+1])
       j.loop()
       if j.pos > 1200:
           j.pos = 0
           stop_car(i.pop(i.index(j)), car_lst)
  return lanes

def bubble_sort(lanes):
    for i in lanes:
        done = False
        while not done:
            done = True
            for j in range(len(i)-1):
                if i[j].pos > i[j+1].pos:
                    done = False
                    i[j],i[j+1] = i[j+1],i[j]
    return lanes
        

def draw_loop(lanes):
    screen.fill((100,100,100))
    pg.draw.line(screen,(255,255,255),(0,100),(1200,100))
    pg.draw.line(screen,(255,255,255),(0,200),(1200,200))
    for i in lanes:
        for j in i:
            if j.identity == "car":
                pg.draw.rect(screen,j.color,pg.Rect(int(j.pos),int((j.lane + j.prevlane) / 2 * 100 + 48), 8,4))
                j.prevlane = j.lane
            else:
                pg.draw.rect(screen,(255,0,0),pg.Rect(int(j.pos),j.lane * 100 + 45, 10,10))
    pg.display.flip()

def main_loop(lanes, car_lst, restriction):
  lanes,car_lst = start_car(lanes, car_lst)
  j = 0
  while len(lanes[0]) > 0 or len(lanes[1]) > 0 or len(lanes[2]) > 1:
    if j % restriction == 0:
        lanes,car_lst = start_car(lanes, car_lst)
    for i in pg.event.get():
        if i.type == pg.QUIT:
            pg.display.quit()
            pg.quit()
    lanes = lane_loop(lanes, car_lst)
    lanes = bubble_sort(lanes)
    lanes = drive_loop(lanes, car_lst)
    draw_loop(lanes)
    j += 1
    pg.time.wait(10)

def main():
  car_lst = []
  lanes = [[],[],[]]
  cars = 300
  restriction = 1
  car_lst = create_cars(cars)
  obstacle = create_obs()
  lanes[obstacle.lane].append(obstacle)
  main_loop(lanes, car_lst, restriction)

main()
