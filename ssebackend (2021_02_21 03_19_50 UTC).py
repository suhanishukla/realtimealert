import json
import os
import random
import time
import csv
from datetime import datetime
from random import choice
from flask import Flask, request, Response, render_template, jsonify, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
random.seed()  # Initialize the random number generator
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ansh@5024@localhost/cec_radiance_db'
# SQLALCHEMY_TRACK_MODIFICATIONS = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

#Output Edge File
class RadienceOutputEdgeFile(db.Model):
    name = db.Column(db.String(20), primary_key=True)
    from_node = db.Column(db.String(6))
    to_node = db.Column(db.String(6))
    status = db.Column(db.String(1))

#Output Node File
class RadienceOutputNodeFile(db.Model):
    name = db.Column(db.String(6), primary_key=True)
    voltage = db.Column(db.String(6))
    load = db.Column(db.String(6))
    gen = db.Column(db.String(6))
    kind = db.Column(db.String(6))
    critical = db.Column(db.String(1))
    pathredundacy = db.Column(db.String(1))

class SystemInfo(db.Model):
    key_code  = db.Column(db.String(6), primary_key=True)
    key_desc = db.Column(db.String(20))
    key_val = db.Column(db.Integer)

class CbDetails(db.Model):
    cb_id = db.Column(db.String(10), primary_key=True)
    cb_loc = db.Column(db.String(10))
    cb_status = db.Column(db.String(2))
    # cb_timestamp = db.Column(db.DateTime)

    def __init__(self, cb_id, cb_loc, cb_status):
        self.cb_id = cb_id
        self.cb_loc = cb_loc
        self.cb_status = cb_status

class SubsDetails(db.Model):
    sub_id = db.Column(db.String(10), primary_key=True)
    sub_loc = db.Column(db.String(10))
    sub_out_feed = db.Column(db.String(10))
    sub_remarks = db.Column(db.String(20))
    # sub_timestamp = db.Column(db.DateTime)

class TransDetails(db.Model):
    trans_id = db.Column(db.String(10), primary_key=True)
    trans_rating = db.Column(db.String(10))
    trans_loc = db.Column(db.String(10))
    trans_op_condition = db.Column(db.String(20))
    # trans_timestamp = db.Column(db.DateTime)

    def __init__(self, trans_id, trans_rating, trans_loc, trans_op_condition):
        self.trans_id=trans_id
        self.trans_rating=trans_rating
        self.trans_loc=trans_loc
        self.trans_op_condition

class GuDetails(db.Model):
    g_id = db.Column(db.String(10), primary_key=True)
    g_kv = db.Column(db.String(10))
    g_unit_id = db.Column(db.String(10))
    g_status = db.Column(db.String(20))
    g_ctrl = db.Column(db.String(10))
    g_mw_measured = db.Column(db.String(10))
    g_rating = db.Column(db.String(10))
    # g_timestamp = db.Column(db.DateTime) 

    def __init__(self, g_id, g_kv, g_unit_id, g_status, g_ctrl, g_mw_measured, g_rating):
        self.g_id=g_id
        self.g_kv=g_kv
        self.g_unit_id=g_unit_id
        self.g_status=g_status
        self.g_ctrl=g_ctrl
        self.g_mw_measured=g_mw_measured
        self.g_rating=g_rating

class LoadDetails(db.Model):
    l_id = db.Column(db.String(10), primary_key=True)
    l_kv = db.Column(db.String(10))
    l_unit_id = db.Column(db.String(10))
    l_status = db.Column(db.String(20))
    l_type = db.Column(db.String(10))
    l_mw_measured = db.Column(db.String(10))
    l_mvar_measured = db.Column(db.String(10))
    # l_timestamp = db.Column(db.DateTime)

    def __init__(self, l_id, l_kv, l_unit_id, l_status, l_type, l_mw_measured, l_mvar_measured):
        self.l_id=l_id
        self.l_kv=l_kv
        self.l_unit_id=l_unit_id
        self.l_status=l_status
        self.l_type=l_type
        self.l_mw_measured=l_mw_measured
        self.l_mvar_measured=l_mvar_measured

