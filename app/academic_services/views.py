import os
from datetime import datetime, date
from pprint import pprint
from typing import Iterable

import arrow
import pandas
from io import BytesIO
import pytz
import requests
from pdfrw import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, SimpleDocTemplate, Paragraph, TableStyle, Table, Spacer, KeepTogether, PageBreak
from sqlalchemy.orm import make_transient
from wtforms import FormField

from app.main import app, get_credential, json_keyfile
from app.academic_services import academic_services
from app.academic_services.forms import (ServiceCustomerInfoForm, LoginForm, ForgetPasswordForm, ResetPasswordForm,
                                         ServiceCustomerAccountForm, create_request_form, ServiceCustomerContactForm,
                                         ServiceCustomerAddressForm, create_payment_form, ServiceSampleAppointmentForm,
                                         )
from app.academic_services.models import *
from flask import render_template, flash, redirect, url_for, request, current_app, abort, session, make_response, \
    jsonify, send_file
from flask_login import login_user, current_user, logout_user, login_required
from flask_principal import Identity, identity_changed, AnonymousIdentity
from flask_admin.helpers import is_safe_url
from itsdangerous.url_safe import URLSafeTimedSerializer as TimedJSONWebSignatureSerializer
from app.main import mail
from flask_mail import Message
from werkzeug.utils import secure_filename
from pydrive.auth import ServiceAccountCredentials, GoogleAuth
from pydrive.drive import GoogleDrive

sarabun_font = TTFont('Sarabun', 'app/static/fonts/THSarabunNew.ttf')
pdfmetrics.registerFont(sarabun_font)
style_sheet = getSampleStyleSheet()
style_sheet.add(ParagraphStyle(name='ThaiStyle', fontName='Sarabun'))
style_sheet.add(ParagraphStyle(name='ThaiStyleNumber', fontName='Sarabun', alignment=TA_RIGHT))
style_sheet.add(ParagraphStyle(name='ThaiStyleCenter', fontName='Sarabun', alignment=TA_CENTER))

gauth = GoogleAuth()
keyfile_dict = requests.get(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')).json()
scopes = ['https://www.googleapis.com/auth/drive']
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, scopes)
drive = GoogleDrive(gauth)

FOLDER_ID = '1832el0EAqQ6NVz2wB7Ade6wRe-PsHQsu'

