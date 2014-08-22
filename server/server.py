from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ursus.db'
db = SQLAlchemy(app)


class UnixBench(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_request_at = db.Column(db.DateTime)
    instance_id = db.Column(db.String)
    instance_name = db.Column(db.String)
    benchmark_id = db.Column(db.String)
    result_reported_at = db.Column(db.DateTime)
    vcpus = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    instances = db.Column(db.Integer)
    dhrystone = db.Column(db.Float)
    whetstone = db.Column(db.Float)
    execl = db.Column(db.Float)
    fcopy_256 = db.Column(db.Float)
    fcopy_1024 = db.Column(db.Float)
    fcopy_4096 = db.Column(db.Float)
    pipe = db.Column(db.Float)
    pipe_context = db.Column(db.Float)
    process = db.Column(db.Float)
    shell_1 = db.Column(db.Float)
    shell_8 = db.Column(db.Float)
    sys_call = db.Column(db.Float)
    score = db.Column(db.Float)


class FioRead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_request_at = db.Column(db.DateTime)
    benchmark_id = db.Column(db.String)
    result_reported_at = db.Column(db.DateTime)
    instance_id = db.Column(db.String)
    instance_name = db.Column(db.String)
    vcpus = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    instances = db.Column(db.Integer)
    read_io = db.Column(db.Float)
    read_aggrb = db.Column(db.Float)
    read_minb = db.Column(db.Float)
    read_maxb = db.Column(db.Float)
    read_mint = db.Column(db.Float)
    read_maxt = db.Column(db.Float)


class FioWrite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_request_at = db.Column(db.DateTime)
    benchmark_id = db.Column(db.String)
    result_reported_at = db.Column(db.DateTime)
    instance_id = db.Column(db.String)
    instance_name = db.Column(db.String)
    vcpus = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    instances = db.Column(db.Integer)
    write_io = db.Column(db.Float)
    write_aggrb = db.Column(db.Float)
    write_minb = db.Column(db.Float)
    write_maxb = db.Column(db.Float)
    write_mint = db.Column(db.Float)
    write_maxt = db.Column(db.Float)


class IPerfInt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_request_at = db.Column(db.DateTime)
    benchmark_id = db.Column(db.String)
    result_reported_at = db.Column(db.DateTime)
    instance_id = db.Column(db.String)
    instance_name = db.Column(db.String)
    vcpus = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    instances = db.Column(db.Integer)
    bandwidth = db.Column(db.Integer)


class IPerfExt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_request_at = db.Column(db.DateTime)
    benchmark_id = db.Column(db.String)
    result_reported_at = db.Column(db.DateTime)
    instance_id = db.Column(db.String)
    instance_name = db.Column(db.String)
    vcpus = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    instances = db.Column(db.Integer)
    bandwidth = db.Column(db.Integer)


db.create_all()
manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(UnixBench, methods=['GET', 'POST'])
manager.create_api(FioRead, methods=['GET', 'POST'])
manager.create_api(FioWrite, methods=['GET', 'POST'])
manager.create_api(IPerfInt, methods=['GET', 'POST'])
manager.create_api(IPerfExt, methods=['GET', 'POST'])