class ResiliencyScores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    res_timestamp = db.Column(db.DateTime)
    res_rg = db.Column(db.String(10))
    res_tif = db.Column(db.String(10))
    res_dcl = db.Column(db.String(10))
    res_clnl = db.Column(db.String(10))
    res_val = db.Column(db.String(10))

    def __init__(self, res_timestamp, res_rg, res_tif, res_dcl, res_clnl, res_val):
        self.res_timestamp = res_timestamp
        self.res_rg = res_rg
        self.res_tif = res_tif
        self.res_dcl = res_dcl
        self.res_clnl = res_clnl
        self.res_val = res_val

class ThreatImpacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    threat_timestamp = db.Column(db.DateTime)
    threat_vol = db.Column(db.String(10))
    threat_freq = db.Column(db.String(10))
    threat_sch_load = db.Column(db.String(10))
    threat_sch_gen = db.Column(db.String(10))
    threat_present_load = db.Column(db.String(10))
    threat_present_gen = db.Column(db.String(10))
    threat_affected_loc = db.Column(db.String(10))

class ExpectedOutage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eo_timestamp = db.Column(db.DateTime)
    eo_fault_loc = db.Column(db.String(10))
    eo_iso_sec_detail = db.Column(db.String(10))
    eo_wind_speed = db.Column(db.String(10))
    eo_wind_direction = db.Column(db.String(10))

class EventDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_timestamp = db.Column(db.DateTime)
    event_type = db.Column(db.String(10))
    event_lat = db.Column(db.String(10))
    event_long = db.Column(db.String(10))
    event_wind_speed = db.Column(db.String(10))
    event_wind_direction = db.Column(db.String(10))

class ResilientMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resilient_timestamp = db.Column(db.DateTime)
    resilient_tf = db.Column(db.String(10))
    resilient_gf = db.Column(db.String(10))
    resilient_tif = db.Column(db.String(10))
    resilient_dcl = db.Column(db.String(10))
    resilient_clnl = db.Column(db.String(10))
    resilient_resval = db.Column(db.String(10))

class EconomicMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eco_timestamp = db.Column(db.DateTime)
    eco_tf = db.Column(db.String(10))
    eco_gf = db.Column(db.String(10))
    eco_tif = db.Column(db.String(10))
    eco_dcl = db.Column(db.String(10))
    eco_clnl = db.Column(db.String(10))
    eco_res_val = db.Column(db.String(10))

# This table is for all the Nodes location on Map
class RadienceStaticNodesGIS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_lat = db.Column(db.String(20), nullable=False)
    node_long = db.Column(db.String(20), nullable=False)
    node_code = db.Column(db.String(10)) # Codes like N200, N300
    node_desc = db.Column(db.String(100))

# This table is for all the static links on Map
class RadienceStaticNodesLinks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_node_lat = db.Column(db.String(20), nullable=False)
    from_node_long = db.Column(db.String(20), nullable=False)
    to_node_lat = db.Column(db.String(20), nullable=False)
    to_node_long = db.Column(db.String(20), nullable=False)
    link_desc = db.Column(db.String(20))

# This table is for all the Nodes location on Map
class RadienceDynamicNodesGIS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_lat = db.Column(db.String(20), nullable=False)
    node_long = db.Column(db.String(20), nullable=False)
    node_code = db.Column(db.String(10)) # Codes like N200, N300
    node_desc = db.Column(db.String(100))
    node_status = db.Column(db.Integer, nullable=False)

# This table is for all the static links on Map
class RadienceDynamicNodesLinks(db.Model):
    link_id = db.Column(db.String(20), primary_key=True)
    from_node_lat = db.Column(db.String(20), nullable=False)
    from_node_long = db.Column(db.String(20), nullable=False)
    to_node_lat = db.Column(db.String(20), nullable=False)
    to_node_long = db.Column(db.String(20), nullable=False)
    link_desc = db.Column(db.String(20))
    link_status = db.Column(db.String(5), nullable=False, default="1")


