#!/bin/bash

set -x

DEPS="gcc make python-pip"
TARBALL="https://byte-unixbench.googlecode.com/files/UnixBench5.1.3.tgz"
ASSETS_DIR="/root/benchmark_assets"
RESULTS_DIR="/root/benchmark_results"
RESULT_FILE="unixbench.result"
BENCHMARK_SERVER=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json | python -c 'import sys, json; print json.load(sys.stdin)["benchmark_server"]')
API_PATH="api/unix_bench"
RESULT_PROCESSOR="assets/result_processor.py"


install_deps() {
    apt-get update
    apt-get install -y ${DEPS}
    pip install --upgrade requests
}

prepare_benchmark() {
    mkdir -p ${ASSETS_DIR}
    mkdir -p ${RESULTS_DIR}
    wget http://${BENCHMARK_SERVER}/${RESULT_PROCESSOR} -O ${ASSETS_DIR}/result_processor
    chmod +x ${ASSETS_DIR}/result_processor
    wget ${TARBALL} -O ${ASSETS_DIR}/unixbench.tgz
    tar xzf ${ASSETS_DIR}/unixbench.tgz -C ${ASSETS_DIR}
    cd ${ASSETS_DIR}/UnixBench
    make
}

run_benchmark() {
    echo -e '#!/bin/bash' > ${ASSETS_DIR}/run_unixbench.cron
    echo -e "cd ${ASSETS_DIR}/UnixBench && ./Run -c `grep -c processor /proc/cpuinfo` > ${RESULTS_DIR}/${RESULT_FILE} 2>&1 && ${ASSETS_DIR}/result_processor -b unixbench -f ${RESULTS_DIR}/${RESULT_FILE} -s http://${BENCHMARK_SERVER}/${API_PATH}" >> ${ASSETS_DIR}/run_unixbench.cron
    chmod +x ${ASSETS_DIR}/run_unixbench.cron
    echo "@reboot ${ASSETS_DIR}/run_unixbench.cron &" > ${ASSETS_DIR}/unixbench_crontab
    crontab ${ASSETS_DIR}/unixbench_crontab
    reboot
}

install_deps
prepare_benchmark
run_benchmark
