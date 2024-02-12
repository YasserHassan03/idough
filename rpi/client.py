import requests as r
import time


def main(): 
    url = "https://ec2-34-207-250-127.compute-1.amazonaws.com:5000/"
    
    while True:

        res = r.get(url+'/predict', verify=False)
        
        print(res.json())

        time.sleep(3)




if __name__ == "__main__":
    main()
