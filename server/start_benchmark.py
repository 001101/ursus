import time
import datetime
import threading
import uuid
import argparse

from novaclient.v1_1 import client


BENCHMARK_SCRIPTS = {
    'fio':       'benchmarks/run_fio.sh',
    'iperf_int': 'benchmarks/run_iperf_int.sh',
    'iperf_ext': 'benchmarks/run_iperf_ext.sh',
    'unixbench': 'benchmarks/run_unixbench.sh'
}


def compile_metadata(instances_count, benchmark_server):
    return {'benchmark_id': str(uuid.uuid1()),
            'instances': str(instances_count),
            'benchmark_server': benchmark_server}


def create_instance(image, flavor, meta_data, benchmark, ssh_key):
    current_time = datetime.datetime.utcnow().isoformat()
    meta_data['create_request_at'] = current_time
    instance_name = 'ursus-instance-{}'.format(current_time)
    with open(BENCHMARK_SCRIPTS[benchmark], 'r') as startup_script:
        try:
            print nova_cl.servers.create(name=instance_name,
                                         image=image,
                                         flavor=flavor,
                                         key_name=ssh_key,
                                         meta=meta_data,
                                         userdata=startup_script)
        except Exception, e:
            print e


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keystone_url', required=True,
                        help='Keystone endpoint URL')
    parser.add_argument('-u', '--user', required=True,
                        help='Keystone username')
    parser.add_argument('-p', '--password', required=True,
                        help='Keystone password')
    parser.add_argument('-t', '--tenant', required=True,
                        help='Keystone tenant name')
    parser.add_argument('-e', '--benchmark_server', required=True,
                        help='Benchmark server to report to')
    parser.add_argument('-f', '--flavor', required=True,
                        help='Flavor ID to use for instances')
    parser.add_argument('-i', '--image', required=True,
                        help='Image ID to create instances from')
    parser.add_argument('-s', '--ssh-key',
                        help='SSH key to create instances with '
                             '(used only for debugging)')
    parser.add_argument('-b', '--benchmark', required=True,
                        help='Benchmark to be run on instances')
    parser.add_argument('-n', '--instances', type=int, required=True,
                        help='Number of instances to create')
    parser.add_argument('-l', '--load', type=int,
                        help='Number of simultaneous instance creation '
                             'requests to send')
    parser.add_argument('-a', '--sleep', type=int,
                        help='Amount of time to sleep between batches')

    args = parser.parse_args()

    if args.benchmark not in BENCHMARK_SCRIPTS.keys():
        exit('Unsupported benchmark. Exiting.')

    nova_cl = client.Client(args.user, args.password, args.tenant,
                            args.keystone_url, service_type='compute')
    meta_data = compile_metadata(args.instances, args.benchmark_server)

    if args.load:
        batches = args.instances / args.load
        batch_amount = args.load
        if batches == 0:
            batches = 1
            batch_amount = args.instances
    else:
        batches = 1
        batch_amount = args.instances

    for batch in range(batches):
        threads = []
        for i in range(batch_amount):
            thread = threading.Thread(target=create_instance,
                                      args=(args.image, args.flavor, meta_data,
                                      args.benchmark, args.ssh_key))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        if args.sleep:
            # TODO: Don't sleep if this is the last batch
            print 'Sleeping for {} seconds'.format(args.sleep)
            time.sleep(args.sleep)
