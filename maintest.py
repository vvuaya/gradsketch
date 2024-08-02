from sketch import Bucket
from sketch import Item
from sketch import Sketch
from sketch import Worker
from sketch import gettopkindexfromworkers
import numpy as np
import logging 

def test1():
    logging.basicConfig(level=logging.INFO)
    item=Item(13,11)      
    bucket=Bucket()  
    bucket.insert(item)
    bucket=Bucket(13,100)  
    bucket.insert(item)
    bucket=Bucket(12,100)  
    bucket.insert(item)
    bucket=Bucket(12,1)  
    bucket.insert(item)     

def testgetminbucket():
    sketch=Sketch(1*1024,1)
    data=[(1,2,Bucket(13,1000).value),(2,5,Bucket(14,200).value),(3,1,Bucket(15,550).value)]
    print(data)
    sketch.getbucket(data)

def testhash():
    sketch=Sketch(1*1024,1)
    for i in [100,200,300,400]:
        for j in range(3):
            print(sketch.hash_to_column(i,j))

def testsketch():
    logging.basicConfig(level=logging.INFO)
    sketch=Sketch(32,4)
    sketch.printsketch()
    item=Item(1,14)
    sketch.insert(item)
    sketch.printsketch()
    item=Item(2,12)
    sketch.insert(item)
    sketch.printsketch()
    item=Item(3,13)
    sketch.insert(item)
    sketch.printsketch()
    item=Item(4,14)
    sketch.insert(item)
    sketch.printsketch()
    item=Item(5,15)
    sketch.insert(item)
    sketch.printsketch()
        
def main():
    item=Item(13,11)
    bucket=Bucket()
    bucket.insert(item)
    print(bucket)

def testwork():
    worker=Worker('./gradients/0_0_grad.npy')
    cnt=0
    while True:
        gradients=worker.get_gradients(100)
        # print(len(gradients))
        cnt+=len(gradients)
        if len(gradients)==0:
            break
    print(cnt)


class TwoSketch:
    def __init__(self,size,row_numbers):
        self.size=int(size/2)
        self.r=row_numbers
        self.positive_sketch=Sketch(self.size,self.r)
        self.negative_sketch=Sketch(self.size,self.r)
    
    def insert(self,item,cur_key=0):
        if item.value>=0:
            self.positive_sketch.insert(item,cur_key)
        else:
            self.negative_sketch.insert(item,cur_key)
    
    def query(self, k):
        
        keys_and_values_in_positive=self.positive_sketch.query()
        keys_and_values_in_negative=self.negative_sketch.query()
        combined_values = {}
        # get the sum before qeurying
        for (key, value) in keys_and_values_in_positive:
            if key in combined_values:
                combined_values[key] += value
            else:
                combined_values[key] = value
        for (key, value) in keys_and_values_in_negative:
            if key in combined_values:
                combined_values[key] += value
            else:
                combined_values[key] = value

        # get topk gradient
        sorted_keys = sorted(combined_values, key=lambda x: abs(combined_values[x]), reverse=True)[:k]
        result_set = set(sorted_keys)
        return result_set

        
        # keys_in_positive=self.positive_sketch.query(min(self.size,k))
        # keys_in_negative=self.negative_sketch.query(min(self.size,k))
        # return keys_in_positive | keys_in_negative

def testTwoSketch():
    sketch=TwoSketch(192000*2,2)
    
    worker=Worker('./gradients/0_0_grad.npy')
    k=int(len(worker.values)*0.001)
    true_topk = gettopkindexfromworkers([worker],k)
    print(f'Topk is {len(true_topk)}')
    
    cnt=0
    while True:
        gradients=worker.get_gradients(25600)
        if len(gradients)==0:
            break
        else:
            for i in gradients:
                item=Item(cnt,i)
                sketch.insert(item)
                cnt=cnt+1
        # print(cnt)
    sketch_result = sketch.query(k)
    sketch_result_array = np.array(list(sketch_result))
    # print(f'there are {len(sketch_result_array)} items in sketch')
    # query_topk = gettopkindex(sketch_result_array,k)
    
    query_topk=sketch_result_array
    intersection = np.intersect1d(query_topk, true_topk)
    print(f'F1/Recall/Precision为{len(intersection)/len(true_topk)}')
    

def expmultipleworkers():
    sketch=TwoSketch(192000*8,2)
    worker_num=3
    workers = []
    for i in range(worker_num):
        workers.append(Worker(f'./gradients/0_{i}_grad.npy'))
    k=int(len(workers[0].values)*0.001)
    true_topk = gettopkindexfromworkers(workers,k)
    print(f'There are {len(true_topk)} Top-k items')
    
    
    cnt=0
    while True:
        for i in range(len(workers)):
            gradients=workers[i].get_gradients(25600)
            for j in gradients:
                item=Item(workers[i].genkey(),j)
                sketch.insert(item,workers[i].cur-25600)
                cnt=cnt+1
        # print(cnt)
        if cnt == len(workers[0].values)*len(workers):
            break
        
    sketch_result = sketch.query(k)
    sketch_result_array = np.array(list(sketch_result))
    # query_topk = gettopkindex(sketch_result_array,k)
    
    query_topk=sketch_result_array
    intersection = np.intersect1d(query_topk, true_topk)
    print(f'F1/Recall/Precision is {len(intersection)/len(true_topk)}')
    

def expmultipleworkers2():
    sketch=TwoSketch(200,4)
    worker_num=2
    workers = []
    for i in range(worker_num):
        workers.append(Worker(f'./gradients/0_{i}_grad.npy'))
    k=int(len(workers[0].values)*0.01)
    true_topk = gettopkindexfromworkers(workers,k)
    print(f'There are {len(true_topk)} Top-k items')
    
    
    cnt=0
    while True:
        for i in range(len(workers)):
            gradients=workers[i].get_gradients(25600)
            for j in gradients:
                item=Item(workers[i].genkey(),j)
                sketch.insert(item,workers[i].cur-25600)
                cnt=cnt+1
        print(cnt)
        if cnt == 100*5*worker_num:
        # if cnt == len(workers[0].values)*len(workers):
            break
        
    sketch_result = sketch.query(k)
    sketch_result_array = np.array(list(sketch_result))
    # query_topk = gettopkindex(sketch_result_array,k)
    
    query_topk=sketch_result_array
    intersection = np.intersect1d(query_topk, true_topk)
    print(f'F1/Recall/Precision is {len(intersection)/len(true_topk)}')

if __name__ =='__main__':
    expmultipleworkers()