class PreEventNodesLinks(db.Model):
    link_id = db.Column(db.String(20), primary_key=True)
    from_node_lat = db.Column(db.String(20), nullable=False)
    from_node_long = db.Column(db.String(20), nullable=False)
    to_node_lat = db.Column(db.String(20), nullable=False)
    to_node_long = db.Column(db.String(20), nullable=False)
    link_desc = db.Column(db.String(20))
    link_status = db.Column(db.String(5), nullable=False, default="1")

class DuringEventNodesLinks(db.Model):
    link_id = db.Column(db.String(20), primary_key=True)
    from_node_lat = db.Column(db.String(20), nullable=False)
    from_node_long = db.Column(db.String(20), nullable=False)
    to_node_lat = db.Column(db.String(20), nullable=False)
    to_node_long = db.Column(db.String(20), nullable=False)
    link_desc = db.Column(db.String(20))
    link_status = db.Column(db.String(5), nullable=False, default="1")


class PostEventNodesLinks(db.Model):
    link_id = db.Column(db.String(20), primary_key=True)
    from_node_lat = db.Column(db.String(20), nullable=False)
    from_node_long = db.Column(db.String(20), nullable=False)
    to_node_lat = db.Column(db.String(20), nullable=False)
    to_node_long = db.Column(db.String(20), nullable=False)
    link_desc = db.Column(db.String(20))
    link_status = db.Column(db.String(5), nullable=False, default="1")

# Marshmallow classes
class RadienceOutputEdgeFileSchema(ma.Schema):
    class Meta:
        fields = ('name', 'from_node', 'to_node', 'status')
output_edge_schema = RadienceOutputEdgeFileSchema()
output_edges_schema = RadienceOutputEdgeFileSchema(many=True)

class RadienceOutputNodeFileSchema(ma.Schema):
    class Meta:
        fields = ('name','voltage','load',
            'gen',
            'kind',
            'critical', 
            'pathredundacy')
output_node_schema = RadienceOutputNodeFileSchema()
output_nodes_schema = RadienceOutputNodeFileSchema(many=True)


class SystemInfoSchema(ma.Schema):
    class Meta:
        fields = ('key_code','key_desc','key_val')
system_info_schema = SystemInfoSchema()
system_infos_schema = SystemInfoSchema(many=True)  


class CbDetailsSchema(ma.Schema):
    class Meta:
        fields = ('cb_id', 'cb_loc', 'cb_status')
cb_detail_schema=CbDetailsSchema()
cb_details_schema=CbDetailsSchema(many=True)


class TransDetailsSchema(ma.Schema):
    class Meta:
        fields = ('trans_id', 'trans_rating', 'trans_loc', 'trans_op_condition')
trans_detail_schema = TransDetailsSchema()
trans_details_schema = TransDetailsSchema(many=True)


class SubsDetailsSchema(ma.Schema):
    class Meta:
        fields=('sub_id', 'sub_loc', 'sub_out_feed', 'sub_remarks')
sub_detail_schema = SubsDetailsSchema()
sub_details_schema = SubsDetailsSchema(many=True)


class GuDetailsSchema(ma.Schema):
    class Meta:
        fields = ('g_id', 'g_kv','g_unit_id', 'g_status', 'g_ctrl', 'g_mw_measured', 'g_rating')
gu_detail_schema = GuDetailsSchema()
gu_details_schema = GuDetailsSchema(many=True)


class LoadDetailsSchema(ma.Schema):
    class Meta:
        fields = ('l_id', 'l_kv','l_unit_id', 'l_status', 'l_type', 'l_mw_measured', 'l_mvar_measured')
loads_detail_schema = LoadDetailsSchema()
loads_details_schema = LoadDetailsSchema(many=True)

class RadienceStaticNodesGISSchema(ma.Schema):
    class Meta: 
        fields = ('id','node_lat','node_long','node_code','node_desc')
static_node_schema = RadienceStaticNodesGISSchema()
static_nodes_schema = RadienceStaticNodesGISSchema(many=True)

class RadienceDynamicEdgesGISSchema(ma.Schema):
    class Meta:
        fields = ('link_id','from_node_lat','from_node_long','to_node_lat','to_node_long','link_desc','link_status')
