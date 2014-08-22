#!/bin/bash

set -x

DEPS="gcc make python-pip libaio-dev"
TARBALL="http://brick.kernel.dk/snaps/fio-2.1.6.1.tar.bz2"
ASSETS_DIR="/root/benchmark_assets"
RESULTS_DIR="/root/benchmark_results"
RESULT_FILE_READ="fio_read.result"
RESULT_FILE_WRITE="fio_write.result"
BENCHMARK_SERVER=$(curl -s http://169.254.169.254/openstack/latest/meta_data.json | python -c 'import sys, json; print json.load(sys.stdin)["benchmark_server"]')
API_PATH_READ="api/fio_read"
API_PATH_WRITE="api/fio_write"
RESULT_PROCESSOR="assets/result_processor.py"
FIO_READ_JOB="assets/fio_read.job"
FIO_WRITE_JOB="assets/fio_write.job"


install_deps() {
    apt-get update
	apt-get install -y ${DEPS}
	pip install --upgrade requests
}

prepare_benchmark() {
	mkdir -p ${ASSETS_DIR}
	mkdir -p ${RESULTS_DIR}
	wget ${TARBALL} -O ${ASSETS_DIR}/fio.tbz2
	tar xjf ${ASSETS_DIR}/fio.tbz2 -C ${ASSETS_DIR}
	cd ${ASSETS_DIR}/fio-2.1.6.1
	./configure
	make install
	wget http://${BENCHMARK_SERVER}/${FIO_READ_JOB} -O ${ASSETS_DIR}/fio_read.job
	wget http://${BENCHMARK_SERVER}/${FIO_WRITE_JOB} -O ${ASSETS_DIR}/fio_write.job
	wget http://${BENCHMARK_SERVER}/${RESULT_PROCESSOR} -O ${ASSETS_DIR}/result_processor
	chmod +x ${ASSETS_DIR}/result_processor
}

run_benchmark() {
	/usr/local/bin/fio ${ASSETS_DIR}/fio_read.job > ${RESULTS_DIR}/${RESULT_FILE_READ} 2>&1
	/usr/local/bin/fio ${ASSETS_DIR}/fio_write.job > ${RESULTS_DIR}/${RESULT_FILE_WRITE} 2>&1
	${ASSETS_DIR}/result_processor -b fio_read -f ${RESULTS_DIR}/${RESULT_FILE_READ} -s http://${BENCHMARK_SERVER}/${API_PATH_READ}
	${ASSETS_DIR}/result_processor -b fio_write -f ${RESULTS_DIR}/${RESULT_FILE_WRITE} -s http://${BENCHMARK_SERVER}/${API_PATH_WRITE}
}

install_deps
prepare_benchmark
run_benchmark
