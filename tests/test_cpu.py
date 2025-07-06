import time
import multiprocessing
import math

def cpu_stress():
    print("Simulating CPU spike...")
    start = time.time()
    while time.time() - start < 180:  # Run for 180 seconds
        for _ in range(20000):
            math.factorial(1000)  # CPU-intensive calculation
    print("CPU spike triggered: CPU stress test completed")

if __name__ == "__main__":
    processes = [multiprocessing.Process(target=cpu_stress) for _ in range(multiprocessing.cpu_count() * 4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
