import coincurve
import hashlib
import bech32
import base58
import time
import os
import random
import multiprocessing
import sys
import mmap
from Crypto.Hash import SHA256, RIPEMD160
from rich.console import Console

console = Console()

class MathRandomSimulator:
    def __init__(self, psize=32, start_timestamp=1262304000, end_timestamp=1388534399):
        self.rng_pool = bytearray()
        self.rng_pptr = 0
        self.rng_psize = psize
        self._seed = random.randint(start_timestamp, end_timestamp)
        random.seed(self._seed)

    @property
    def seed(self):
        return self._seed

    def rng_get_bytes(self, size):
        while len(self.rng_pool) < size:
            random_value = int(random.random() * (2**32))
            self.rng_pool.extend(random_value.to_bytes(4, 'big'))
        result = bytes(self.rng_pool[:size])
        self.rng_pool = self.rng_pool[size:]
        return result

def custom_private_key_generator(rng_simulator=None):
    rng = MathRandomSimulator()
    private_key_bytes = rng.rng_get_bytes(32)
    return private_key_bytes.hex()
    
def generate_compressed_P2P_address(private_key):
    private_key_bytes = bytes.fromhex(private_key)
    public_key = coincurve.PrivateKey(private_key_bytes).public_key.format(compressed=True)
    public_key_hash = hashlib.new('ripemd160', hashlib.sha256(public_key).digest()).hexdigest()
    extended_public_key_hash = '00' + public_key_hash
    checksum = hashlib.sha256(hashlib.sha256(bytes.fromhex(extended_public_key_hash)).digest()).hexdigest()[:8]
    p2pkh_address = base58.b58encode(bytes.fromhex(extended_public_key_hash + checksum))
    return p2pkh_address.decode()

total_keys_generated = multiprocessing.Value('i', 0)

def search_for_match(database, address_set, process_id, result_queue, rng_simulator):
    global total_keys_generated
    iteration = 0
    keys_generated_at_start = total_keys_generated.value
    start_time = time.time()
    matches = []

    while True:
        private_key = custom_private_key_generator(rng_simulator)
        compressed_p2pkh_address = generate_compressed_P2P_address(private_key)

        with total_keys_generated.get_lock():
            total_keys_generated.value += 1

        if iteration % 10000 == 0:
            current_time = time.time()
            elapsed_time = current_time - start_time
            keys_generated = total_keys_generated.value - keys_generated_at_start
            keys_per_second = keys_generated / elapsed_time if elapsed_time > 0 else 0

            print(f"\rGenerated Keys: \033[92m{total_keys_generated.value:,.0f}\033[0m"
                  f" | Keys/Second: \033[92m{keys_per_second:,.0f}\033[0m", end='', flush=True)

        if compressed_p2pkh_address in address_set:
            matches.append({
                'private_key_hex': private_key,
                'address_info': compressed_p2pkh_address,
            })

        iteration += 1

    # After the loop ends, put all matches into the result queue
    for match in matches:
        result_queue.put(match)

if __name__ == '__main__':
    file_path = 'dormant.txt'

    # Get user input for number of CPUs to use
    try:
        cpu_count = 15
        if cpu_count < 1 or cpu_count > multiprocessing.cpu_count():
            raise ValueError("Invalid CPU count")
    except ValueError as e:
        print(e)
        sys.exit(1)

    address_set = set()
    with open(file_path, 'rb') as file:
        with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
            while True:
                line = mmapped_file.readline()
                if not line:
                    break
                address_set.add(line.strip())
    
    print(f"Opening {file_path} - \033[92m{len(address_set):,.0f}\033[0m Addresses")

    database = set()
    processes = []
    result_queue = multiprocessing.Queue()
    rng_simulator = MathRandomSimulator()

    try:
        for cpu in range(cpu_count):
            process = multiprocessing.Process(target=search_for_match, args=(database, address_set, cpu, result_queue, rng_simulator))
            processes.append(process)
            process.start()

        while True:
            time.sleep(0.8)

    except KeyboardInterrupt:
        print("\nReceived KeyboardInterrupt. Terminating processes.")
        for process in processes:
            process.terminate()
            process.join()

        while not result_queue.empty():
            result = result_queue.get()
            with open('winner.txt', 'a') as output_file:
                output_file.write(f"HEX: {result['private_key_hex']}\n")
                output_file.write(f"P2PKH Bitcoin Address: {result['address_info']}\n")

        print("\nAll processes finished.")
        sys.exit(0)

