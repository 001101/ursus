ursus
=====
=====

OpenStack instance benchmarking framework (inspired by `ServerBear <http://serverbear.com>`_ benchmarking)

Supported benchmark suits:

- `UnixBench <https://code.google.com/p/byte-unixbench/>`_
- `fio <http://git.kernel.dk/?p=fio.git;a=summary>`_
- `Iperf <https://iperf.fr/>`_

Running
-------

1. Create an OpenStack instance and run :code:`install.sh` on it. This will install the ursus server (used to collect benchmarking results)
2. Run :code:`start_benchmark.py` (:code:`start_benchmark.py -h` to see available options)
3. Wait for benchmarking to finish, then check :code:`/var/www/ursus/ursus.db` SQLite database to see the results