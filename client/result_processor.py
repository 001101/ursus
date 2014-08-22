#!/usr/bin/env python


import datetime
import json
import re

from optparse import OptionParser

import requests


META_DATA_URL = 'http://169.254.169.254/openstack/latest/meta_data.json'
UB_TESTS = {
    'Dhrystone 2 using register variables': 'dhrystone',
    'Double-Precision Whetstone': 'whetstone',
    'Execl Throughput': 'execl',
    'File Copy 1024 bufsize 2000 maxblocks': 'fcopy_1024',
    'File Copy 256 bufsize 500 maxblocks': 'fcopy_256',
    'File Copy 4096 bufsize 8000 maxblocks': 'fcopy_4096',
    'Pipe Throughput': 'pipe',
    'Pipe-based Context Switching': 'pipe_context',
    'Process Creation': 'process',
    'Shell Scripts (1 concurrent)': 'shell_1',
    'Shell Scripts (8 concurrent)': 'shell_8',
    'System Call Overhead': 'sys_call',
    'System Benchmarks Index Score': 'score'
}


def process_unixbench_result(result_file):
    with open(result_file, 'r') as ub_result_file:
        contents = ub_result_file.read()
    data = {}
    for line in contents.splitlines():
        test_match = re.match('^(.*)\s+(\d+\.\d)\s+(\d+\.\d)\s+(\d+\.\d)$',
                              line)
        if test_match is None:
            continue
        data[UB_TESTS[test_match.group(1).rstrip()]] = test_match.group(4)
    for line in contents.splitlines():
        score_match = re.match('^System Benchmarks Index Score\s+(\d+\.\d)$',
                               line)
        if score_match is not None:
            data['score'] = score_match.group(1)
    return data


def process_fio_result(result_file, result_type):
    with open(result_file, 'r') as fio_result_file:
        contents = fio_result_file.read()

    match_string = '^\s+{0}:\s' \
                   'io=(\d+\.\d+|\d+)(.*),\s' \
                   'aggrb=(\d+\.\d+|\d+)(.*),\s' \
                   'minb=(\d+\.\d+|\d+)(.*),\s' \
                   'maxb=(\d+\.\d+|\d+)(.*),\s' \
                   'mint=(\d+\.\d+|\d+)(.*),\s' \
                   'maxt=(\d+\.\d+|\d+)(.*)$'.format(result_type.upper())

    for line in contents.splitlines():
        read_match = re.match(match_string, line)
        if read_match is not None:
            data_read = {'{0}_io'.format(result_type): read_match.group(1),
                         '{0}_aggrb'.format(result_type): read_match.group(3),
                         '{0}_minb'.format(result_type): read_match.group(5),
                         '{0}_maxb'.format(result_type): read_match.group(7),
                         '{0}_mint'.format(result_type): read_match.group(9),
                         '{0}_maxt'.format(result_type): read_match.group(11)
                         }
    return data_read


def process_iperf_result(result_file):
    with open(result_file, 'r') as iperf_result_file:
        contents = iperf_result_file.read()
    data = contents.splitlines()[0].split(',')
    return {'bandwidth': data[-1]}


def get_vcpus_number():
    vcpus = []
    with open('/proc/cpuinfo') as cpuinfo:
        lines = cpuinfo.readlines()
        for line in lines:
            if line.startswith('processor'):
                vcpus.append(line)
    return len(vcpus)


def get_ram_amount():
    with open('/proc/meminfo') as meminfo:
        memtotal = meminfo.readline()
    ram = int(memtotal.split()[1]) / 1000000
    return ram


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', '--benchmark', dest='benchmark')
    parser.add_option('-f', '--file', dest='file')
    parser.add_option('-s', '--server', dest='server')
    options, args = parser.parse_args()

    if options.benchmark == 'unixbench':
        benchmark_result = process_unixbench_result(options.file)
    elif options.benchmark == 'fio_read':
        benchmark_result = process_fio_result(options.file, 'read')
    elif options.benchmark == 'fio_write':
        benchmark_result = process_fio_result(options.file, 'write')
    elif options.benchmark == 'iperf':
        benchmark_result = process_iperf_result(options.file)
    else:
        exit('Unsupported benchmark type')

    meta_data = requests.get(META_DATA_URL).json()
    benchmark_result['create_request_at'] = \
        meta_data['meta']['create_request_at']
    benchmark_result['instance_id'] = meta_data['uuid']
    benchmark_result['instance_name'] = meta_data['name']
    benchmark_result['benchmark_id'] = meta_data['meta']['benchmark_id']
    benchmark_result['vcpus'] = get_vcpus_number()
    benchmark_result['ram'] = get_ram_amount()
    benchmark_result['result_reported_at'] = \
        datetime.datetime.utcnow().isoformat()
    benchmark_result['instances'] = meta_data['meta']['instances']
    response = requests.post(options.server, json.dumps(benchmark_result),
                             headers={'Content-type': 'application/json'})
    print response.status_code
    print response.json()