keyfile = requests.get(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')).json()

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

bangkok = pytz.timezone('Asia/Bangkok')


def send_mail(recp, title, message):
    message = Message(subject=title, body=message, recipients=recp)
    mail.send(message)


def initialize_gdrive():
    gauth = GoogleAuth()
    scopes = ['https://www.googleapis.com/auth/drive']
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(keyfile, scopes)
    return GoogleDrive(gauth)


@academic_services.route('/lab/index')
def second_lab_index():
    lab = request.args.get('lab')
    return render_template('academic_services/second_lab_index.html', lab=lab)


@academic_services.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        next_url = request.args.get('next', url_for('academic_services.customer_account'))
        if is_safe_url(next_url):
            return redirect(next_url)
        else:
            return abort(400)
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(ServiceCustomerAccount).filter_by(email=form.email.data).first()
        if user:
            pwd = form.password.data
            if user.verify_password(pwd):
                login_user(user)
                identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
                next_url = request.args.get('next', url_for('index'))
                if not is_safe_url(next_url):
                    return abort(400)
                else:
                    flash('ลงทะเบียนเข้าใช้งานสำเร็จ', 'success')
                    if user.is_first_login == True :
                        return redirect(url_for('academic_services.lab_index', menu='new'))
                    else:
                        user.is_first_login = True
                        db.session.add(user)
                        db.session.commit()
                        return redirect(url_for('academic_services.customer_account', menu='view'))
            else:
                flash('รหัสผ่านไม่ถูกต้อง กรุณาลองอีกครั้ง', 'danger')
                return redirect(url_for('academic_services.customer_index'))
        else:
            flash('ไม่พบบัญชีผู้ใช้งาน', 'danger')
            return redirect(url_for('academic_services.customer_index'))
    else:
        for er in form.errors:
            flash("{} {}".format(er, form.errors[er]), 'danger')
    return render_template('academic_services/login.html', form=form)


@academic_services.route('/logout')
@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    flash('ออกจากระบบเรียบร้อย', 'success')
    return redirect(url_for('academic_services.customer_index'))


@academic_services.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        return redirect('academic_services.customer_account')
    form = ForgetPasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = ServiceCustomerAccount.query.filter_by(email=form.email.data).first()
            if not user:
                flash('ไม่พบบัญชีผู้ใช้งาน', 'warning')
                return render_template('academic_services/forget_password.html', form=form, errors=form.errors)
            serializer = TimedJSONWebSignatureSerializer(app.config.get('SECRET_KEY'))
            token = serializer.dumps({'email': form.email.data})
            url = url_for('academic_services.reset_password', token=token, _external=True)
            message = 'Click the link below to reset the password.'\
                      ' กรุณาคลิกที่ลิงค์เพื่อทำการตั้งรหัสผ่านใหม่\n\n{}'.format(url)
            try:
                send_mail([form.email.data],
                          title='MUMT-MIS: Password Reset. ตั้งรหัสผ่านใหม่สำหรับระบบ MUMT-MIS',
                          message=message)
            except:
                flash('ระบบไม่สามารถส่งอีเมลได้กรุณาตรวจสอบอีกครั้ง'.format(form.email.data),'danger')
            else:
                flash('โปรดตรวจสอบอีเมลของท่านเพื่อทำการแก้ไขรหัสผ่านภายใน 20 นาที', 'success')
            return redirect(url_for('academic_services.login'))
        else:
            for er in form.errors:
                flash("{} {}".format(er, form.errors[er]), 'danger')
    return render_template('academic_services/forget_password.html', form=form)


@academic_services.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    serializer = TimedJSONWebSignatureSerializer(app.config.get('SECRET_KEY'))
    try:
        token_data = serializer.loads(token, max_age=72000)
    except:
        return 'รหัสสำหรับทำการตั้งค่า password หมดอายุหรือไม่ถูกต้อง'
    user = ServiceCustomerAccount.query.filter_by(email=token_data.get('email')).first()
    if not user:
        flash('ไม่พบชื่อบัญชีในฐานข้อมูล')
        return redirect(url_for('academic_services.customer_index'))

    form = ResetPasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user.password = form.new_password.data
            db.session.add(user)
            db.session.commit()
            flash('ตั้งรหัสผ่านใหม่เรียบร้อย', 'success')
            return redirect(url_for('academic_services.customer_index'))
        else:
            for er in form.errors:
                flash("{} {}".format(er, form.errors[er]), 'danger')
    return render_template('academic_services/reset_password.html', form=form)


@academic_services.route('/customer/index', methods=['GET', 'POST'])
def customer_index():
    labs = ServiceLab.query.all()
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(ServiceCustomerAccount).filter_by(email=form.email.data).first()
        if user:
            pwd = form.password.data
            if user.verify_password(pwd):
                login_user(user)
                identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
                next_url = request.args.get('next', url_for('academic_services.customer_index'))
                if not is_safe_url(next_url):
                    return abort(400)
                else:
                    flash('ลงทะเบียนเข้าใช้งานสำเร็จ', 'success')
                    if user.is_first_login == True :
                        return redirect(url_for('academic_services.lab_index', menu='new'))
                    else:
                        user.is_first_login = True
                        db.session.add(user)
                        db.session.commit()
                        return redirect(url_for('academic_services.customer_account', menu='view'))
            else:
                flash('รหัสผ่านไม่ถูกต้อง กรุณาลองอีกครั้ง', 'danger')
                return redirect(url_for('academic_services.customer_index'))
        else:
            flash('ไม่พบบัญชีผู้ใช้งาน', 'danger')
            return redirect(url_for('academic_services.customer_index'))
    else:
        for er in form.errors:
            flash("{} {}".format(er, form.errors[er]), 'danger')
    return render_template('academic_services/customer_index.html', form=form, labs=labs)


@academic_services.route('/customer/lab/index')
def lab_index():
    menu = request.args.get('menu')
    labs = ServiceLab.query.all()
    return render_template('academic_services/lab_index.html', menu=menu, labs=labs)


@academic_services.route('/customer/sub/lab/index')
def sub_lab_index():
    menu = request.args.get('menu')
    lab = request.args.get('lab')
    return render_template('academic_services/sub_lab_index.html', lab=lab, menu=menu)


@academic_services.route('/customer/lab/detail', methods=['GET', 'POST'])
def detail_lab_index():
    code = request.args.get('code')
    menu = request.args.get('menu') or code
    labs = ServiceLab.query.filter_by(code=code)
    return render_template('academic_services/detail_lab_index.html', labs=labs, code=code, menu=menu)


@academic_services.route('/customer/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password and confirm_password:
            if new_password == confirm_password:
                current_user.password = new_password
                db.session.add(current_user)
                db.session.commit()
                flash('รหัสผ่านแก้ไขแล้ว', 'success')
            else:
                flash('รหัสผ่านไม่ตรงกัน', 'danger')
        else:
            flash('กรุณากรอกรหัสใหม่', 'danger')
    return render_template('academic_services/account.html')


@academic_services.route('/customer/view', methods=['GET', 'POST'])
def customer_account():
    menu = request.args.get('menu')
    return render_template('academic_services/customer_account.html', menu=menu)


@academic_services.route('/customer/account/add', methods=['GET', 'POST'])
def create_customer_account(customer_id=None):
    menu = request.args.get('menu')
    form = ServiceCustomerAccountForm()
    if form.validate_on_submit():
        account = ServiceCustomerAccount()
        form.populate_obj(account)
        if form.confirm_pdpa.data:
            db.session.add(account)
            db.session.commit()
            serializer = TimedJSONWebSignatureSerializer(app.config.get('SECRET_KEY'))
            token = serializer.dumps({'email': form.email.data})
            scheme = 'http' if current_app.debug else 'https'
            url = url_for('academic_services.verify_email', token=token, _external=True, _scheme=scheme)
            message = 'Click the link below to confirm.' \
                        ' กรุณาคลิกที่ลิงค์เพื่อทำการยืนยันการสมัครบัญชีระบบ MUMT-MIS\n\n{}'.format(url)
            send_mail([form.email.data], title='ยืนยันการสมัครบัญชีระบบ MUMT-MIS', message=message)
            flash('โปรดตรวจสอบอีเมลของท่านผ่านภายใน 20 นาที', 'success')
            return redirect(url_for('academic_services.customer_index'))
        else:
            flash('กรุณาคลิกยืนยันการให้เก็บข้อมูลส่วนบุคคลตามนโยบาย', 'danger')
            return redirect(url_for('academic_services.create_customer_account', form=form, customer_id=customer_id,
                           menu=menu))
    else:
        for er in form.errors:
            flash("{} {}".format(er, form.errors[er]), 'danger')
    return render_template('academic_services/create_customer.html', form=form, customer_id=customer_id,
                           menu=menu)


@academic_services.route('/email-verification', methods=['GET', 'POST'])
def verify_email():
    token = request.args.get('token')
    serializer = TimedJSONWebSignatureSerializer(app.config.get('SECRET_KEY'))
    try:
        token_data = serializer.loads(token, max_age=72000)
    except:
        return 'รหัสสำหรับทำการสมัครบัญชีหมดอายุหรือไม่ถูกต้อง'
    user = ServiceCustomerAccount.query.filter_by(email=token_data.get('email')).first()
    if not user:
        flash('ไม่พบชื่อบัญชีผู้ใช้งาน กรุณาลงทะเบียนใหม่อีกครั้ง', 'danger')
    elif user.verify_datetime:
        flash('ได้รับการยืนยันอีเมลแล้ว', 'info')
    else:
        user.verify_datetime = arrow.now('Asia/Bangkok').datetime
        db.session.add(user)
        db.session.commit()
        flash('ยืนยันอีเมลเรียบร้อยแล้ว', 'success')
    return redirect(url_for('academic_services.customer_index'))


@academic_services.route('/customer/add', methods=['GET', 'POST'])
@academic_services.route('/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer_account(customer_id=None):
    menu = request.args.get('menu')
    account = ServiceCustomerAccount.query.get(current_user.id)
    if customer_id:
        customer = ServiceCustomerInfo.query.get(customer_id)
        form = ServiceCustomerInfoForm(obj=customer)
    else:
        form = ServiceCustomerInfoForm()
        customer = ServiceCustomerInfo.query.all()
    if form.validate_on_submit():
        if customer_id is None:
            customer = ServiceCustomerInfo()
        form.populate_obj(customer)
        if customer_id is None:
            account.customer_info = customer
            db.session.add(account)
        db.session.add(customer)
        db.session.commit()
        flash('แก้ไขข้อมูลสำเร็จ', 'success')
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp
    return render_template('academic_services/modal/edit_customer_modal.html', form=form, menu=menu,
                           customer_id=customer_id, customer=customer)


@academic_services.route('/edit_password', methods=['GET', 'POST'])
def edit_password():
    menu = request.args.get('menu')
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password and confirm_password:
            if new_password == confirm_password:
                current_user.password = new_password
                db.session.add(current_user)
                db.session.commit()
                flash('รหัสผ่านแก้ไขแล้ว', 'success')
            else:
                flash('รหัสผ่านไม่ตรงกัน', 'danger')
        else:
            flash('กรุณากรอกรหัสใหม่', 'danger')
    return render_template('academic_services/edit_password.html', menu=menu)


@academic_services.route('/customer/organization/add/<int:customer_id>', methods=['GET', 'POST'])
def add_organization(customer_id):
    customer = ServiceCustomerInfo.query.get(customer_id)
    form = ServiceCustomerInfoForm(obj=customer)
    if form.validate_on_submit():
        form.populate_obj(customer)
        db.session.add(customer)
        db.session.commit()
        flash('เพิ่มบริษัท/องค์กรในข้อมูลบัญชีของท่านสำเร็จ', 'success')
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp
    return render_template('academic_services/modal/add_organization_modal.html', form=form,
                           customer_id=customer_id)


@academic_services.route('/customer/organization/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_organization(customer_id):
    customer = ServiceCustomerInfo.query.get(customer_id)
    form = ServiceCustomerInfoForm(obj=customer)
    if form.validate_on_submit():
        form.populate_obj(customer)
        if form.same_address.data:
            customer.quotation_address = form.document_address.data
        db.session.add(customer)
        db.session.commit()
        flash('แก้ไขข้อมูลบริษัท/องค์กรสำเร็จ', 'success')
        resp= make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp
    return render_template('academic_services/modal/edit_organization_modal.html', form=form,
                           customer_id=customer_id)


@academic_services.route('/admin/customer/delete/<int:customer_id>', methods=['GET', 'DELETE'])
def delete_customer_by_admin(customer_id):
    if customer_id:
        customer = ServiceCustomerInfo.query.get(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash('ลบรายชื่อลูกค้าสำเร็จ', 'success')
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp


@academic_services.route('/admin/customer/address/view/<int:customer_id>')
def view_customer_address(customer_id):
    customers = ServiceCustomerInfo.query.get(customer_id)
    return render_template('academic_services/modal/view_customer_address_modal.html', customers=customers)


@academic_services.route('/academic-service-form', methods=['GET'])
def get_request_form():
    code = request.args.get('code')
    lab = ServiceLab.query.filter_by(code=code).first()
    sub_lab = ServiceSubLab.query.filter_by(code=code).first()
    sheetid = '1EHp31acE3N1NP5gjKgY-9uBajL1FkQe7CCrAu-TKep4'
    print('Authorizing with Google..')
    gc = get_credential(json_keyfile)
    wks = gc.open_by_key(sheetid)
    if sub_lab:
        sheet = wks.worksheet(sub_lab.sheet)
    else:
        sheet = wks.worksheet(lab.sheet)
    df = pandas.DataFrame(sheet.get_all_records())
    form = create_request_form(df)()
    template = ''
    for f in form:
        template += str(f)
    return template


@academic_services.route('/academic-service-request', methods=['GET'])
@login_required
def create_service_request():
    code = request.args.get('code')
    return render_template('academic_services/request_form.html', code=code)


def form_data(data):
    if isinstance(data, dict):
        return {k: form_data(v) for k, v in data.items() if k != "csrf_token" and k != 'submit'}
    elif isinstance(data, list):
        return [form_data(item) for item in data]
    elif isinstance(data, (date)):
        return data.isoformat()
    return data


@academic_services.route('/submit-request', methods=['POST'])
@academic_services.route('/submit-request/<int:request_id>', methods=['POST'])
def submit_request(request_id=None):
    if request_id:
        service_request = ServiceRequest.query.get(request_id)
        lab = ServiceLab.query.filter_by(code=service_request.lab).first()
        sub_lab = ServiceSubLab.query.filter_by(code=service_request.lab).first()
    else:
        code = request.args.get('code')
        lab = ServiceLab.query.filter_by(code=code).first()
        sub_lab = ServiceSubLab.query.filter_by(code=code).first()
    sheetid = '1EHp31acE3N1NP5gjKgY-9uBajL1FkQe7CCrAu-TKep4'
    gc = get_credential(json_keyfile)
    wks = gc.open_by_key(sheetid)
    if sub_lab:
        sheet = wks.worksheet(sub_lab.sheet)
    else:
        sheet = wks.worksheet(lab.sheet)
    df = pandas.DataFrame(sheet.get_all_records())
    form = create_request_form(df)(request.form)
    if request_id:
        req = ServiceRequest.query.get(request_id)
        req.data = form_data(form.data)
        req.modified_at = arrow.now('Asia/Bangkok').datetime
    else:
        req = ServiceRequest(customer_account_id=current_user.id, created_at=arrow.now('Asia/Bangkok').datetime,
                             lab=sub_lab.code if sub_lab else lab.code, data=form_data(form.data))
    db.session.add(req)
    db.session.commit()
    if not request_id:
        req.request_no = f'RQ{req.id}'
        db.session.add(req)
        db.session.commit()
    return redirect(url_for('academic_services.view_request', request_id=req.id))


@academic_services.route('/customer/request/index')
@login_required
def request_index():
    menu = request.args.get('menu')
    return render_template('academic_services/request_index.html', menu=menu)


@academic_services.route('/api/request/index')
def get_requests():
    query = ServiceRequest.query.filter_by(customer_account_id=current_user.id)
    records_total = query.count()
    search = request.args.get('search[value]')
    if search:
        query = query.filter(ServiceRequest.created_at.contains(search))
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    total_filtered = query.count()
    query = query.offset(start).limit(length)
    data = []
    for item in query:
        item_data = item.to_dict()
        data.append(item_data)
    return jsonify({'data': data,
                    'recordFiltered': total_filtered,
                    'recordTotal': records_total,
                    'draw': request.args.get('draw', type=int)
                    })


@academic_services.route('/request/view/<int:request_id>')
@login_required
def view_request(request_id=None):
    request = ServiceRequest.query.get(request_id)
    return render_template('academic_services/view_request.html', request=request)


def generate_request_pdf(service_request, sign=False, cancel=False):
    logo = Image('app/static/img/logo-MU_black-white-2-1.png', 40, 40)

    sheetid = '1EHp31acE3N1NP5gjKgY-9uBajL1FkQe7CCrAu-TKep4'
    gc = get_credential(json_keyfile)
    wks = gc.open_by_key(sheetid)
    lab = ServiceLab.query.filter_by(code=service_request.lab).first()
    sub_lab = ServiceSubLab.query.filter_by(code=service_request.lab).first()
    if sub_lab:
        sheet = wks.worksheet(sub_lab.sheet)
    else:
        sheet = wks.worksheet(lab.sheet)
    df = pandas.DataFrame(sheet.get_all_records())
    data = service_request.data
    form = create_request_form(df)(**data)
    values = []
    set_fields = set()
    for fn in df.fieldGroup:
        for field in getattr(form, fn):
            if field.type == 'FieldList':
                for fd in field:
                    for f in fd:
                        if f.data != None and f.data != '' and f.data != [] and f.label not in set_fields:
                            set_fields.add(f.label)
                            if f.type == 'CheckboxField':
                                values.append(f"{f. label.text} : {', '.join(f.data)}")
                            else:
                                values.append(f"{f.label.text} : {f.data}")
            else:
                if field.data != None and field.data != '' and field.data != [] and field.label not in set_fields:
                    set_fields.add(field.label)
                    if field.type == 'CheckboxField':
                        values.append(f"{field.label.text} : {', '.join(field.data)}")
                    else:
                        values.append(f"{field.label.text} : {field.data}")

    def all_page_setup(canvas, doc):
        canvas.saveState()
        canvas.setFont("Sarabun", 12)
        page_number = canvas.getPageNumber()
        canvas.drawString(530, 30, f"Page {page_number}")
        canvas.restoreState()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            rightMargin=20,
                            leftMargin=20,
                            topMargin=10,
                            bottomMargin=10
                            )

    data = []

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=style_sheet['ThaiStyle'],
        fontSize=15,
        alignment=TA_CENTER,
    )

    header = Table([[Paragraph('<b>ใบขอรับบริการ / Request</b>', style=header_style)]], colWidths=[530],
                   rowHeights=[25])

    header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    lab_address = '''<para><font size=12>
                    {address}
                    </font></para>'''.format(address=lab.address if lab else sub_lab.address)

    lab_table = Table([[logo, Paragraph(lab_address, style=style_sheet['ThaiStyle'])]], colWidths=[45, 330])

    lab_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    staff_only = '''<para><font size=12>
                สำหรับเจ้าหน้าที่ / Staff only<br/>
                เลขที่ใบคำขอ &nbsp;&nbsp;_____________<br/>
                วันที่รับตัวอย่าง _____________<br/>
                วันที่รายงานผล _____________<br/>
                </font></para>'''

    staff_table = Table([[Paragraph(staff_only, style=style_sheet['ThaiStyle'])]], colWidths=[150])

    staff_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    content_header = Table([[Paragraph('<b>รายละเอียด / Detail</b>', style=header_style)]], colWidths=[530],
                           rowHeights=[25])

    content_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    detail_style = ParagraphStyle(
        'ThaiStyle',
        parent=style_sheet['ThaiStyle'],
        fontSize=12,
        leading=18
    )

    customer = '''<para>ข้อมูลผู้ส่งตรวจ<br/>
                        ผู้ส่ง : {customer}<br/>
                        ที่อยู่ : {address}<br/>
                        เบอร์โทรศัพท์ : {phone_number}<br/>
                        อีเมล : {email}
                    </para>
                    '''.format(customer=current_user.customer_info.cus_name,
                               address=', '.join([address.address for address in current_user.customer_info.addresses if address.address_type == 'customer']),
                               phone_number=current_user.customer_info.phone_number,
                               email=current_user.customer_info.email)

    customer_table = Table([[Paragraph(customer, style=detail_style)]], colWidths=[530])

    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    data.append(KeepTogether(Spacer(7, 7)))
    data.append(KeepTogether(Paragraph('<para align=center><font size=18>ใบขอรับบริการ / REQUEST<br/><br/></font></para>',
                                       style=style_sheet['ThaiStyle'])))
    data.append(KeepTogether(header))
    data.append(KeepTogether(Spacer(3, 3)))
    data.append(KeepTogether(Table([[lab_table, staff_table]], colWidths=[378, 163])))
    data.append(KeepTogether(Spacer(3, 3)))
    data.append(KeepTogether(content_header))
    data.append(KeepTogether(Spacer(7, 7)))
    data.append(KeepTogether(customer_table))

    details = 'ข้อมูลผลิตภัณฑ์' + "<br/>" + "<br/>".join(values)
    first_page_limit = 500
    remaining_text = ""
    current_length = 0

    lines = details.split("<br/>")
    first_page_lines = []
    for line in lines:
        if current_length + detail_style.leading <= first_page_limit:
            first_page_lines.append(line)
            current_length += detail_style.leading
        else:
            remaining_text += line + "<br/>"

    first_page_text = "<br/>".join(first_page_lines)
    first_page_paragraph = Paragraph(first_page_text, style=detail_style)

    if remaining_text:
        remaining_paragraph = Paragraph(remaining_text, style=detail_style)

    first_page_table = [[first_page_paragraph]]
    first_page_table = Table(first_page_table, colWidths=[530])
    first_page_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    data.append(KeepTogether(first_page_table))

    if remaining_text:
        data.append(PageBreak())
        remaining_table = [[remaining_paragraph]]
        remaining_table = Table(remaining_table, colWidths=[530])
        remaining_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        data.append(KeepTogether(Spacer(20, 20)))
        data.append(KeepTogether(content_header))
        data.append(KeepTogether(Spacer(7, 7)))
        data.append(KeepTogether(remaining_table))
    lab_test = '''<para><font size=12>
                    สำหรับเจ้าหน้าที่<br/>
                    Lab No. : __________________________________<br/>
                    สภาพตัวอย่าง : O ปกติ<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; O ไม่ปกติ<br/>
                    </font></para>'''

    lab_test_table = Table([[Paragraph(lab_test, style=detail_style)]], colWidths=[530])

    lab_test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    if service_request.lab == 'bacteria' or service_request.lab == 'virology':
        if remaining_text:
            data.append(KeepTogether(lab_test_table))
        else:
            data.append(KeepTogether(lab_test_table))

    doc.build(data, onLaterPages=all_page_setup, onFirstPage=all_page_setup)
    buffer.seek(0)
    return buffer


@academic_services.route('/request/pdf/<int:request_id>', methods=['GET'])
def export_request_pdf(request_id):
    service_request = ServiceRequest.query.get(request_id)
    buffer = generate_request_pdf(service_request)
    return send_file(buffer, download_name='Request_form.pdf', as_attachment=True)


@academic_services.route('/customer/quotation/index')
@login_required
def quotation_index():
    menu = request.args.get('menu')
    return render_template('academic_services/quotation_index.html', menu=menu)


@academic_services.route('/api/quotation/index')
def get_quotations():
    query = ServiceRequest.query.filter( ServiceRequest.customer_account_id == current_user.id, ServiceRequest.status != None)
    records_total = query.count()
    search = request.args.get('search[value]')
    if search:
        query = query.filter(ServiceRequest.created_at.contains(search))
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    total_filtered = query.count()
    query = query.offset(start).limit(length)
    data = []
    for item in query:
        item_data = item.to_dict()
        data.append(item_data)
    return jsonify({'data': data,
                    'recordFiltered': total_filtered,
                    'recordTotal': records_total,
                    'draw': request.args.get('draw', type=int)
                    })


@academic_services.route('/quotation/view/<int:request_id>')
@login_required
def view_quotation(request_id=None):
    request = ServiceRequest.query.get(request_id)
    return render_template('academic_services/view_quotation.html', request=request)


def generate_quotation_pdf(request, sign=False, cancel=False):
    logo = Image('app/static/img/logo-MU_black-white-2-1.png', 40, 40)

    value = []

    def all_page_setup(canvas, doc):
        canvas.saveState()
        logo_image = ImageReader('app/static/img/mu-watermark.png')
        canvas.drawImage(logo_image, 140, 265, mask='auto')
        canvas.restoreState()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            rightMargin=20,
                            leftMargin=20,
                            topMargin=10,
                            bottomMargin=10,
                            )
    # data = []
    #
    # if request.lab == 'bacteria':
    #     lab_address = '''<para><font size=11>
    #                     ห้องปฏิบัติการประเมินความปลอดภัยทางอาหารและชีวภาพ หน่วยตรวจวิเคราะห์ทางชีวภาพ<br/>
    #                     คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
    #                     เลขที่ 2 ถนนวังหลัง แขวงศิริราช เขตบำงกอกน้อย กรุงเทพฯ 10700<br/>
    #                     โทร 02-419-7172, 065-523-3387 เลขที่ผู้เสียภาษี 0994000158378<br/>
    #                     </font></para>'''
    # elif request.lab == 'foodsafety':
    #     lab_address = '''<para><font size=11>
    #                     ห้องปฏิบัติการประเมินความปลอดภัยทางอาหารและชีวภาพ (หน่วยตรวจวิเคราะห์สารเคมีป้องกันกาจัดศัตรูพืช)<br/>
    #                     อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์ คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
    #                     เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
    #                     โทร 084-349-8489 หรือ 0-2441-4371 ต่อ 2630 เลขที่ผู้เสียภาษี 0994000158378<br/>
    #                     </font></para>'''
    # elif request.lab == 'heavymetal':
    #     lab_address = '''<para><font size=11>
    #                     ห้องปฏิบัติการประเมินความปลอดภัยทางอาหารและชีวภาพ (หน่วยตรวจวิเคราะห์โลหะหนัก)<br/>
    #                     อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์ คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
    #                     เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
    #                     โทร 084-349-8489 หรือ 0-2441-4371 ต่อ 2630 เลขที่ผู้เสียภาษี 0994000158378<br/>
    #                     </font></para>'''
    # elif request.lab == 'mass_spectrometry':
    #     lab_address = '''<para><font size=11>
    #                     งานบริการโปรติโอมิกส์ ห้อง 608 อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์<br/>
    #                     คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
    #                     เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
    #                     โทร 02-441-4371 ต่อ 2620<br/>
    #                     </font></para>'''
    # elif request.lab == 'quantitative':
    #     lab_address = '''<para><font size=11>
    #                     งานบริการโปรติโอมิกส์ ห้อง 608 อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์<br/>
    #                     คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
    #                     เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
    #                     โทร 02-441-4371 ต่อ 2620<br/>
    #                     </font></para>'''
    # elif request.lab == 'toxicolab':
    #     lab_address = '''<para><font size=11>
    #                     ห้องปฏิบัติการพิศวิทยา งานพัฒนาคุณภาพและประเมินผลิตภัณฑ์<br/>
    #                     ตึกคณะเทคนิคการแพทย์ ชั้น 5 ภายในโรงพยาบาลศิริราช<br/>
    #                     เลขที่ 2 ถนนวังหลัง แขวงศิริราช เขตบำงกอกน้อย กรุงเทพฯ 10700<br/>
    #                     โทร 02-412-4727 ต่อ 153 E-mail : toxicomtmu@gmail.com<br/>
    #                     </font></para>'''
    # elif request.lab == 'virology':
    #     lab_address = '''<para><font size=11>
    #                     โครงการงานบริการทางห้องปฏิบัติการไวรัสวิทยา<br/>
    #                     คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
    #                     เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
    #                     โทร 0-2441-4371 ต่อ 2610 เลขที่ผู้เสียภาษี 0994000158378<br/>
    #                     </font></para>'''
    # elif request.lab == 'endotoxin':
    #     lab_address = '''<para><font size=11>
    #                     ห้องปฏิบัติการคณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
    #                     คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
    #                     เลขที่ 2 ถนนวังหลัง แขวงศิริราช เขตบา   งกอกน้อย กรุงเทพฯ 10700<br/>
    #                     โทร 02-411-2258 ต่อ 171, 174 หรือ 081-423-5013<br/>
    #                     </font></para>'''
    # else:
    #     lab_address = '''<para><font size=11>
    #                     งานบริการโปรติโอมิกส์ ห้อง 608 อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์<br/>
    #                     คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
    #                     เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
    #                     โทร 02-441-4371 ต่อ 2620<br/>
    #                     </font></para>'''
    #
    # quotation_info = '''<br/><br/><font size=10>
    #             เลขที่/No. {quotation_no}<br/>
    #             วันที่/Date {issued_date}
    #             </font>
    #             '''
    # quotation = request.quotations
    # quotation_no = quotation.quotation_no
    # issued_date = arrow.get(quotation.created_at.astimezone(bangkok)).format(fmt='DD MMMM YYYY', locale='th-th')
    # quotation_info_ori = quotation_info.format(quotation_no=quotation_no,
    #                                        issued_date=issued_date,
    #                                        )
    #
    # header_content_ori = [
    #     [[logo, Paragraph(lab_address, style=style_sheet['ThaiStyle'])],
    #      [Paragraph(quotation_info_ori, style=style_sheet['ThaiStyle'])]]
    # ]
    #
    # header_styles = TableStyle([
    #     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    #     ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    #     ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    # ])
    #
    # header_ori = Table(header_content_ori, colWidths=[400, 100])
    #
    # header_ori.hAlign = 'CENTER'
    # header_ori.setStyle(header_styles)
    #
    # customer_name = '''<para><font size=11>
    #             ลูกค้า/Customer {customer}<br/>
    #             ที่อยู่/Address {address}<br/>
    #             เลขประจำตัวผู้เสียภาษี/Taxpayer identification no {taxpayer_identification_no}
    #             </font></para>
    #             '''.format(customer=request.customer,
    #                        address=", ".join(address.address for address in request.customer.addresses
    #                                          if address.address_type == 'quotation'),
    #                        taxpayer_identification_no=request.customer.taxpayer_identification_no)
    #
    # customer = Table([[Paragraph(customer_name, style=style_sheet['ThaiStyle']),
    #                    ]],
    #                  colWidths=[540, 280]
    #                  )
    # customer.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    #                               ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    #
    # items = [[Paragraph('<font size=10>ลำดับ / No.</font>', style=style_sheet['ThaiStyleCenter']),
    #           Paragraph('<font size=10>รายการ / Description</font>', style=style_sheet['ThaiStyleCenter']),
    #           Paragraph('<font size=10>จำนวน / Quality</font>', style=style_sheet['ThaiStyleCenter']),
    #           Paragraph('<font size=10>ราคาหน่วย(บาท)/ Unit Price</font>', style=style_sheet['ThaiStyleCenter']),
    #           Paragraph('<font size=10>ราคารวม(บาท) / Total</font>', style=style_sheet['ThaiStyleCenter']),
    #           ]]
    #
    # n = len(items)
    # for i in range(18 - n):
    #     items.append([
    #         Paragraph('<font size=12>&nbsp; </font>', style=style_sheet['ThaiStyleNumber']),
    #         Paragraph('<font size=12> </font>', style=style_sheet['ThaiStyle']),
    #         Paragraph('<font size=12> </font>', style=style_sheet['ThaiStyleNumber']),
    #         Paragraph('<font size=12> </font>', style=style_sheet['ThaiStyleNumber']),
    #         Paragraph('<font size=12> </font>', style=style_sheet['ThaiStyleNumber']),
    #     ])
    #
    # items.append([
    #     Paragraph('<font size=12></font>', style=style_sheet['ThaiStyleNumber']),
    #     Paragraph('<font size=12>รวมทั้งสิ้น</font>', style=style_sheet['ThaiStyle']),
    #     Paragraph('<font size=12></font>', style=style_sheet['ThaiStyleNumber'])
    # ])
    # item_table = Table(items, colWidths=[50, 250, 75])
    # item_table.setStyle(TableStyle([
    #     ('BOX', (0, 0), (-1, 0), 0.25, colors.black),
    #     ('BOX', (0, -1), (-1, -1), 0.25, colors.black),
    #     ('BOX', (0, 0), (0, -1), 0.25, colors.black),
    #     ('BOX', (1, 0), (1, -1), 0.25, colors.black),
    #     ('BOX', (2, 0), (2, -1), 0.25, colors.black),
    #     ('BOX', (3, 0), (3, -1), 0.25, colors.black),
    #     ('BOX', (4, 0), (4, -1), 0.25, colors.black),
    #     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    #     ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
    #     ('BOTTOMPADDING', (0, -2), (-1, -2), 10),
    # ]))
    # item_table.setStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
    # item_table.setStyle([('SPAN', (0, -1), (1, -1))])
    #
    # text_info = Paragraph('<br/><font size=12>ขอแสดงความนับถือ<br/></font>',style=style_sheet['ThaiStyle'])
    # text = [[text_info, Paragraph('<font size=12></font>', style=style_sheet['ThaiStyle'])]]
    # text_table = Table(text, colWidths=[0, 155, 155])
    # text_table.hAlign = 'RIGHT'
    # sign_info = Paragraph('<font size=12>(&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
    #                       '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
    #                       '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
    #                       '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</font>', style=style_sheet['ThaiStyle'])
    # sign = [[sign_info, Paragraph('<font size=12></font>', style=style_sheet['ThaiStyle'])]]
    # sign_table = Table(sign, colWidths=[0, 200, 200])
    # sign_table.hAlign = 'RIGHT'
    #
    # data.append(KeepTogether(Paragraph('<para align=center><font size=16>ใบเสนอราคา<br/><br/></font></para>',
    #                                    style=style_sheet['ThaiStyle'])))
    # data.append(KeepTogether(Paragraph('<para align=center><font size=16>QUOTATION<br/><br/><br/></font></para>',
    #                                    style=style_sheet['ThaiStyle'])))
    # data.append(KeepTogether(header_ori))
    # data.append(KeepTogether(Spacer(1, 12)))
    # data.append(KeepTogether(customer))
    # data.append(KeepTogether(Spacer(1, 16)))
    # data.append(KeepTogether(item_table))
    # data.append(KeepTogether(Spacer(1, 16)))
    # data.append(KeepTogether(text_table))
    # data.append(KeepTogether(Spacer(1, 25)))
    # data.append(KeepTogether(sign_table))

    doc.build(data, onLaterPages=all_page_setup, onFirstPage=all_page_setup)
    buffer.seek(0)
    return buffer


@academic_services.route('/quotation/pdf/<int:request_id>', methods=['GET'])
def export_quotation_pdf(request_id):
    requests = ServiceRequest.query.get(request_id)
    buffer = generate_quotation_pdf(requests)
    return send_file(buffer, download_name='Quotation.pdf', as_attachment=True)


@academic_services.route('/quotation/confirm/<int:request_id>', methods=['GET', 'POST'])
def confirm_quotation(request_id=None):
    quotation = ServiceQuotation.query.filter_by(request_id=request_id).first()
    if not quotation:
        quotation = ServiceQuotation(
            request_id=request_id,
            total_price=0.0,
            status=True
        )
    else:
        quotation.status = True
    db.session.add(quotation)
    db.session.commit()
    flash('ยืนยันสำเร็จ', 'success')
    resp = make_response()
    resp.headers['HX-Refresh'] = 'true'
    return resp


@academic_services.route('/customer/contact/index')
@login_required
def customer_contact_index():
    menu = request.args.get('menu')
    contacts = ServiceCustomerContact.query.filter_by(adder_id=current_user.id)
    return render_template('academic_services/customer_contact_index.html', contacts=contacts, menu=menu,
                           adder_id=current_user.id)


@academic_services.route('/api/contact/index')
def get_customer_contacts():
    adder_id = request.args.get('adder_id')
    query = ServiceCustomerContact.query.filter_by(adder_id=adder_id)
    records_total = query.count()
    search = request.args.get('search[value]')
    if search:
        query = query.filter(ServiceCustomerContact.name.contains(search))
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    total_filtered = query.count()
    query = query.offset(start).limit(length)
    data = []
    for item in query:
        item_data = item.to_dict()
        data.append(item_data)
    return jsonify({'data': data,
                    'recordFiltered': total_filtered,
                    'recordTotal': records_total,
                    'draw': request.args.get('draw', type=int)
                    })


@academic_services.route('/customer/contact/add', methods=['GET', 'POST'])
@academic_services.route('/customer/contact/edit/<int:contact_id>', methods=['GET', 'POST'])
def create_customer_contact(contact_id=None):
    adder_id = request.args.get('adder_id')
    if contact_id:
        contact = ServiceCustomerContact.query.get(contact_id)
        form = ServiceCustomerContactForm(obj=contact)
    else:
        form = ServiceCustomerContactForm()
        contact = ServiceCustomerContact.query.all()
    if form.validate_on_submit():
        if contact_id is None:
            contact = ServiceCustomerContact()
        form.populate_obj(contact)
        if contact_id is None:
            contact.adder_id = current_user.id
        db.session.add(contact)
        db.session.commit()
        if contact_id:
            flash('แก้ไขข้อมูลสำเร็จ', 'success')
        else:
            flash('เพิ่มข้อมูลสำเร็จ', 'success')
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp
    return render_template('academic_services/modal/create_customer_contact_modal.html', adder_id=adder_id,
                           contact_id=contact_id, form=form)


@academic_services.route('/customer/contact/delete/<int:contact_id>', methods=['GET', 'DELETE'])
def delete_customer_contact(contact_id):
    if contact_id:
        contact = ServiceCustomerContact.query.get(contact_id)
        db.session.delete(contact)
        db.session.commit()
        flash('ลบข้อมูลสำเร็จ', 'success')
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp


@academic_services.route('/customer/address/index')
def address_index():
    menu = request.args.get('menu')
    addresses = ServiceCustomerAddress.query.filter_by(customer_id=current_user.customer_info.id).all()
    return render_template('academic_services/address_index.html', addresses=addresses, menu=menu)


@academic_services.route('/customer/address/add', methods=['GET', 'POST'])
@academic_services.route('/customer/address/edit/<int:address_id>', methods=['GET', 'POST'])
def create_address(address_id=None):
    type = request.args.get('type')
    if address_id:
        address = ServiceCustomerAddress.query.get(address_id)
        form = ServiceCustomerAddressForm(obj=address)
    else:
        form = ServiceCustomerAddressForm()
        address = ServiceCustomerAddress.query.all()
    if form.validate_on_submit():
        if address_id is None:
            address = ServiceCustomerAddress()
        form.populate_obj(address)
        if address_id is None:
            address.customer_id = current_user.customer_info.id
            address.address_type = type
        db.session.add(address)
        db.session.commit()
        if address_id:
            flash('แก้ไขข้อมูลสำเร็จ', 'success')
        else:
            flash('เพิ่มข้อมูลสำเร็จ', 'success')
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp
    return render_template('academic_services/modal/create_address_modal.html', address_id=address_id,
                           type=type, form=form)


@academic_services.route('/customer/address/delete/<int:address_id>', methods=['GET', 'DELETE'])
def delete_address(address_id):
    address = ServiceCustomerAddress.query.get(address_id)
    db.session.delete(address)
    db.session.commit()
    flash('ลบข้อมูลสำเร็จ', 'success')
    resp = make_response()
    resp.headers['HX-Refresh'] = 'true'
    return resp


@academic_services.route('/customer/address/submit/<int:address_id>', methods=['GET', 'POST'])
def submit_same_address(address_id):
    if request.method == 'POST':
        address = ServiceCustomerAddress.query.get(address_id)
        db.session.expunge(address)
        make_transient(address)
        address.name = address.name
        address.address_type = 'customer'
        address.address = address.address
        address.phone_number = address.phone_number
        address.remark = None
        address.customer_account_id = current_user.id
        address.id = None
        db.session.add(address)
        db.session.commit()
        flash('ยืนยันสำเร็จ', 'success')
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp


@academic_services.route('/customer/appointment/inde')
def sample_appointment_index():
    menu = request.args.get('menu')
    requests = ServiceRequest.query.filter_by(customer_account_id=current_user.id)
    return render_template('academic_services/sample_appointment_index.html', requests=requests, menu=menu)


@academic_services.route('/customer/appointment/add/<int:request_id>', methods=['GET', 'POST'])
@academic_services.route('/customer/appointment/edit/<int:appointment_id>', methods=['GET', 'POST'])
def create_sample_appointment(request_id=None, appointment_id=None):
    if appointment_id:
        appointment = ServiceSampleAppointment.query.get(appointment_id)
        form = ServiceSampleAppointmentForm(obj=appointment)
    else:
        form = ServiceSampleAppointmentForm()
        appointment = ServiceSampleAppointment.query.all()
    if form.validate_on_submit():
        if appointment_id is None:
            appointment = ServiceSampleAppointment()
        form.populate_obj(appointment)
        appointment.appointment_date = arrow.get(form.appointment_date.data, 'Asia/Bangkok').datetime
        db.session.add(appointment)
        db.session.commit()
        if appointment_id is None:
            requests = ServiceRequest.query.filter_by(id=request_id).all()
            for request in requests:
                request.appointment_id = appointment.id
                db.session.add(request)
                db.session.commit()
        if appointment_id:
            flash('แก้ไขข้อมูลสำเร็จ', 'success')
        else:
            flash('เพิ่มข้อมูลสำเร็จ', 'success')
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp
    return render_template('academic_services/modal/create_sample_appointment.html', request_id=request_id,
                           appointment_id=appointment_id, form=form)


@academic_services.route('/customer/payment/index')
def payment_index():
    menu = request.args.get('menu')
    requests = ServiceRequest.query.filter_by(customer_account_id=current_user.id).all()
    for r in requests:
        if r.payment and r.payment.url:
            file_upload = drive.CreateFile({'id': r.payment.url})
            file_upload.FetchMetadata()
            r.file_url = file_upload.get('embedLink')
        else:
            r.file_url = None
    return render_template('academic_services/payment_index.html', requests=requests, menu=menu)


@academic_services.route('/customer/payment/add', methods=['GET', 'POST'])
def add_payment():
    payment_id = request.args.get('payment_id')
    payment = ServicePayment.query.get(payment_id)
    ServicePaymentForm = create_payment_form(file='file')
    form = ServicePaymentForm(obj=payment)
    if form.validate_on_submit():
        form.populate_obj(payment)
        file = form.file_upload.data
        payment.customer_account_id = current_user.id
        payment.paid_at = arrow.now('Asia/Bangkok').datetime
        payment.status = 'รอตรวจสอบการชำระเงิน'
        drive = initialize_gdrive()
        if file:
            file_name = secure_filename(file.filename)
            file.save(file_name)
            file_drive = drive.CreateFile({'title': file_name,
                                           'parents': [{'id': FOLDER_ID, "kind": "drive#fileLink"}]})
            file_drive.SetContentFile(file_name)
            file_drive.Upload()
            permission = file_drive.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
            payment.url = file_drive['id']
            payment.bill = file_name
        db.session.add(payment)
        db.session.commit()
        flash('อัพเดตสลิปสำเร็จ', 'success')
        return redirect(url_for('academic_services.payment_index', customer_account_id=current_user.id))
    else:
        for field, error in form.errors.items():
            flash(f'{field}: {error}', 'danger')
    return render_template('academic_services/add_payment.html', payment_id=payment_id, payment=payment,
                           form=form)


@academic_services.route('/customer/result/index')
def result_index():
    menu = request.args.get('menu')
    requests = ServiceRequest.query.filter_by(customer_account_id=current_user.id).all()
    for r in requests:
        if r.result and r.result.url:
            file_upload = drive.CreateFile({'id': r.result.url})
            file_upload.FetchMetadata()
            r.file_url = f"https://drive.google.com/uc?export=download&id={r.result.url}"
        else:
            r.file_url = None
    return render_template('academic_services/result_index.html', requests=requests, menu=menu)


@academic_services.route('/customer/invoice/index')
@login_required
def invoice_index():
    menu = request.args.get('menu')
    return render_template('academic_services/invoice_index.html', menu=menu)


@academic_services.route('/invoice/view/<int:request_id>')
@login_required
def view_invoice(request_id=None):
    request = ServiceRequest.query.get(request_id)
    return render_template('academic_services/view_invoice.html', request=request)


def generate_invoice_pdf(request, sign=False, cancel=False):
    logo = Image('app/static/img/logo-MU_black-white-2-1.png', 40, 40)

    value = []

    for data in request.data:
        name = data[0]
        items = data[1]
        name_data = [f"{name}"]

        for item in items:
            name_item = item[0]
            value_item = item[1]
            if value_item:
                if isinstance(value_item, list):
                    formatted_value = ', '.join(value_item)
                else:
                    formatted_value = value_item
                name_data.append(f"{name_item} :  {formatted_value}")
        if len(name_data) > 1:
            value.append("<br/>".join(name_data))

    def all_page_setup(canvas, doc):
        canvas.saveState()
        logo_image = ImageReader('app/static/img/mu-watermark.png')
        canvas.drawImage(logo_image, 140, 265, mask='auto')
        canvas.restoreState()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            rightMargin=20,
                            leftMargin=20,
                            topMargin=10,
                            bottomMargin=10,
                            )
    data = []

    if request.lab == 'bacteria':
        lab_address = '''<para><font size=11>
                        ห้องปฏิบัติการประเมินความปลอดภัยทางอาหารและชีวภาพ หน่วยตรวจวิเคราะห์ทางชีวภาพ<br/>
                        คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
                        เลขที่ 2 ถนนวังหลัง แขวงศิริราช เขตบำงกอกน้อย กรุงเทพฯ 10700<br/>
                        โทร 02-419-7172, 065-523-3387 เลขที่ผู้เสียภาษี 0994000158378<br/>
                        </font></para>'''
    elif request.lab == 'foodsafety':
        lab_address = '''<para><font size=11>
                        ห้องปฏิบัติการประเมินความปลอดภัยทางอาหารและชีวภาพ (หน่วยตรวจวิเคราะห์สารเคมีป้องกันกาจัดศัตรูพืช)<br/>
                        อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์ คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
                        เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
                        โทร 084-349-8489 หรือ 0-2441-4371 ต่อ 2630 เลขที่ผู้เสียภาษี 0994000158378<br/>
                        </font></para>'''
    elif request.lab == 'heavymetal':
        lab_address = '''<para><font size=11>
                        ห้องปฏิบัติการประเมินความปลอดภัยทางอาหารและชีวภาพ (หน่วยตรวจวิเคราะห์โลหะหนัก)<br/>
                        อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์ คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
                        เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
                        โทร 084-349-8489 หรือ 0-2441-4371 ต่อ 2630 เลขที่ผู้เสียภาษี 0994000158378<br/>
                        </font></para>'''
    elif request.lab == 'mass_spectrometry':
        lab_address = '''<para><font size=11>
                        งานบริการโปรติโอมิกส์ ห้อง 608 อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์<br/>
                        คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
                        เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
                        โทร 02-441-4371 ต่อ 2620<br/>
                        </font></para>'''
    elif request.lab == 'quantitative':
        lab_address = '''<para><font size=11>
                        งานบริการโปรติโอมิกส์ ห้อง 608 อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์<br/>
                        คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
                        เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
                        โทร 02-441-4371 ต่อ 2620<br/>
                        </font></para>'''
    elif request.lab == 'toxicolab':
        lab_address = '''<para><font size=11>
                        ห้องปฏิบัติการพิศวิทยา งานพัฒนาคุณภาพและประเมินผลิตภัณฑ์<br/>
                        ตึกคณะเทคนิคการแพทย์ ชั้น 5 ภายในโรงพยาบาลศิริราช<br/>
                        เลขที่ 2 ถนนวังหลัง แขวงศิริราช เขตบำงกอกน้อย กรุงเทพฯ 10700<br/>
                        โทร 02-412-4727 ต่อ 153 E-mail : toxicomtmu@gmail.com<br/>
                        </font></para>'''
    elif request.lab == 'virology':
        lab_address = '''<para><font size=11>
                        โครงการงานบริการทางห้องปฏิบัติการไวรัสวิทยา<br/>
                        คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
                        เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
                        โทร 0-2441-4371 ต่อ 2610 เลขที่ผู้เสียภาษี 0994000158378<br/>
                        </font></para>'''
    elif request.lab == 'endotoxin':
        lab_address = '''<para><font size=11>
                        ห้องปฏิบัติการคณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
                        คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
                        เลขที่ 2 ถนนวังหลัง แขวงศิริราช เขตบา   งกอกน้อย กรุงเทพฯ 10700<br/>
                        โทร 02-411-2258 ต่อ 171, 174 หรือ 081-423-5013<br/>
                        </font></para>'''
    else:
        lab_address = '''<para><font size=11>
                        งานบริการโปรติโอมิกส์ ห้อง 608 อาคารวิทยาศาสตร์และเทคโนโลยีการแพทย์<br/>
                        คณะเทคนิคการแพทย์ มหาวิทยาลัยมหิดล<br/>
                        เลขที่ 999 ถนนพุทธมณฑลสาย 4 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170<br/>
                        โทร 02-441-4371 ต่อ 2620<br/>
                        </font></para>'''

    invoice_info = '''<br/><br/><font size=10>
                เลขที่/No. {invoice_no}<br/>
                วันที่/Date {issued_date}
                </font>
                '''
    invoice = request.invoices[0]
    invoice_no = invoice.invoice_no
    issued_date = arrow.get(invoice.created_at.astimezone(bangkok)).format(fmt='DD MMMM YYYY', locale='th-th')
    invoice_info_ori = invoice_info.format(invoice_no=invoice_no,
                                           issued_date=issued_date,
                                           )

    header_content_ori = [
        [[logo, Paragraph(lab_address, style=style_sheet['ThaiStyle'])],
         [Paragraph(invoice_info_ori, style=style_sheet['ThaiStyle'])]]
    ]

    header_styles = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ])

    header_ori = Table(header_content_ori, colWidths=[400, 100])

    header_ori.hAlign = 'CENTER'
    header_ori.setStyle(header_styles)

    customer_name = '''<para><font size=11>
                ลูกค้า/Customer {customer}<br/>
                ที่อยู่/Address {address}<br/>
                เลขประจำตัวผู้เสียภาษี/Taxpayer identification no {taxpayer_identification_no}
                </font></para>
                '''.format(customer=request.customer,
                           address=", ".join(address.address for address in request.customer.addresses
                                             if address.address_type == 'quotation'),
                           taxpayer_identification_no=request.customer.taxpayer_identification_no)

    customer = Table([[Paragraph(customer_name, style=style_sheet['ThaiStyle']),
                       ]],
                     colWidths=[540, 280]
                     )
    customer.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                  ('VALIGN', (0, 0), (-1, -1), 'TOP')]))

    items = [[Paragraph('<font size=10>ลำดับ / No.</font>', style=style_sheet['ThaiStyleCenter']),
              Paragraph('<font size=10>รายการ / Description</font>', style=style_sheet['ThaiStyleCenter']),
              Paragraph('<font size=10>จำนวน / Quality</font>', style=style_sheet['ThaiStyleCenter']),
              Paragraph('<font size=10>ราคาหน่วย(บาท)/ Unit Price</font>', style=style_sheet['ThaiStyleCenter']),
              Paragraph('<font size=10>ราคารวม(บาท) / Total</font>', style=style_sheet['ThaiStyleCenter']),
              ]]

    n = len(items)
    for i in range(18 - n):
        items.append([
            Paragraph('<font size=12>&nbsp; </font>', style=style_sheet['ThaiStyleNumber']),
            Paragraph('<font size=12> </font>', style=style_sheet['ThaiStyle']),
            Paragraph('<font size=12> </font>', style=style_sheet['ThaiStyleNumber']),
            Paragraph('<font size=12> </font>', style=style_sheet['ThaiStyleNumber']),
            Paragraph('<font size=12> </font>', style=style_sheet['ThaiStyleNumber']),
        ])
    items.append([
        Paragraph('<font size=12></font>', style=style_sheet['ThaiStyleNumber']),
        Paragraph('<font size=12>รวมทั้งสิ้น</font>', style=style_sheet['ThaiStyleCenter']),
        Paragraph('<font size=12></font>', style=style_sheet['ThaiStyleNumber'])
    ])
    item_table = Table(items, colWidths=[50, 250, 75])
    item_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, 0), 0.25, colors.black),
        ('BOX', (0, -1), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (0, -1), 0.25, colors.black),
        ('BOX', (1, 0), (1, -1), 0.25, colors.black),
        ('BOX', (2, 0), (2, -1), 0.25, colors.black),
        ('BOX', (3, 0), (3, -1), 0.25, colors.black),
        ('BOX', (4, 0), (4, -1), 0.25, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, -2), (-1, -2), 10),
    ]))
    item_table.setStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
    item_table.setStyle([('SPAN', (0, -1), (1, -1))])

    text_info = Paragraph('<br/><font size=12>ขอแสดงความนับถือ<br/></font>',style=style_sheet['ThaiStyle'])
    text = [[text_info, Paragraph('<font size=12></font>', style=style_sheet['ThaiStyle'])]]
    text_table = Table(text, colWidths=[0, 155, 155])
    text_table.hAlign = 'RIGHT'
    sign_info = Paragraph('<font size=12>(&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                          '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                          '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                          '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</font>', style=style_sheet['ThaiStyle'])
    sign = [[sign_info, Paragraph('<font size=12></font>', style=style_sheet['ThaiStyle'])]]
    sign_table = Table(sign, colWidths=[0, 200, 200])
    sign_table.hAlign = 'RIGHT'

    data.append(KeepTogether(Paragraph('<para align=center><font size=16>ใบแจ้งหนี้<br/><br/></font></para>',
                                       style=style_sheet['ThaiStyle'])))
    data.append(KeepTogether(Paragraph('<para align=center><font size=16>Invoice<br/><br/><br/></font></para>',
                                       style=style_sheet['ThaiStyle'])))
    data.append(KeepTogether(header_ori))
    data.append(KeepTogether(Spacer(1, 12)))
    data.append(KeepTogether(customer))
    data.append(KeepTogether(Spacer(1, 16)))
    data.append(KeepTogether(item_table))
    data.append(KeepTogether(Spacer(1, 16)))
    data.append(KeepTogether(text_table))
    data.append(KeepTogether(Spacer(1, 25)))
    data.append(KeepTogether(sign_table))

    doc.build(data, onLaterPages=all_page_setup, onFirstPage=all_page_setup)
    buffer.seek(0)
    return buffer


@academic_services.route('/invoice/pdf/<int:request_id>', methods=['GET'])
def export_invoice_pdf(request_id):
    requests = ServiceRequest.query.get(request_id)
    buffer = generate_invoice_pdf(requests)
    return send_file(buffer, download_name='Invoice.pdf', as_attachment=True)


@academic_services.route('/customer/request/delete', methods=['GET', 'DELETE'])
def delete_request(request_id):
    if request_id:
        request = ServiceRequest.query.get(request_id)
        db.session.delete(request)
        db.session.commit()
        flash('ยกเลิกคำขอรับบริการสำเร็จ', 'success')
        return redirect(url_for('academic_services.request_index', customer_account_id=current_user.id))


@academic_services.route('/customer/request/issue/<int:request_id>', methods=['GET', 'POST'])
def issue_quotation(request_id):
    if request_id:
        request = ServiceRequest.query.get(request_id)
        request.status = 'ออกใบเสนอราคา'
        request.issue_quotation = True
        db.session.add(request)
        db.session.commit()
        flash('ออกใบเสนอราคาสำเร็จ', 'success')
        return redirect(url_for('academic_services.quotation_index'))


@academic_services.route('/edit/academic-service-form', methods=['GET'])
def edit_request_form():
    request_id = request.args.get('request_id')
    service_request = ServiceRequest.query.get(request_id)
    lab = ServiceLab.query.filter_by(code=service_request.lab).first()
    sub_lab = ServiceSubLab.query.filter_by(code=service_request.lab).first()
    sheetid = '1EHp31acE3N1NP5gjKgY-9uBajL1FkQe7CCrAu-TKep4'
    print('Authorizing with Google..')
    gc = get_credential(json_keyfile)
    wks = gc.open_by_key(sheetid)
    if sub_lab:
        sheet = wks.worksheet(sub_lab.sheet)
    else:
        sheet = wks.worksheet(lab.sheet)
    df = pandas.DataFrame(sheet.get_all_records())
    data = service_request.data
    form = create_request_form(df)(**data)
    template = ''
    for f in form:
        template += str(f)
    return template


@academic_services.route('/academic-service-request/<int:request_id>', methods=['GET'])
@login_required
def edit_service_request(request_id):
    return render_template('academic_services/edit_request.html', request_id=request_id)


def walk_form_fields(field, quote_column_names, values=[]):
    if isinstance(field, Iterable):
        for f in field:
            if isinstance(f, Iterable):
                values.append(walk_form_fields(f, quote_column_names, values))
                return ''
            else:
                print(f.name)
                field_name = f.name.split('-')[-1]
                if field_name in quote_column_names:
                    print('value: ', f.data)
                    values.append(f.data)
                    return ''
    else:
        field_name = field.name.split('-')[-1]
        if field_name in quote_column_names:
            values.append(field.data)
            print('value: ', field.data)
    return ''


@academic_services.route('/cus/quotation/<int:request_id>', methods=['GET'])
def quotation(request_id):
    service_request = ServiceRequest.query.get(request_id)
    sheet_price_id = '1hX0WT27oRlGnQm997EV1yasxlRoBSnhw3xit1OljQ5g'
    gc = get_credential(json_keyfile)
    wksp = gc.open_by_key(sheet_price_id)
    sheet_price =wksp.worksheet('Sheet1')
    df_price = pandas.DataFrame(sheet_price.get_all_records())
    quotes = {}
    for _, row in df_price.iterrows():
        key = ''.join(sorted(row[1:].str.cat()))
        quotes[key] = row['price']
    # print('d', quotes)
    sheet_request_id = '1EHp31acE3N1NP5gjKgY-9uBajL1FkQe7CCrAu-TKep4'
    wksr = gc.open_by_key(sheet_request_id)
    lab = ServiceLab.query.filter_by(code=service_request.lab).first()
    sub_lab = ServiceSubLab.query.filter_by(code=service_request.lab).first()
    if sub_lab:
        sheet_request = wksr.worksheet(sub_lab.sheet)
    else:
        sheet_request = wksr.worksheet(lab.sheet)
    df_request = pandas.DataFrame(sheet_request.get_all_records())
    data = service_request.data
    form = create_request_form(df_request)(**data)
    for field in form:
        if isinstance(field, FormField):
            the_values = []
            walk_form_fields(field, df_price.columns, the_values)
            print(''.join(sorted(''.join(the_values))))

    #     if field.type == 'FieldList':
    #         for form_field in field:
    #             print(form_field.name)
    #             for f in form_field:
    #                 print('\t', f.name)
    #                 key = ''.join(f.label.text)
    #                 if f.data != None and f.data != '' and f.data != [] and f.label not in set_fields:
    #                     set_fields.add(f.label)
    #                     if f.type == 'CheckboxField':
    #                         values[key] = ', '.join(f.data)
    #                     else:
    #                         values[key] = f.data
    #     else:
    #         print(field.name)
    #         key = ''.join(field.label.text)
    #         if field.type == 'FormField':
    #             for f in field:
    #                 print('\t', f.name)
    #             if field.data != None and field.data != '' and field.data != [] and field.label not in set_fields:
    #                 set_fields.add(field.label)
    #             if field.type == 'CheckboxField':
    #                 values[key] = ', '.join(field.data)
    #             else:
    #                 values[key] = field.data
    # # print('f', values)
    return render_template( 'academic_services/quotation.html', result_dict=None)