dynamic_link_schema = RadienceDynamicEdgesGISSchema()
dynamic_links_schema = RadienceDynamicEdgesGISSchema(many=True)


class PreEventDynamicEdgesGISSchema(ma.Schema):
    class Meta:
        fields = ('link_id','from_node_lat','from_node_long','to_node_lat','to_node_long','link_desc','link_status')
pre_dynamic_link_schema = PreEventDynamicEdgesGISSchema()
pre_dynamic_links_schema = PreEventDynamicEdgesGISSchema(many=True)

class DuringEventDynamicEdgesGISSchema(ma.Schema):
    class Meta:
        fields = ('link_id','from_node_lat','from_node_long','to_node_lat','to_node_long','link_desc','link_status')
during_dynamic_link_schema = DuringEventDynamicEdgesGISSchema()
during_dynamic_links_schema = DuringEventDynamicEdgesGISSchema(many=True)

class PostEventDynamicEdgesGISSchema(ma.Schema):
    class Meta:
        fields = ('link_id','from_node_lat','from_node_long','to_node_lat','to_node_long','link_desc','link_status')
post_dynamic_link_schema = PostEventDynamicEdgesGISSchema()
post_dynamic_links_schema = PostEventDynamicEdgesGISSchema(many=True)


#Routes
@app.route('/')
def index():
    return render_template('RadianceProject.html')

@app.route('/systeminfo', methods = ['GET', 'POST'])
def system_info():
    if request.method == 'POST':
        f = request.files['file']
        fstring = f.read()
        fstring = fstring.decode("utf-8") 
        
        #create list of dictionaries keyed by header row
        csv_dicts = [{k: v for k, v in row.items()} for row in csv.DictReader(fstring.splitlines(), skipinitialspace=True)]
        csv_dicts = csv_dicts[0]

        for k in csv_dicts:
            try:
                updateStatus = SystemInfo.query.filter_by(key_code=k).update(dict(key_val=csv_dicts[k]))
                if updateStatus == 0: 
                    return 'Unsuccessful. Please check the file structure'
                db.session.commit()
            except:
                return "Something went wrong. Check the csv file structure."
        wait_time = 3000
        seconds = wait_time / 1000
        redirect_url = 'http://127.0.0.1:5000/'
        return f"<html><body><p>Your upload was successful. You will be redirected to homepage in { seconds } seconds</p><script>var timer = setTimeout(function() {{window.location='{ redirect_url }'}}, { wait_time });</script></body></html>"


    if request.method == 'GET':  
        query_result = SystemInfo.query.all()
        final_result = system_infos_schema.dump(query_result) 
        return jsonify({'data': final_result})


@app.route('/cbdetails', methods = ['GET', 'POST'])
def cb_details():
    if request.method == 'POST':
        f = request.files['file']
        data = pd.read_csv(f)
        
        for i in range(len(data)): 
            cbrow = CbDetails(str(data['cb_id'][i]), str(data['cb_location'][i]), str(data['cb_status'][i]))
            try:
                db.session.add(cbrow)
                # if status == 0:
                #     return 'Unsuccessful. Please check the file structure'
                db.session.commit()
            except ValueError as ve:
                print(ve)
                return "Something went wrong. Check the csv file structure."    
        
        wait_time = 3000
        seconds = wait_time / 1000
        redirect_url = 'http://127.0.0.1:5000/'
        return f"<html><body><p>Your upload was successful. You will be redirected to homepage in { seconds } seconds</p><script>var timer = setTimeout(function() {{window.location='{ redirect_url }'}}, { wait_time });</script></body></html>"

    else:
        query_result = CbDetails.query.all()
        final_result = cb_details_schema.dump(query_result) 
        return jsonify({'data': final_result})


