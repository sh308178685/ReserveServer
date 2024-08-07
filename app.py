from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import Config
from models import db, User, Venue, Booking
import datetime
from util import Util
import requests

app = Flask(__name__)
app.config.from_object(Config)
# 设置 Secret Key
app.secret_key = Config.SERVER_SECRET
mysql = MySQL(app)
db.init_app(app)

with app.app_context():
    db.create_all()

admin = Admin(app, name='管理后台', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Venue, db.session))
admin.add_view(ModelView(Booking, db.session))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    js_code = request.json.get('js_code')
    username = request.json.get('username')
    email = request.json.get('email')
    phone_number = request.json.get('phone_number')

    if not js_code or not username or not email or not phone_number:
        return jsonify({'status': 'error', 'message': '缺少必要的参数'}), 400

    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={Config.APP_ID}&secret={Config.APP_SECRET}&js_code={js_code}&grant_type=authorization_code'
    response = requests.get(url)

    if response.status_code == 200:
        session_data = response.json()
        openid = session_data.get('openid')
        if openid:
            conn = mysql.connection
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE openid = %s", (openid,))
            user = cursor.fetchone()
            
            if user:
                #创建token
                user_id = user['id']
                token = Util.create_token(user_id,Config.SERVER_SECRET,3600*24)
                cursor.close()
                return jsonify({
                    'status': 'success',
                    'openid': openid,
                    'username': user['username'],
                    'email': user['email'],
                    'user_id': user_id,
                    'token': token,
                    'message': '登录成功'
                })
            else:
                try:
                    # 插入新用户
                    cursor.execute(
                        "INSERT INTO users (username, email, phone_number, openid) VALUES (%s, %s, %s, %s)",
                        (username, email, phone_number, openid)
                    )
                    conn.commit()
                    
                    # 获取新插入用户的 ID
                    user_id = cursor.lastrowid
                    token = Util.create_token(user_id,Config.SERVER_SECRET,3600*24)
                    cursor.close()
                    return jsonify({
                        'status': 'success',
                        'openid': openid,
                        'username': username,
                        'email': email,
                        'user_id': user_id,
                        'token': token,
                        'message': '注册并登录成功'
                    })
                except Exception as e:
                    conn.rollback()
                    cursor.close()
                    return jsonify({
                        'status': 'error',
                        'message': '注册失败: ' + str(e)
                    }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': '网络请求失败'
            }), response.status_code

@app.route('/allbookings', methods=['GET'])
def get_allbookings():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT b.id, b.booking_date, b.details, u.username, v.name as venue_name FROM bookings b JOIN users u ON b.user_id = u.id JOIN venues v ON b.venue_id = v.id')
    bookings = cursor.fetchall()
    cursor.close()

    events = []
    for booking in bookings:
        events.append({
            'title': f"{booking['username']} - {booking['venue_name']} ({booking['details']})",
            'start': booking['booking_date'].isoformat(),
            'description': booking['details']
        })

    return jsonify(events)

@app.route('/venues', methods=['GET'])
def get_venues():
    venues = Venue.query.all()
    return jsonify([{'id': v.id, 'name': v.name, 'location': v.location} for v in venues])






@app.route('/takebooking', methods=['POST'])
def create_booking():
    data = request.get_json()
    user_id = Util.get_current_user_id(request)  # 获取当前登录用户的ID
    print(user_id)
    if user_id is not None:
        venue_id = data.get('venue_id')
        booking_date = datetime.datetime.strptime(data.get('booking_date'), '%Y-%m-%d').date()
        start_time = datetime.datetime.strptime(data.get('start_time'), '%H:%M').time()
        end_time = datetime.datetime.strptime(data.get('end_time'), '%H:%M').time()
        details = data.get('details')  # 新增细节信息
        # 检查该时间段是否已被预订
        existing_booking = Booking.query.filter(
            Booking.user_id == user_id,
            Booking.venue_id == venue_id,
            Booking.booking_date == booking_date,
            Booking.start_time <= end_time,
            Booking.end_time >= start_time
        ).first()
        if existing_booking:
            return jsonify({'message': 'This time slot is already booked.'}), 400

        new_booking = Booking(
            user_id=user_id,
            venue_id=venue_id,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            details=details  # 添加细节信息
        )

        db.session.add(new_booking)
        db.session.commit()

        return jsonify({'message': 'Booking created successfully.'}), 201
    else:
        return jsonify({'message': 'TOKEN过期请重新登录.'}), 202
    


@app.route('/bookings', methods=['GET'])
def get_bookings():
    user_id = Util.get_current_user_id(request)  # 获取当前登录用户的ID
    bookings = Booking.query.filter_by(user_id=user_id).all()
    
    result = []
    for booking in bookings:
        venue = Venue.query.get(booking.venue_id)
        result.append({
            'id': booking.id,
            'venue_name': venue.name,
            'venue_location': venue.location,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d'),
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M'),
            'details': booking.details  # 返回细节信息
        })
    
    return jsonify(result), 200



@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != Util.get_current_user_id(request):  # 验证用户权限
        return jsonify({'message': 'You do not have permission to cancel this booking.'}), 403
    
    db.session.delete(booking)
    db.session.commit()
    
    return jsonify({'message': 'Booking cancelled successfully.'}), 200







if __name__ == '__main__':
    app.run( host='0.0.0.0', debug=True)
