from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

app = Flask(__name__)

VERSION = "1.0.0"  # Definiere die Version des Programms

# Funktion zur Erstellung einer neuen Datenbankverbindung
def create_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),          # Datenbank-Host
        user=os.getenv('DB_USER', 'radius_dba'),         # Datenbank-Benutzer
        password=os.getenv('DB_PASSWORD', 'Radius4711#'),# Datenbank-Passwort
        database=os.getenv('DB_NAME', 'radius_db'),      # Name der Datenbank
        charset='utf8mb4',
        collation='utf8mb4_general_ci' # Kompatible Kollation
    )

def get_access_reject_entries(order_by="id", order_dir="DESC"):
    try:
        connection = create_connection()
        query = (
            f"SELECT id, username, reply, authdate, packet_src_ip_address FROM radpostauth "
            f"WHERE reply = 'Access-Reject' "
            f"ORDER BY {order_by} {order_dir} "
            f"LIMIT 100"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Fehler beim Abrufen der Einträge: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_summary_counts():
    try:
        connection = create_connection()
        query_reject = "SELECT COUNT(*) AS count FROM radpostauth WHERE reply = 'Access-Reject'"
        query_accept = "SELECT COUNT(*) AS count FROM radpostauth WHERE reply = 'Access-Accept'"
        query_users = "SELECT COUNT(*) AS count FROM radcheck"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query_reject)
        reject_count = cursor.fetchone()['count']
        cursor.execute(query_accept)
        accept_count = cursor.fetchone()['count']
        cursor.execute(query_users)
        user_count = cursor.fetchone()['count']
        return reject_count, accept_count, user_count
    except Error as e:
        print(f"Fehler beim Abrufen der Summen: {e}")
        return 0, 0, 0
    finally:
        if connection.is_connected():
            connection.close()

def delete_old_entries():
    try:
        connection = create_connection()
        delete_query = (
            "DELETE FROM radpostauth WHERE id NOT IN ("
            "SELECT id FROM ("
            "SELECT id FROM radpostauth WHERE reply = 'Access-Reject' ORDER BY id DESC LIMIT 100"
            ") AS temp_table)"
        )
        cursor = connection.cursor()
        cursor.execute(delete_query)
        connection.commit()
    except Error as e:
        print(f"Fehler beim Löschen von Einträgen: {e}")
    finally:
        if connection.is_connected():
            connection.close()

@app.route('/')
def index():
    order_by = request.args.get("order_by", "id")
    order_dir = request.args.get("order_dir", "DESC")
    entries = get_access_reject_entries(order_by, order_dir)
    reject_count, accept_count, user_count = get_summary_counts()
    last_update = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
    return render_template('index.html', entries=entries, reject_count=reject_count, accept_count=accept_count, user_count=user_count, last_update=last_update, version=VERSION, order_by=order_by, order_dir=order_dir)

@app.route('/edit-users', methods=['GET', 'POST'])
def edit_users():
    if request.method == 'POST':
        try:
            connection = create_connection()
            cursor = connection.cursor()
            if 'add_user' in request.form:
                username = request.form['username']
                attribute = request.form['attribute']
                op = request.form['op']
                value = request.form['value']
                cursor.execute("INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, %s, %s, %s)", (username, attribute, op, value))
                connection.commit()
            elif 'delete_user' in request.form:
                user_id = request.form['user_id']
                cursor.execute("DELETE FROM radcheck WHERE id = %s", (user_id,))
                connection.commit()
        except Error as e:
            print(f"Fehler beim Bearbeiten von radcheck: {e}")
        finally:
            if connection.is_connected():
                connection.close()
        return redirect(url_for('edit_users'))

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM radcheck")
        users = cursor.fetchall()
    except Error as e:
        print(f"Fehler beim Abrufen von radcheck: {e}")
        users = []
    finally:
        if connection.is_connected():
            connection.close()

    return render_template('edit_users.html', users=users, version=VERSION)

@app.route('/edit-nas', methods=['GET', 'POST'])
def edit_nas():
    if request.method == 'POST':
        try:
            connection = create_connection()
            cursor = connection.cursor()
            if 'add_nas' in request.form:
                nasname = request.form['nasname']
                shortname = request.form['shortname']
                type_ = request.form['type']
                ports = request.form['ports']
                secret = request.form['secret']
                cursor.execute("INSERT INTO nas (nasname, shortname, type, ports, secret) VALUES (%s, %s, %s, %s, %s)", (nasname, shortname, type_, ports, secret))
                connection.commit()
            elif 'delete_nas' in request.form:
                nas_id = request.form['nas_id']
                cursor.execute("DELETE FROM nas WHERE id = %s", (nas_id,))
                connection.commit()
        except Error as e:
            print(f"Fehler beim Bearbeiten von nas: {e}")
        finally:
            if connection.is_connected():
                connection.close()
        return redirect(url_for('edit_nas'))

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM nas")
        nas_entries = cursor.fetchall()
    except Error as e:
        print(f"Fehler beim Abrufen von nas: {e}")
        nas_entries = []
    finally:
        if connection.is_connected():
            connection.close()

    return render_template('edit_nas.html', nas_entries=nas_entries, version=VERSION)

@app.route('/refresh', methods=['POST'])
def refresh():
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
    delete_old_entries()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