@app.route('/transdetails', methods = ['GET', 'POST'])
def trans_details():
    if request.method == 'POST':
        f = request.files['file']
        data = pd.read_csv(f)
        
        for i in range(len(data)): 
            transRow = TransDetails(str(data['t_id'][i]), str(data['t_rating'][i]), str(data['t_location'][i]), str(data['t_oper_condition'][i]))
            try:
                db.session.add(transRow)
                db.session.commit()
            except ValueError as ve:
                print(ve)
                return "Something went wrong. Check the csv file structure."    
        
        wait_time = 3000
        seconds = wait_time / 1000
        redirect_url = 'http://127.0.0.1:5000/'
        return f"<html><body><p>Your upload was successful. You will be redirected to homepage in { seconds } seconds</p><script>var timer = setTimeout(function() {{window.location='{ redirect_url }'}}, { wait_time });</script></body></html>"

    else:
        query_result = TransDetails.query.all()
        final_result = trans_details_schema.dump(query_result) 
        return jsonify({'data': final_result})


@app.route('/subdetails', methods = ['GET', 'POST'])
def sub_details():
    if request.method == 'POST':
        pass
    else:
        query_result = SubsDetails.query.all()
        final_result = sub_details_schema.dump(query_result) 
        return jsonify({'data': final_result})


@app.route('/gudetails', methods = ['GET', 'POST'])
def gu_details():
    if request.method == 'POST':
        f = request.files['file']
        data = pd.read_csv(f)
        
        for i in range(len(data)): 
            guRow = GuDetails(str(data['g_id'][i]), str(data['g_kv'][i]), str(data['g_unitid'][i]), str(data['g_status'][i]), str(data['g_control'][i]), str(data['g_mw'][i]), str(data['g_rating'][i]))
            try:
                db.session.add(guRow)
                db.session.commit()
            except ValueError as ve:
                print(ve)
                return "Something went wrong. Check the csv file structure."    
        
        wait_time = 3000
        seconds = wait_time / 1000
        redirect_url = 'http://127.0.0.1:5000/'
        return f"<html><body><p>Your upload was successful. You will be redirected to homepage in { seconds } seconds</p><script>var timer = setTimeout(function() {{window.location='{ redirect_url }'}}, { wait_time });</script></body></html>"
    else:
        query_result = GuDetails.query.all()
        final_result = gu_details_schema.dump(query_result) 
        return jsonify({'data': final_result})


@app.route('/loaddetails', methods = ['GET', 'POST'])
def load_details():
    if request.method == 'POST':
        f = request.files['file']
        data = pd.read_csv(f)
        
        for i in range(len(data)): 
            guRow = LoadDetails(str(data['l_id'][i]), str(data['l_kv'][i]), str(data['l_unitid'][i]), str(data['l_status'][i]), str(data['l_type'][i]), str(data['l_mw'][i]), str(data['l_measured'][i]))
            try:
                db.session.add(guRow)
                db.session.commit()
            except ValueError as ve:
                print(ve)
                return "Something went wrong. Check the csv file structure."    
        
        wait_time = 3000
        seconds = wait_time / 1000
        redirect_url = 'http://127.0.0.1:5000/'
        return f"<html><body><p>Your upload was successful. You will be redirected to homepage in { seconds } seconds</p><script>var timer = setTimeout(function() {{window.location='{ redirect_url }'}}, { wait_time });</script></body></html>"
    else:
        query_result = LoadDetails.query.all()
        final_result = loads_details_schema.dump(query_result) 
        return jsonify({'data': final_result})


@app.route('/staticnodes')
def static_nodes():
    query_result = RadienceStaticNodesGIS.query.all()
    final_result = static_nodes_schema.dump(query_result)
    links_result = RadienceDynamicNodesLinks.query.all()
    final_links_result = dynamic_links_schema.dump(links_result) 
    return jsonify({'data': final_result, 'links': final_links_result})

@app.route('/preeventedges')
def pre_event_edges():
    # query_result = PreEventNodesLinks.query.all()
    # final_result = pre_static_nodes_schema.dump(query_result)
    links_result = PreEventNodesLinks.query.all()
    final_links_result = pre_dynamic_links_schema.dump(links_result) 
    return jsonify({'links': final_links_result})


@app.route('/duringeventedges')
def during_event_edges():
    # query_result = PreEventNodesLinks.query.all()
    # final_result = pre_static_nodes_schema.dump(query_result)
    links_result = DuringEventNodesLinks.query.all()
    final_links_result = during_dynamic_links_schema.dump(links_result) 
    return jsonify({'links': final_links_result})


