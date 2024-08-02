import logging 
import random
import hashlib
import numpy as np
logger = logging.getLogger(__name__)

class Item:
    def __init__(self, key=None, value=None):
        self.key=key
        self.value=value

class Bucket:
    def __init__(self, key=None, value=None):
        self.key=key
        self.value=value
    
    def __str__(self):
        return f'[{self.key},{self.value}]'
    
    def add(self, item):
        if self.key == None: 
            self.key=item.key
            self.value=item.value
            logger.info('Insert to a empty bucket')
        elif self.key == item.key:
            self.value=self.value+item.value
            # print('Increase a exists bucket')
            logger.info('Increase a exists bucket')
        else:
            raise ValueError(f'{self.key}!={item.key}')
    
    def replace(self,item):
        # if item.value > self.value:
        #     self.key=item.key
        #     self.value=item.value
        #     return True
        # else:
        #     return False
        rnd=random.random()
        P = 0
        if self.value == 0:
            P=1
        else:
            P = abs(item.value)/(abs(self.value)+abs(item.value))
            # P = abs(item.value)/(abs(self.value)+abs(item.value))
        if rnd < P:
            logger.info(f'[{self.key},{self.value}] is replaced by [{item.key},{item.value}({self.value+item.value})] with P={rnd}')
            # print(f'[{self.key},{self.value}] is replaced by [{item.key},{item.value}({self.value+item.value})] with P={rnd}')
            replaced_item=Item(self.key,self.value)
            self.key=item.key
            # self.value=self.value+item.value
            self.value=self.value+item.value
            return replaced_item
        else:
            logger.info('Insert fail')
            return None
    
    def replace_insert(self,item):
        if abs(self.value)<abs(item.value):
            self.key=item.key
            self.value=item.value
            
        



class Sketch:
    def __init__(self,size,row_numbers): 
        self.size=size
        self.r=row_numbers
        # 8 bytes: 4 byte for key and 4 byte for value
        self.c=int(self.size/8/self.r)
        self.sketch=[[Bucket() for _ in range(self.c)] for _ in range(self.r)]
        print(f'init sketch {self.r}x{self.c}')
    

    def hash_to_column(self, key, idx):
        """
        Calculate a hash value based on key and idx, and map it to a column in range 0 to c-1.

        Parameters:
        key (str): The key to be hashed.
        idx (int): The index to be hashed.
        c (int): The number of columns.

        Returns:
        int: A positive integer in the range 0 to c-1.
        """
        # Combine the key and idx to create a unique input
        combined = f"{key}_{idx}"
        
        # Calculate the MD5 hash value
        hash_object = hashlib.md5(combined.encode())
        hash_hex = hash_object.hexdigest()
        
        # Convert the hash value to an integer
        hash_int = int(hash_hex, 16)
        
        # Map the hash value to the range 0 to c-1
        column = hash_int % self.c
        
        return column

    def hash_to_column2(self, key, idx):
        """
        Calculate a hash value based on key and idx, and map it to a column in range 0 to c-1.

        Parameters:
        key (str): The key to be hashed.
        idx (int): The index to be hashed.
        c (int): The number of columns.

        Returns:
        int: A positive integer in the range 0 to c-1.
        """
        # Combine the key and idx to create a unique input
        combined = f"{key}_{2*idx}"
        
        # Calculate the MD5 hash value
        hash_object = hashlib.md5(combined.encode())
        hash_hex = hash_object.hexdigest()
        
        # Convert the hash value to an integer
        hash_int = int(hash_hex, 16)
        
        # Map the hash value to the range 0 to c-1
        column = hash_int % self.c
        
        return column

    def getbucket(self,i,j):
        return self.sketch[i][j]
        
    def getminbucket(self,buckets_tuple):
        sorted_buckets_tuple=sorted(buckets_tuple,key=lambda x:x[2])
        return self.getbucket(sorted_buckets_tuple[0][0],sorted_buckets_tuple[0][1])


    def insert(self,item,cur_key):
        insert_flag=False
        buckets_tuple=[]
        # print(f'try to insert {item.key},{item.value}')
        for i in range(self.r):    
            j=self.hash_to_column(item.key,i)
            bucket=self.getbucket(i,j)
            buckets_tuple.append((i,j,bucket.value))
            if bucket.key == None or bucket.key == item.key: 
                bucket.add(item)
                logger.info(f'Insert to ({i},{j}) success!')
                insert_flag=True
                break
        if not insert_flag:
            bucket=self.getminbucket(buckets_tuple)
            result=bucket.replace(item)
            if result!=None:
                # reinsert
                candicate_bucket=[]
                candicate_replace_flag=False
                for i in range(self.r):
                    # another function
                    j=self.hash_to_column2(result.key,i)
                    bucket=self.getbucket(i,j)
                    if bucket.key == None:
                        bucket.add(result)
                        candicate_replace_flag=True
                        break
                    elif bucket.key < cur_key:
                        candicate_bucket.append((i,j,bucket.value))
                if (not candicate_replace_flag) and len(candicate_bucket)>0:
                    two_chance_bucket=self.getminbucket(candicate_bucket)
                    two_chance_bucket.replace_insert(item)
                
                logger.info('Replace success!')
            else:
                logger.info('Insert fail')
    
    # def query(self):
    #     keys=set()
    #     for i in range(self.r):
    #         for j in range(self.c):
    #             keys.add(self.getbucket(i,j).key)
    #     return keys

    def query(self):
        keys_and_values = []
        for i in range(self.r):
            for j in range(self.c):
                bucket = self.getbucket(i, j)
                if bucket.key!=None:
                    keys_and_values.append((bucket.key, bucket.value))
        return keys_and_values
        
        # # sorted by values
        # keys_and_values.sort(key=lambda x: x[1], reverse=True)

        # # get topk
        # topk_keys = set()
        # for kv in keys_and_values[:k]:
        #     topk_keys.add(kv[0])
        
        # return topk_keys
    
    def printsketch(self):
        for i in range(self.r):
            for j in range(self.c):
                print(self.getbucket(i,j))
    


class Worker:
    def __init__(self,path):
        self.values=np.load(path).flatten()
        self.cur=0
        self.key=0
        self.end=len(self.values)
        self.stepsize=1000
    
    def get_gradients(self,size):
        cur_end=min(self.end,self.cur+size)
        result=self.values[self.cur:cur_end]
        self.cur=cur_end
        return result

    def genkey(self):
        return_result=self.key
        self.key+=1
        return return_result


def gettopkindexfromworkers(workers,topk):
    combined_array = np.sum([workers[i].values for i in range(len(workers))],axis=0)  
    print(f'total number is {len(combined_array)}')
    # k=int(len(combined_array)*0.01)
    k=topk
    topk_indices = np.argpartition(np.abs(combined_array), -k)[-k:]
    # topk_indices = np.argpartition(combined_array, -k)[-k:]
    return topk_indices

