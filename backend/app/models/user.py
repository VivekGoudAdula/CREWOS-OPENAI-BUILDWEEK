from app.schemas.common import utcnow
def user_document(*, email: str, full_name: str, password_hash: str) -> dict:
    now=utcnow(); return {'email':email.lower(),'full_name':full_name,'password_hash':password_hash,'is_active':True,'created_at':now,'updated_at':now}
