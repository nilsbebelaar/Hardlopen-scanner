from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db
from app.models import Deelnemers, Tijden
from datetime import datetime
from sqlalchemy import asc, desc

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')


@main_bp.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')


@main_bp.route('/deelnemer/add', methods=['GET', 'POST'])
def deelnemer_add():
    if request.method == 'GET':
        return render_template('deelnemer_edit.html', deelnemer=None)

    if request.method == 'POST':
        barcode = request.form.get('barcode')
        if Deelnemers.query.filter_by(barcode=barcode).all():
            flash(f"Barcode '{barcode}' is al in gebruik", 'danger')
            return redirect(url_for('main.deelnemer_add'))

        deelnemer = Deelnemers()
        deelnemer.naam = request.form.get('naam')
        deelnemer.geslacht = request.form.get('geslacht')
        deelnemer.barcode = request.form.get('barcode')

        db.session.add(deelnemer)
        db.session.commit()
        flash(f"Deelnemer '{deelnemer.naam}' is toegevoegd", 'info')
        return redirect(url_for('main.deelnemers'))


@main_bp.route('/deelnemer/edit/<id>', methods=['GET', 'POST'])
def deelnemer_edit(id):
    if request.method == 'GET':
        deelnemer = Deelnemers.query.get(id)
        if not deelnemer:
            flash(f"ID '{id}' bestaat niet", 'danger')
            return redirect(url_for('main.deelnemers'))

        return render_template('deelnemer_edit.html', deelnemer=deelnemer)

    if request.method == 'POST':
        deelnemer = Deelnemers.query.get(id)

        if not deelnemer:
            flash(f"ID '{id}' bestaat niet", 'info')
            return redirect(url_for('main.deelnemers'))

        deelnemer.naam = request.form.get('naam')
        deelnemer.geslacht = request.form.get('geslacht')
        deelnemer.barcode = request.form.get('barcode')

        db.session.commit()
        flash(f"Deelnemer '{deelnemer.naam}' is bewerkt", 'info')
        return redirect(url_for('main.deelnemers'))


@main_bp.route('/deelnemer/delete/<id>', methods=['DELETE'])
def deelnemer_delete(id):
    deelnemer = Deelnemers.query.get(id)

    if not deelnemer:
        flash(f"ID '{id}' bestaat niet", 'info')
        return redirect(url_for('main.deelnemers'))

    flash(f"Deelnemer '{deelnemer.naam}' is verwijderd", 'info')
    return redirect(url_for('main.deelnemers'))


@main_bp.route('/deelnemers', methods=['GET'])
def deelnemers():
    deelnemers = Deelnemers.query.all()
    return render_template('deelnemers.html', deelnemers=deelnemers)


@main_bp.route('/tijd/scan', methods=['GET', 'POST'])
def tijd_scan():
    if request.method == 'GET':
        return render_template('tijd_scan.html')

    if request.method == 'POST':
        db_row = Tijden()
        db_row.tijd = datetime.utcnow()
        db_row.barcode = request.form.get('barcode')

        db.session.add(db_row)
        db.session.commit()

        start_tijd = Tijden.query.filter_by(barcode=9999).order_by(desc(Tijden.tijd)).first()
        gelopen_tijd = db_row.tijd - start_tijd.tijd
        flash(f"{str(gelopen_tijd).split('.')[0]} geregistreerd voor '{db_row.deelnemer.naam}' is bewerkt", 'info')
        return redirect(url_for('main.tijd_scan'))


@main_bp.route('/timer/start', methods=['GET'])
def timer_start():
    db_row = Tijden()
    db_row.tijd = datetime.utcnow()
    db_row.barcode = 9999

    db.session.add(db_row)
    db.session.commit()

    flash(f"Timer gestart om {db_row.tijd.strftime('%H:%M')}", 'info')
    return redirect(url_for('main.tijd_scan'))


@main_bp.route('/uitslag/list', methods=['GET'])
def uitslag_list():
    start_tijd = Tijden.query.filter_by(barcode=9999).order_by(desc(Tijden.tijd)).first().tijd
    
    deelnemers =  [{'barcode':r.barcode} for r in db.session.query(Tijden.barcode).distinct() if r.barcode != 9999]
    meeste_rondes = 0
    for deelnemer in deelnemers:
        deelnemer['rondes'] = Tijden.query.filter_by(barcode = deelnemer['barcode']).count()
        if deelnemer['rondes'] > meeste_rondes:
            meeste_rondes = deelnemer['rondes']
    
    deelnemers_gesorteerd = []
    for i in range(meeste_rondes, 0, -1):
        deelnemers_met_x_rondes = [{'barcode':d['barcode']} for d in deelnemers if d['rondes'] == i]
        deelnemers_met_x_rondes_gesorteerd = []
        for deelnemer in deelnemers_met_x_rondes:
            deelnemer_db = Tijden.query.filter_by(barcode=deelnemer['barcode']).order_by(desc(Tijden.tijd)).first()
            deelnemer['tijd'] = deelnemer_db.tijd - start_tijd
            deelnemer['tijd_str'] = str(deelnemer_db.tijd - start_tijd).split('.')[0]
            deelnemer['naam'] = deelnemer_db.deelnemer.naam
            deelnemer['geslacht'] = deelnemer_db.deelnemer.geslacht
            deelnemer['rondes'] = i
        
            deelnemers_met_x_rondes_gesorteerd.append(deelnemer)
        
        deelnemers_met_x_rondes_gesorteerd = sorted(deelnemers_met_x_rondes_gesorteerd, key=lambda d: d['tijd'])
        
        for deelnemer in deelnemers_met_x_rondes_gesorteerd:
            deelnemers_gesorteerd.append(deelnemer)
    print(deelnemers_gesorteerd)

    return render_template('uitslagen_list.html', deelnemers=deelnemers_gesorteerd)