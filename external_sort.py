import os
import heapq
import tempfile
from multiprocessing import Pool, cpu_count


def sort_and_save_chunk(args):
    chunk_data, temp_dir, chunk_id = args
    chunk_data.sort()

    temp_path = os.path.join(temp_dir, f"chunk_{chunk_id}.txt")

    with open(temp_path, 'w') as f:
        for number in chunk_data:
            f.write(f"{number}\n")

    return temp_path


def read_chunk(file_obj, max_numbers):
    numbers = []
    for _ in range(max_numbers):
        line = file_obj.readline()
        if not line:
            break
        line = line.strip()
        if line:
            numbers.append(int(line))

    return numbers


def merge_files(sorted_files, output_file):

    file_handlers = [open(f, 'r') for f in sorted_files]

    min_heap = []

    for file_index, f in enumerate(file_handlers):

        line = f.readline()
        if line:
            value = int(line.strip())
            heapq.heappush(min_heap, (value, file_index))

    with open(output_file, 'w') as out:

        while min_heap:

            value, file_index = heapq.heappop(min_heap)
            out.write(f"{value}\n")

            next_line = file_handlers[file_index].readline()

            if next_line:
                next_value = int(next_line.strip())
                heapq.heappush(min_heap, (next_value, file_index))

    for f in file_handlers:
        f.close()

def external_sort(input_file, max_numbers_in_memory):
    base_dir = os.path.dirname(os.path.abspath(input_file))
    output_file = os.path.join(
        base_dir,
        f"sorted_{os.path.basename(input_file)}"
    )

    temp_dir = tempfile.mkdtemp(prefix='external_sort_')

    print(f"临时目录: {temp_dir}")

    tasks = []

    with open(input_file, 'r') as f:

        chunk_id = 0

        while True:

            numbers = read_chunk(f, max_numbers_in_memory)

            if not numbers:
                break

            tasks.append((numbers, temp_dir, chunk_id))

            chunk_id += 1

    print(f"Chunk 数量: {len(tasks)}")
    print(f"CPU 核心数: {cpu_count()}")

    with Pool(cpu_count()) as pool:
        sorted_temp_files = pool.map(sort_and_save_chunk, tasks)

    print("Chunk 排序完成")

    print("开始归并...")

    merge_files(sorted_temp_files, output_file)

    print(f"排序完成: {output_file}")

    for file_path in sorted_temp_files:
        os.remove(file_path)

    os.rmdir(temp_dir)
if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        description='External Parallel TXT Sort'
    )

    parser.add_argument(
        'filename',
        help='输入 txt 文件名'
    )

    parser.add_argument(
        'max_numbers',
        type=int,
        help='允许同时加载到内存中的整数数量'
    )

    args = parser.parse_args()

    external_sort(args.filename, args.max_numbers)