import os
import heapq
import tempfile
import multiprocessing


def process_chunk(data):
    numbers, temp_path = data
    numbers.sort()
    with open(temp_path, 'w') as file:
        for value in numbers:
            file.write(str(value) + '\n')
    return temp_path

def load_block(file, limit):
    result = []
    while len(result) < limit:
        line = file.readline()
        if not line:
            break
        line = line.strip()
        if line:
            result.append(int(line))
    return result
def merge_sorted_files(files, output_name):
    opened_files = []
    for name in files:
        opened_files.append(open(name, 'r'))
    heap = []
    for index, file in enumerate(opened_files):
        value = file.readline()
        if value:
            heapq.heappush(heap, (int(value.strip()), index))
    with open(output_name, 'w') as output:
        while heap:
            smallest, file_index = heapq.heappop(heap)
            output.write(f"{smallest}\n")
            next_value = opened_files[file_index].readline()
            if next_value:
                heapq.heappush(
                    heap,
                    (int(next_value.strip()), file_index)
                )
    for file in opened_files:
        file.close()

def sort_large_file(filename, memory_limit):
    directory = os.path.dirname(os.path.abspath(filename))
    output_file = os.path.join(
        directory,
        'sorted_' + os.path.basename(filename)
    )
    temp_folder = tempfile.mkdtemp()
    tasks = []
    with open(filename, 'r') as source:
        counter = 0
        while True:
            block = load_block(source, memory_limit)
            if len(block) == 0:
                break
            temp_file = os.path.join(
                temp_folder,
                f'temp_{counter}.txt'
            )
            tasks.append((block, temp_file))
            counter += 1
    print('Chunks:', len(tasks))
    workers = multiprocessing.cpu_count()
    print('CPU cores:', workers)
    with multiprocessing.Pool(workers) as pool:
        sorted_parts = pool.map(process_chunk, tasks)
    print('Chunk sorting completed')
    print('Merging files...')
    merge_sorted_files(sorted_parts, output_file)

    for name in sorted_parts:
        os.remove(name)
    os.rmdir(temp_folder)
    print('Sorting finished')
    print('Output file:', output_file)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Usage:')
        print('python external_sort.py <file> <memory_limit>')
        exit()
    input_file = sys.argv[1]
    memory_limit = int(sys.argv[2])
    sort_large_file(input_file, memory_limit)