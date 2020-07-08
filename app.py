import time
import os
import cv2
from flask import Flask, flash, request, redirect, url_for
from flask import Response
from werkzeug.utils import secure_filename
import numpy as np
import json
import requests

import rrc_evaluation_funcs

from validation import validate_data
from script import cleval_evaluation

from arg_parser import PARAMS

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/hello')
def hello():
    return 'Hello, World'

@app.route('/cleval', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'gt_file' not in request.files :
            return json.loads(json.dumps({'status':'gt_file is not found.'}))
        if 'pred_file' not in request.files :
            return json.loads(json.dumps({'status':'pred_file is not found.'}))

        if 'eval_method' not in request.form:
            return json.loads(json.dumps({'status':'eval_method is not found.'}))
        if 'box_type' not in request.form:
            return json.loads(json.dumps({'status':'box_type is not found.'}))

        gt_file = request.files['gt_file']
        pred_file = request.files['pred_file']

        if gt_file.filename == '':
            return json.loads(json.dumps({'status':'gt_file is null.'}))
        if pred_file.filename == '':
            return json.loads(json.dumps({'status':'pred_file is null.'}))


        if not(gt_file and allowed_file(gt_file.filename) and pred_file and allowed_file(pred_file.filename)):
            return json.loads(json.dumps({'status':'input is not allowed.'}))


        if not (request.form['eval_method'] in ['detection','end-to-end']):
            return json.loads(json.dumps({'status':'evaluation method is not found.'}))

        if not (request.form['box_type'] in ['LTRB', 'QUAD', 'POLY']):
            return json.loads(json.dumps({'status':'Box Typeis not found.'}))



        gt_filename = secure_filename(gt_file.filename)
        gt_file.save(os.path.join(app.config['UPLOAD_FOLDER'], gt_filename))
        pred_filename = secure_filename(pred_file.filename)
        pred_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pred_filename))

        # Set Path, and submit
        setattr(PARAMS, 'GT_PATH', os.path.join(app.config['UPLOAD_FOLDER'], gt_filename))
        setattr(PARAMS, 'SUBMIT_PATH', os.path.join(app.config['UPLOAD_FOLDER'], pred_filename))
        

        if request.form['eval_method'] == 'detection':
            setattr(PARAMS, 'E2E', False)
        else:
            setattr(PARAMS, 'E2E', True)

        setattr(PARAMS, 'BOX_TYPE', request.form['box_type'])
     
        resDict = rrc_evaluation_funcs.main_evaluation(validate_data, cleval_evaluation)
 

        return json.loads(json.dumps({'status':'ok','evaluate':resDict}))
        
            
    return '''
    <!doctype html>
    <title>CLEval API</title>
    <h1>CLEval Tool</h1>
    <form method=post enctype=multipart/form-data>
      <b>Upload GT file  (zip): <input type=file name=gt_file> <br><br>
      <b>Upload Predict file (zip): <input type=file name=pred_file> <br><br>
      <b>Evaluation Method: 
      <input type="radio" id="detection" name="eval_method" value="detection">
      <label for="detection">detection</label>
      <input type="radio" id="end-to-end" name="eval_method" value="end-to-end" checked="checked">
      <label for="end-to-end">END-TO-END</label><br><br>

      <b>Box Type: 
      <input type="radio" id="LTRB" name="box_type" value="LTRB" checked="checked">
      <label for="LTRB">LTRB</label>      
      <input type="radio" id="LTRB" name="box_type" value="QUAD">
      <label for="QUAD">QUAD</label>
      <input type="radio" id="POLY" name="box_type" value="POLY">
      <label for="POLY">POLY</label><br><br>
      
      <br><br>
      <input type=submit value=Upload>
    </form>
    '''


# calling using this command
# FLASK_ENV=development flask run --port 8000 --host 0.0.0.0