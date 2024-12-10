from flask import Flask, render_template, request, redirect, url_for, flash
from flask_apscheduler import APScheduler
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'secret_key'  # Ganti dengan key rahasia Anda
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Simpan harapan di memori
future_hopes = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hope', methods=['GET', 'POST'])
def hope():
    if request.method == 'POST':
        email = request.form['email']
        hope_message = request.form['hope']
        send_date = request.form['send_date']

        # Validasi data
        if not email or not hope_message or not send_date:
            flash('Semua kolom harus diisi.', 'error')
            return redirect(url_for('hope'))

        try:
            send_datetime = datetime.strptime(send_date, '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Format tanggal tidak valid. Gunakan format YYYY-MM-DD HH:MM.', 'error')
            return redirect(url_for('hope'))

        if send_datetime <= datetime.now():
            flash('Tanggal pengiriman harus di masa depan.', 'error')
            return redirect(url_for('hope'))

        # Simpan harapan dan jadwalkan pengiriman
        job_id = f"{email}_{send_datetime.timestamp()}"
        future_hopes[job_id] = {'email': email, 'message': hope_message}
        scheduler.add_job(id=job_id, func=send_email, trigger='date', run_date=send_datetime, args=[email, hope_message])
        
        flash('Harapan Anda berhasil disimpan dan akan dikirimkan sesuai jadwal!', 'success')
        return redirect(url_for('hope'))

    return render_template('hope.html')

def send_email(email, message):
    """Mengirim email harapan masa depan."""
    smtp_server = "smtp.gmail.com"  # Ganti dengan server SMTP Anda
    smtp_port = 587
    sender_email = "youremail@gmail.com"  # Ganti dengan email Anda
    sender_password = "yourpassword"  # Ganti dengan password Anda

    try:
        msg = MIMEText(message)
        msg['Subject'] = 'Harapan Masa Depan Anda'
        msg['From'] = sender_email
        msg['To'] = email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        print(f"Email terkirim ke {email}")
    except Exception as e:
        print(f"Gagal mengirim email ke {email}: {e}")

if __name__ == '__main__':
    app.run(debug=True)
