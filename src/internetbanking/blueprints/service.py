from db import session
from sqlalchemy import text

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker


if __name__ == "__main__":
    query = 'UPDATE tb_account SET is_active = False WHERE nomor_rekening NOT IN (SELECT tb_account.nomor_rekening FROM tb_account LEFT JOIN tb_user AS u ON u.id_user = tb_account.id_user LEFT JOIN tb_transaction AS ts ON tb_account.nomor_rekening = ts.nomor_rekening WHERE u."is_admin" IS FALSE AND (ts.created_at >= NOW() - INTERVAL \'3 months\') GROUP BY tb_account.nomor_rekening);'

    
    #scritp untuk melakukan pengecekkan dormant
    engine = create_engine("postgresql://postgres:admin123@localhost:5433/internetbanking")
    session.configure(bind=engine)
    
    accounts = session.execute(text(query))
    session.commit()
