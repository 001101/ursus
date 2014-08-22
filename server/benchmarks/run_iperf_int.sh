#!/bin/bash

set -x

DEPS="iperf python-pip"
ASSETS_DIR="/root/benchmark_assets"
RESULTS_DIR="/root/benchmark_results"
RESULT_FILE="iperf_int.result"
BENCHMARK_SERVER=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json | python -c 'import sys, json; print json.load(sys.stdin)["benchmark_server"]')
IPERF_SERVER=${BENCHMARK_SERVER}
API_PATH="api/i_perf_int"
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
}

run_benchmark() {
	iperf -c ${IPERF_SERVER} -t 900 -y C > ${RESULTS_DIR}/${RESULT_FILE}
	${ASSETS_DIR}/result_processor -b iperf -f ${RESULTS_DIR}/${RESULT_FILE} -s http://${BENCHMARK_SERVER}/${API_PATH}
}

install_deps
prepare_benchmark
run_benchmark