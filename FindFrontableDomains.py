#!/usr/bin/python
# Run setup.sh first!

import alexa
import dns.resolver
from dns.resolver import Resolver
import threading
import Queue
import argparse
import sys
import random
from Sublist3r import sublist3r

class ThreadLookup(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):

        while True:
            if self.queue.empty():
                break
            #grabs host from queue
            hostname = self.queue.get()
            try:

                # Shake things up with some random DNS servers
                resolver = Resolver()
                dns =  ['209.244.0.3', '209.244.0.4','64.6.64.6','64.6.65.6', '8.8.8.8', '8.8.4.4','84.200.69.80', '84.200.70.40', '8.26.56.26', '8.20.247.20', '208.67.222.222', '208.67.220.220','199.85.126.10', '199.85.127.10', '81.218.119.11', '209.88.198.133', '195.46.39.39', '195.46.39.40', '96.90.175.167', '193.183.98.154','208.76.50.50', '208.76.51.51', '216.146.35.35', '216.146.36.36', '37.235.1.174', '37.235.1.177', '198.101.242.72', '23.253.163.53', '77.88.8.8', '77.88.8.1', '91.239.100.100', '89.233.43.71', '74.82.42.42', '109.69.8.51']
                random_dns_server = [ item.address for server in dns for item in resolver.query(server) ]
                # a resolver using dreamhost dns server
                random_dns = Resolver()
                random_dns.nameservers = random_dns_server
                cname = random_dns.query(hostname, 'CNAME')
                # Iterate through response and check for potential CNAMES
                for i in cname.response.answer:
                    for j in i.items:
                        target =  j.to_text()
                        if 'cloudfront' in target:
                            print 'CloundFront Frontable domain found: ' + str(hostname) + " " + str(target)
                        elif 'appspot.com' in target:
                            print 'Google Frontable domain found: ' + str(hostname) + " " + str(target)
                        elif 'msecnd.net' in target:
                            print 'Azure Frontable domain found: ' + str(hostname) + " " + str(target)
                        elif 'aspnetcdn.com' in target:
                            print 'Azure Frontable domain found: ' + str(hostname) + " " + str(target)
                        elif 'a248.e.akamai.net' in target:
                            print 'Akamai frontable domain found: ' + str(hostname) + " " + str(target)
                        elif 'secure.footprint.net' in target:
                            print 'Level 3 URL frontable domain found: ' + str(hostname) + " " + str(target)            
            except:
                pass
            self.queue.task_done()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=False)
    parser.add_argument('-t', '--threads', type=int, required=False, default=10)
    parser.add_argument('-a', '--alexa', type=int, required=False)
    parser.add_argument('-d', '--domain', type=str, required=False)
    args = parser.parse_args()
    threads =  args.threads
    top = args.alexa
    file = args.file
    domain = args.domain
    queue = Queue.Queue()
    if file:
        with open(file, 'r') as f:
            for d in f:
                d = d.rstrip()
                if d:
                    queue.put(d)          
    elif domain:
        subdomains = []
        subdomains = sublist3r.main(domain, threads, savefile=None, ports=None, silent=False, verbose=False, enable_bruteforce=True, engines=None)
        for i in subdomains:
            print i
            queue.put(i)
    elif alexa:
        results = alexa.top_list(top)
        for i in results:
            for r in i:
                r = str(r)
                if not r.isdigit():
                    queue.put(r)
    else:
        print "No Input Detected!"
        sys.exit()
    print "Starting search..."
    # spawn a pool of threads and pass them queue instance
    for i in range(threads):
        t = ThreadLookup(queue)
        t.setDaemon(True)
        t.start()
    
    queue.join()
    print ""
    print "Search complete!"

if __name__ == "__main__":
    main()