@app.route('/posteventedges')
def post_event_edges():
    # query_result = PreEventNodesLinks.query.all()
    # final_result = pre_static_nodes_schema.dump(query_result)
    links_result = PostEventNodesLinks.query.all()
    final_links_result = post_dynamic_links_schema.dump(links_result) 
    return jsonify({'links': final_links_result})

@app.route('/exportfiles')
def export_files():
    edge = RadienceOutputEdgeFile.query.all()
    node = RadienceOutputNodeFile.query.all()
    edge_result = output_edges_schema.dump(edge)
    node_result = output_nodes_schema.dump(node)

    path = os.getcwd()
    path = path + "/outputfiles/"
    with open(path+'edge-file-case0.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'from_node','to_node','status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for eachrow in edge_result:
            writer.writerow({'name': eachrow['name'], 'from_node': eachrow['from_node'], 'to_node': eachrow['to_node'], 'status': eachrow['status']})

    with open(path+'node-file-case0.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'voltage','load','gen', 'kind', 'critical', 'pathredundacy']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for eachrow in node_result:
            writer.writerow({'name': eachrow['name'], 'voltage': eachrow['voltage'], 
            'load': eachrow['load'], 'gen': eachrow['gen'], 'kind':eachrow['kind'], 'critical':eachrow['critical'], 
            'pathredundacy':eachrow['pathredundacy']})

    # print(final_result[0].name)
    result = {"result": "Files created"}
    return jsonify(result)

@app.route('/bar-chart-data')
def bar_chart_data():
    def generate_random_values():
        counterMax = 13
        counter = 0
        tf = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        rg = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        tif = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        dcl = [0.70286, 0.69407, 0.70749, 0.67424, 0.61322, 0.64357, 0.6833, 0.6851, 0.74966, 0.79589, 0.78448, 0.78558, 0.79163]
        clnl = [0.6, 0.6, 0.64, 0.6, 0.52, 0.56, 0.6, 0.6, 0.68, 0.76, 0.72, 0.72, 0.72]
        resiliency = [0.80207, 0.7993, 0.81489, 0.79304, 0.75109, 0.77201, 0.7959, 0.79647, 0.83954, 0.87684, 0.86188, 0.86223, 0.86414]
        while True:
            if counter == counterMax:
                counter = 0 
            json_data = json.dumps(
                {
                    # 'tf': choice([0.34, 0.43, 0.55, 0.34, 0.55, 0.43]),
                    # 'rg': choice([0.34, 0.43, 0.55, 0.34, 0.55, 0.43]),
                    # 'tif': choice([0.34, 0.43, 0.55, 0.34, 0.55, 0.43]),
                    # 'dcl': choice([0.34, 0.43, 0.55, 0.34, 0.55, 0.43]),
                    # 'clnl': choice([0.34, 0.43, 0.55, 0.34, 0.55, 0.43]),
                    # 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    # 'resiliency': choice([0.79, 0.73, 0.81, 0.74, 0.85, 0.90])

                    'tf': tf[counter],
                    'rg': rg[counter],
                    'tif': tif[counter],
                    'dcl': dcl[counter],
                    'clnl': clnl[counter],
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'resiliency': resiliency[counter] 
                })
            yield f"data:{json_data}\n\n"
            json_data = json.loads(json_data)
            # print(json_data["tf"])
            #res_timestamp, res_rg, res_tif, res_dcl, res_clnl, res_val)
            newData = ResiliencyScores(json_data['time'], json_data['rg'], json_data['tif'], json_data['dcl'], json_data['clnl'], json_data['resiliency'])
            # print(DateTime(json_data["time"]))
            # newData = ResiliencyScores(0.2, 0.5, 0.6, 0.1, 0.9, 0.10)
            try:
                db.session.add(newData)
                db.session.commit()
                # print("It's working")
            except:
                print("bar-chart data api not working")
            counter += 1
            time.sleep(10)

    return Response(generate_random_values(), mimetype='text/event-stream')

#Updated files in the system

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
