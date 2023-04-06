from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, Markup
from app import db
from app.models import Deelnemers, Tijden
from datetime import datetime, timedelta
import time
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
        return jsonify({'success': False})

    deelnemer = Deelnemers.query.get(id)
    db.session.delete(deelnemer)
    db.session.commit()

    flash(f"Deelnemer '{deelnemer.naam}' is verwijderd", 'danger')
    return jsonify({'success': True})


@main_bp.route('/deelnemers', methods=['GET'])
def deelnemers():
    deelnemers = Deelnemers.query.all()
    return render_template('deelnemers.html', deelnemers=deelnemers)


@main_bp.route('/tijd/scan', methods=['GET', 'POST'])
def tijd_scan():
    if request.method == 'GET':
        return render_template('tijd_scan.html')

    if request.method == 'POST':
        barcode = request.form.get('barcode')

        if not Deelnemers.query.filter_by(barcode=barcode).first():
            #Nieuwe lege gebruiker maken
            new = Deelnemers()
            new.naam = '-'
            new.barcode = barcode
            # new.geslacht = 'U'

            db.session.add(new)
            db.session.commit()
            flash(f'Er is een nieuwe gebruiker met barcode {barcode} toegevoegd', 'warning')
            # return redirect(url_for('main.tijd_scan'))

        db_row = Tijden()
        db_row.tijd = time.time()
        db_row.barcode = barcode

        db.session.add(db_row)
        db.session.commit()

        start_tijd = Tijden.query.filter_by(barcode=9999).order_by(desc(Tijden.tijd)).first().tijd
        flash(f"{time.strftime('%H:%M:%S', time.gmtime(db_row.tijd - start_tijd))} geregistreerd voor '{db_row.deelnemer.naam}' is bewerkt", 'info')
        return redirect(url_for('main.tijd_scan'))


@main_bp.route('/timer/start', methods=['PUT'])
def timer_start():
    rows = Tijden.query.all()
    for row in rows:
        db.session.delete(row)
    # db.session.commit()

    db_row = Tijden()
    db_row.tijd = time.time()
    db_row.barcode = 9999

    db.session.add(db_row)
    db.session.commit()

    flash(Markup(f'Timer gestart om <timestamp time="{db_row.tijd}"></timestamp>'), 'info')
    return jsonify({'success': True})


@main_bp.route('/uitslag/list', methods=['GET'])
def uitslag_list():
    start_tijd = Tijden.query.filter_by(barcode=9999).order_by(desc(Tijden.tijd)).first().tijd

    deelnemers = [{'barcode': r.barcode} for r in db.session.query(Tijden.barcode).distinct() if r.barcode != 9999]
    meeste_rondes = 0
    for deelnemer in deelnemers:
        deelnemer['rondes'] = Tijden.query.filter_by(barcode=deelnemer['barcode']).count()
        if deelnemer['rondes'] > meeste_rondes:
            meeste_rondes = deelnemer['rondes']

    deelnemers_gesorteerd = []
    for i in range(meeste_rondes, 0, -1):
        deelnemers_met_x_rondes = [{'barcode': d['barcode']} for d in deelnemers if d['rondes'] == i]
        deelnemers_met_x_rondes_gesorteerd = []
        for deelnemer in deelnemers_met_x_rondes:
            deelnemer_db = Tijden.query.filter_by(barcode=deelnemer['barcode']).order_by(desc(Tijden.tijd)).first()
            if deelnemer_db.barcode:
                deelnemer['tijd'] = deelnemer_db.tijd - start_tijd
                deelnemer['tijd_str'] = time.strftime('%H:%M:%S', time.gmtime(deelnemer_db.tijd - start_tijd))
                deelnemer['naam'] = deelnemer_db.deelnemer.naam
                deelnemer['geslacht'] = deelnemer_db.deelnemer.geslacht
                deelnemer['rondes'] = i

                deelnemers_met_x_rondes_gesorteerd.append(deelnemer)

        deelnemers_met_x_rondes_gesorteerd = sorted(deelnemers_met_x_rondes_gesorteerd, key=lambda d: d['tijd'])

        for deelnemer in deelnemers_met_x_rondes_gesorteerd:
            deelnemers_gesorteerd.append(deelnemer)
    # print(deelnemers_gesorteerd)

    return render_template('uitslagen_list.html', deelnemers=deelnemers_gesorteerd)


@main_bp.route('/start_tijd', methods=['GET'])
def start_tijd():
    tijd = Tijden.query.filter_by(barcode=9999).one().tijd
    return jsonify(success=True, tijd=tijd)
