import math


def get_cost_per_query_per_partition(selectivity_list, partition_size, referenced_partiotions_size):
    buffer_size = 8 * 1024 * 1024
    block_size = 8 * 1024
    seek_time = 0.008
    read_disk_bw = 92 * 1024 * 1024
    partition_buffer_size = max(math.floor(buffer_size * partition_size / referenced_partiotions_size),
                              block_size)

    blocks_read_per_buffer = math.floor(partition_buffer_size / block_size)

    number_of_blocks = math.ceil(partition_size / block_size)

    seek_cost = seek_time * math.ceil(number_of_blocks / blocks_read_per_buffer)
    scan_cost = number_of_blocks * block_size / read_disk_bw
    return seek_cost + scan_cost


def get_cost_per_query(query_idx, cluster_map):
    referenced_partitions = dict((cluster_id, 0) for selectivity, cluster_id in zip(selectivity_list, cluster_map)
                             if selectivity[query_idx])

    for selectivity, cluster_id in zip(selectivity_list, cluster_map):
        if cluster_id in referenced_partitions:
            referenced_partitions[cluster_id] += 1

    referenced_partiotions_size = sum(referenced_partitions.values())

    return sum([get_cost_per_query_per_partition(part_size, referenced_partiotions_size)
                for part_size in referenced_partitions.values()])
