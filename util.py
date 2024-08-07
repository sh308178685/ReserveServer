
import jwt
import datetime
from config import Config

class Util:
    @staticmethod
    def create_token(user_id, secret_key, expiration_seconds=3600):
        now = datetime.datetime.utcnow()
        exp = now + datetime.timedelta(seconds=expiration_seconds)
        
        payload = {
            'user_id': user_id,
            'exp': exp.timestamp(),
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
    @staticmethod
    def validate_token(token, secret_key):
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        

        # 解析 JWT 令牌
    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(token, Config.SERVER_SECRET , algorithms=['HS256'])
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return None  # 令牌过期
        except jwt.InvalidTokenError:
            return None  # 无效令牌

    # 获取当前登录用户的 ID
    @staticmethod
    def get_current_user_id(request):
        print("get_current_user_id")
        token = request.headers.get('Authorization')
        if token:
            token = token.replace('Bearer ', '')
            
            user_id = Util.decode_token(token)
            if user_id:
                return user_id
        return None

